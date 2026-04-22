import { useState, useCallback } from 'react'
import { detectFaceLandmarks } from '@/lib/facemesh'
import { useTryOnStore } from '@/store/tryonStore'
import type { FaceLandmark } from '@/types/tryon'

interface UseFaceDetectionResult {
  detecting: boolean
  error: string | null
  runDetection: (imageEl: HTMLImageElement) => Promise<boolean>
  clearError: () => void
}

export function useFaceDetection(): UseFaceDetectionResult {
  const setDetectedFace = useTryOnStore((s) => s.setDetectedFace)
  const [detecting, setDetecting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const runDetection = useCallback(
    async (imageEl: HTMLImageElement): Promise<boolean> => {
      setDetecting(true)
      setError(null)
      try {
        const landmarks = await detectFaceLandmarks(imageEl)
        if (!landmarks) {
          setError(
            "We couldn't find a face. Try a clearer front-facing photo.",
          )
          return false
        }
        // Store as typed array; landmarks are normalized 0-1
        const typed: FaceLandmark[] = Array.from(landmarks).map((lm) => ({
          x: lm.x,
          y: lm.y,
          z: lm.z,
        }))
        setDetectedFace({
          landmarks: typed,
          imageWidth: imageEl.naturalWidth,
          imageHeight: imageEl.naturalHeight,
        })
        return true
      } catch {
        setError('Face detection failed. Please try again.')
        return false
      } finally {
        setDetecting(false)
      }
    },
    [setDetectedFace],
  )

  return { detecting, error, runDetection, clearError: () => setError(null) }
}
