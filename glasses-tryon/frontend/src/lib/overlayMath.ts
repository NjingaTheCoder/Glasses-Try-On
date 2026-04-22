import type { FaceLandmark } from '@/types/tryon'
import type { Product } from '@/types/product'
import { type Point, type AffineCoeffs, midpoint, lerp, solveAffine } from './geometry'

// ─── Tuning constants ─────────────────────────────────────────────────────────
// Export them so Phase-2 / debug tooling can read the live values.

export const FIT = {
  /**
   * Fraction of canvas height to push the bridge target BELOW the inner-eye
   * midpoint so frames sit on the nose bridge rather than on the eye line.
   */
  BRIDGE_DROP: 0.012,

  /**
   * How far beyond each outer eye-corner to place the temple target,
   * expressed as a fraction of the full outer-corner-to-outer-corner span.
   * 0.25 ≈ 25 % of the eye distance past the corner → near the temples.
   */
  TEMPLE_REACH: 0.25,
} as const

// ─── Types ────────────────────────────────────────────────────────────────────

/** Three anchor points on the glasses PNG, in image-pixel coordinates. */
export interface GlassesAnchors {
  bridge: Point
  leftTemple: Point
  rightTemple: Point
}

/** Three target points on the canvas (face photo), in canvas-pixel coordinates. */
export interface FaceTargets {
  bridge: Point
  leftTemple: Point
  rightTemple: Point
}

// ─── Source anchor computation ────────────────────────────────────────────────

/**
 * Convert the product's normalized anchor points into image-pixel coordinates.
 *
 * "Left" and "right" are from the viewer's perspective (same as the image
 * coordinate system): left_temple_x is near 0, right_temple_x near 1.
 */
export function computeGlassesSources(
  product: Product,
  imgW: number,
  imgH: number,
): GlassesAnchors {
  return {
    bridge:      { x: product.bridge_x      * imgW, y: product.bridge_y      * imgH },
    leftTemple:  { x: product.left_temple_x  * imgW, y: product.left_temple_y  * imgH },
    rightTemple: { x: product.right_temple_x * imgW, y: product.right_temple_y * imgH },
  }
}

// ─── Destination target computation ──────────────────────────────────────────

/**
 * Derive the three face-target points from MediaPipe landmarks.
 *
 * Landmarks used (indices into the 478-point FaceMesh with refineLandmarks):
 *   33  — right outer eye corner  \  eye-distance reference
 *   263 — left  outer eye corner  /
 *   133 — right inner eye corner  \  bridge anchor (midpoint = nose-bridge)
 *   362 — left  inner eye corner  /
 *
 * Temple targets are extrapolated outward from the outer eye corners so the
 * frame temples reach the sides of the face.  No specific side-face landmark
 * index is required, keeping this robust to any landmark-set variation.
 *
 * Left/right: from the viewer's perspective (lm33 is on the LEFT side of the
 * image because the person's right eye appears on the camera's left).
 */
export function computeFaceTargets(
  landmarks: FaceLandmark[],
  cw: number,
  ch: number,
): FaceTargets {
  const px = (lm: FaceLandmark): Point => ({ x: lm.x * cw, y: lm.y * ch })

  const lm33  = px(landmarks[33])   // left  side of image (outer right eye)
  const lm263 = px(landmarks[263])  // right side of image (outer left eye)
  const lm133 = px(landmarks[133])  // inner right eye corner
  const lm362 = px(landmarks[362])  // inner left  eye corner

  // Bridge: midpoint of inner corners, nudged downward onto the nose bridge
  const innerMid = midpoint(lm133, lm362)
  const bridge: Point = {
    x: innerMid.x,
    y: innerMid.y + FIT.BRIDGE_DROP * ch,
  }

  // Temple targets: extend beyond each outer eye corner away from the eye centre
  const eyeCenter = midpoint(lm33, lm263)
  // lerp(from, to, t) with t > 1 goes beyond `to`
  const leftTemple  = lerp(eyeCenter, lm33,  1 + FIT.TEMPLE_REACH)
  const rightTemple = lerp(eyeCenter, lm263, 1 + FIT.TEMPLE_REACH)

  return { bridge, leftTemple, rightTemple }
}

// ─── Background removal ───────────────────────────────────────────────────────

/**
 * Strip the background from a glasses image by sampling its four corners to
 * detect the background colour and then zeroing pixels within `tolerance`
 * (Euclidean RGB distance).  A soft feather zone at 1–1.5× tolerance prevents
 * hard aliased edges.
 *
 * Requires the image to have been loaded with crossOrigin='anonymous'.
 * Throws SecurityError if the canvas is tainted — caller must catch.
 */
function removeBackground(img: HTMLImageElement, tolerance = 40): ImageData {
  const w = img.naturalWidth
  const h = img.naturalHeight

  const canvas = document.createElement('canvas')
  canvas.width = w
  canvas.height = h
  const ctx = canvas.getContext('2d')!
  ctx.drawImage(img, 0, 0)
  const imageData = ctx.getImageData(0, 0, w, h)
  const d = imageData.data

  // Sample one pixel in from each corner to detect the background colour
  const sample = (x: number, y: number): [number, number, number] => {
    const i = (y * w + x) * 4
    return [d[i], d[i + 1], d[i + 2]]
  }
  const corners = [sample(1, 1), sample(w - 2, 1), sample(1, h - 2), sample(w - 2, h - 2)]
  const bgR = Math.round(corners.reduce((s, c) => s + c[0], 0) / 4)
  const bgG = Math.round(corners.reduce((s, c) => s + c[1], 0) / 4)
  const bgB = Math.round(corners.reduce((s, c) => s + c[2], 0) / 4)

  for (let i = 0; i < d.length; i += 4) {
    const dr = d[i] - bgR
    const dg = d[i + 1] - bgG
    const db = d[i + 2] - bgB
    const delta = Math.sqrt(dr * dr + dg * dg + db * db)
    if (delta < tolerance) {
      d[i + 3] = 0
    } else if (delta < tolerance * 1.5) {
      // Soft edge
      d[i + 3] = Math.round(((delta - tolerance) / (tolerance * 0.5)) * 255)
    }
  }

  return imageData
}

/** ImageData cache keyed by image src URL — processed once per unique image. */
const bgCache = new Map<string, ImageData>()

function getStrippedImageData(img: HTMLImageElement): ImageData {
  if (!bgCache.has(img.src)) {
    bgCache.set(img.src, removeBackground(img))
  }
  return bgCache.get(img.src)!
}

// ─── Main render ──────────────────────────────────────────────────────────────

/**
 * Draw the face photo and the glasses overlay onto `ctx`.
 *
 * Rendering path:
 *   1. Draw face photo (full canvas).
 *   2. Strip glasses background (cached after first call per product image).
 *   3. Solve a 3-point affine from glasses-image anchors → face landmarks.
 *   4. ctx.setTransform + drawImage — one GPU-composited pass, no manual
 *      translate/rotate/scale decomposition needed.
 *
 * Falls back to drawing the raw glasses image (without bg removal) if the
 * canvas is tainted due to missing CORS headers on the image origin.
 */
export async function renderOverlay(
  ctx: CanvasRenderingContext2D,
  faceImg: HTMLImageElement,
  glassesImg: HTMLImageElement,
  landmarks: FaceLandmark[],
  product: Product,
): Promise<void> {
  const { width: cw, height: ch } = ctx.canvas
  ctx.clearRect(0, 0, cw, ch)

  // ── Layer 1: face photo ───────────────────────────────────────────────────
  ctx.drawImage(faceImg, 0, 0, cw, ch)

  // ── Layer 2: glasses ──────────────────────────────────────────────────────
  const imgW = glassesImg.naturalWidth
  const imgH = glassesImg.naturalHeight

  // Background-stripped source (falls back to raw if canvas is tainted)
  let drawSource: HTMLCanvasElement | HTMLImageElement
  try {
    const stripped = getStrippedImageData(glassesImg)
    const tmp = document.createElement('canvas')
    tmp.width = imgW
    tmp.height = imgH
    tmp.getContext('2d')!.putImageData(stripped, 0, 0)
    drawSource = tmp
  } catch {
    drawSource = glassesImg
  }

  // 3-point affine: glasses image space → canvas space
  const src = computeGlassesSources(product, imgW, imgH)
  const dst = computeFaceTargets(landmarks, cw, ch)

  const { a, b, c, d, e, f }: AffineCoeffs = solveAffine(
    [src.bridge, src.leftTemple, src.rightTemple],
    [dst.bridge, dst.leftTemple, dst.rightTemple],
  )

  ctx.save()
  ctx.imageSmoothingEnabled = true
  ctx.imageSmoothingQuality = 'high'
  ctx.setTransform(a, b, c, d, e, f)
  ctx.drawImage(drawSource, 0, 0, imgW, imgH)
  ctx.restore()
}
