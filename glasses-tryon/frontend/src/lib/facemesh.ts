import { FaceMesh, type Results, type NormalizedLandmarkList } from '@mediapipe/face_mesh'

let instance: FaceMesh | null = null

function getInstance(): FaceMesh {
  if (!instance) {
    instance = new FaceMesh({
      // Served from /mediapipe/ via vite-plugin-static-copy (build)
      // and vite-plugin-static-copy's dev middleware (dev server)
      locateFile: (file) => `/mediapipe/${file}`,
    })
    instance.setOptions({
      maxNumFaces: 1,
      refineLandmarks: true,
      minDetectionConfidence: 0.5,
      minTrackingConfidence: 0.5,
    })
  }
  return instance
}

/**
 * Detect face landmarks in a static image element.
 * Returns the 478-point normalized landmark list or null if no face found.
 */
export function detectFaceLandmarks(
  imageEl: HTMLImageElement,
): Promise<NormalizedLandmarkList | null> {
  return new Promise((resolve, reject) => {
    const mesh = getInstance()

    let settled = false
    const settle = (value: NormalizedLandmarkList | null) => {
      if (settled) return
      settled = true
      // Remove listener so it doesn't fire on the next call
      mesh.onResults(() => {})
      resolve(value)
    }

    mesh.onResults((results: Results) => {
      if (results.multiFaceLandmarks && results.multiFaceLandmarks.length > 0) {
        settle(results.multiFaceLandmarks[0])
      } else {
        settle(null)
      }
    })

    mesh.send({ image: imageEl }).catch((err) => {
      if (!settled) {
        settled = true
        mesh.onResults(() => {})
        reject(err)
      }
    })
  })
}
