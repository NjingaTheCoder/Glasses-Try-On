export interface FaceLandmark {
  x: number
  y: number
  z: number
}

export interface DetectedFace {
  landmarks: FaceLandmark[]
  imageWidth: number
  imageHeight: number
}

export interface AnchorPoint {
  x: number // normalized 0-1
  y: number // normalized 0-1
}
