/**
 * Pure 2-D geometry helpers.
 * No DOM dependencies — all functions are plain math, fully testable in isolation.
 */

export interface Point {
  x: number
  y: number
}

/**
 * Canvas ctx.setTransform(a, b, c, d, e, f) coefficients.
 *
 * The transform maps canvas-space (x, y) as:
 *   x' = a·x + c·y + e
 *   y' = b·x + d·y + f
 */
export interface AffineCoeffs {
  a: number
  b: number
  c: number
  d: number
  e: number
  f: number
}

export function midpoint(p1: Point, p2: Point): Point {
  return { x: (p1.x + p2.x) / 2, y: (p1.y + p2.y) / 2 }
}

/**
 * Linear interpolation — t=0 → p1, t=1 → p2, t>1 → beyond p2 (used for
 * temple extrapolation past the outer eye corner).
 */
export function lerp(p1: Point, p2: Point, t: number): Point {
  return {
    x: p1.x + (p2.x - p1.x) * t,
    y: p1.y + (p2.y - p1.y) * t,
  }
}

export function dist(p1: Point, p2: Point): number {
  const dx = p2.x - p1.x
  const dy = p2.y - p1.y
  return Math.sqrt(dx * dx + dy * dy)
}

/**
 * Solve a 2-D affine transform that maps 3 source points onto 3 destination
 * points exactly (no least-squares approximation needed: 6 DOF, 6 equations).
 *
 * Returns AffineCoeffs ready for ctx.setTransform(a, b, c, d, e, f).
 *
 * The 3 source points MUST NOT be collinear.  If they are (degenerate input),
 * the identity transform is returned so the caller never crashes.
 *
 * Derivation: solve A · [m11, m12, m13]ᵀ = [dx]  and
 *                    A · [m21, m22, m23]ᵀ = [dy]
 * where A = [[s0.x, s0.y, 1], [s1.x, s1.y, 1], [s2.x, s2.y, 1]]
 * using Cramer's rule (closed-form, no matrix library needed).
 *
 * Canvas convention:
 *   x' = m11·x + m12·y + m13  →  ctx a=m11, c=m12, e=m13
 *   y' = m21·x + m22·y + m23  →  ctx b=m21, d=m22, f=m23
 */
export function solveAffine(
  src: [Point, Point, Point],
  dst: [Point, Point, Point],
): AffineCoeffs {
  const [s0, s1, s2] = src
  const [d0, d1, d2] = dst

  // det of the source matrix A
  const det =
    s0.x * (s1.y - s2.y) -
    s0.y * (s1.x - s2.x) +
    (s1.x * s2.y - s2.x * s1.y)

  if (Math.abs(det) < 1e-8) {
    // Degenerate: collinear source points — return identity so nothing breaks
    return { a: 1, b: 0, c: 0, d: 1, e: 0, f: 0 }
  }

  const inv = 1 / det

  // ── x-row: m11·x + m12·y + m13 = x' ─────────────────────────────────────
  // Cramer col-1 replaced by dx
  const m11 =
    inv *
    (d0.x * (s1.y - s2.y) -
      s0.y * (d1.x - d2.x) +
      (d1.x * s2.y - d2.x * s1.y))

  // Cramer col-2 replaced by dx
  const m12 =
    inv *
    (s0.x * (d1.x - d2.x) -
      d0.x * (s1.x - s2.x) +
      (s1.x * d2.x - s2.x * d1.x))

  // Cramer col-3 replaced by dx
  const m13 =
    inv *
    (s0.x * (s1.y * d2.x - s2.y * d1.x) -
      s0.y * (s1.x * d2.x - s2.x * d1.x) +
      d0.x * (s1.x * s2.y - s2.x * s1.y))

  // ── y-row: m21·x + m22·y + m23 = y' ─────────────────────────────────────
  const m21 =
    inv *
    (d0.y * (s1.y - s2.y) -
      s0.y * (d1.y - d2.y) +
      (d1.y * s2.y - d2.y * s1.y))

  const m22 =
    inv *
    (s0.x * (d1.y - d2.y) -
      d0.y * (s1.x - s2.x) +
      (s1.x * d2.y - s2.x * d1.y))

  const m23 =
    inv *
    (s0.x * (s1.y * d2.y - s2.y * d1.y) -
      s0.y * (s1.x * d2.y - s2.x * d1.y) +
      d0.y * (s1.x * s2.y - s2.x * s1.y))

  // ctx.setTransform(a, b, c, d, e, f)
  return { a: m11, b: m21, c: m12, d: m22, e: m13, f: m23 }
}
