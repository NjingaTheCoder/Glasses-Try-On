// Augment @mediapipe/face_mesh types so TypeScript resolves them
// The package ships its own .d.ts; this file is here only as a reference marker.
declare module '@mediapipe/face_mesh' {
  export interface NormalizedLandmark {
    x: number
    y: number
    z: number
    visibility?: number
  }

  export type NormalizedLandmarkList = NormalizedLandmark[]

  export interface Results {
    multiFaceLandmarks: NormalizedLandmarkList[]
    image: HTMLCanvasElement
  }

  export interface FaceMeshOptions {
    maxNumFaces?: number
    refineLandmarks?: boolean
    minDetectionConfidence?: number
    minTrackingConfidence?: number
  }

  export class FaceMesh {
    constructor(config: { locateFile: (file: string) => string })
    setOptions(options: FaceMeshOptions): void
    onResults(callback: (results: Results) => void): void
    send(inputs: { image: HTMLImageElement | HTMLVideoElement | HTMLCanvasElement }): Promise<void>
    close(): Promise<void>
  }
}
