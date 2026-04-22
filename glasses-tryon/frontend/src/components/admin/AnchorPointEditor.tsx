import { useRef, useEffect, useState, useCallback } from 'react'
import { Button } from '@/components/ui/Button'

export interface AnchorPoints {
  bridge_x: number
  bridge_y: number
  left_temple_x: number
  left_temple_y: number
  right_temple_x: number
  right_temple_y: number
}

type AnchorKey = 'bridge' | 'left_temple' | 'right_temple'

const ANCHOR_CONFIG: { key: AnchorKey; label: string; color: string }[] = [
  { key: 'bridge', label: 'Bridge Center', color: '#4361ee' },
  { key: 'left_temple', label: 'Left Temple End', color: '#ef4444' },
  { key: 'right_temple', label: 'Right Temple End', color: '#22c55e' },
]

interface Props {
  imageUrl: string
  value: AnchorPoints
  onChange: (points: AnchorPoints) => void
}

export function AnchorPointEditor({ imageUrl, value, onChange }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const imageRef = useRef<HTMLImageElement | null>(null)
  const [activeAnchor, setActiveAnchor] = useState<AnchorKey>('bridge')
  const [imgSize, setImgSize] = useState({ w: 0, h: 0 })

  const draw = useCallback(() => {
    const canvas = canvasRef.current
    const img = imageRef.current
    if (!canvas || !img || imgSize.w === 0) return

    const ctx = canvas.getContext('2d')!
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    ctx.drawImage(img, 0, 0, canvas.width, canvas.height)

    // Draw anchor points
    ANCHOR_CONFIG.forEach(({ key, color }) => {
      const x = value[`${key}_x` as keyof AnchorPoints] * canvas.width
      const y = value[`${key}_y` as keyof AnchorPoints] * canvas.height

      if (x === 0 && y === 0) return

      ctx.beginPath()
      ctx.arc(x, y, 8, 0, Math.PI * 2)
      ctx.fillStyle = color + 'aa'
      ctx.fill()
      ctx.strokeStyle = color
      ctx.lineWidth = 2
      ctx.stroke()

      // Crosshair
      ctx.beginPath()
      ctx.moveTo(x - 12, y)
      ctx.lineTo(x + 12, y)
      ctx.moveTo(x, y - 12)
      ctx.lineTo(x, y + 12)
      ctx.strokeStyle = color
      ctx.lineWidth = 1.5
      ctx.stroke()
    })
  }, [value, imgSize])

  useEffect(() => {
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload = () => {
      imageRef.current = img
      const canvas = canvasRef.current!
      // Scale to fit max 600px wide while preserving aspect ratio
      const maxW = 600
      const scale = Math.min(1, maxW / img.naturalWidth)
      canvas.width = img.naturalWidth * scale
      canvas.height = img.naturalHeight * scale
      setImgSize({ w: canvas.width, h: canvas.height })
    }
    img.src = imageUrl
  }, [imageUrl])

  useEffect(() => { draw() }, [draw])

  function handleCanvasClick(e: React.MouseEvent<HTMLCanvasElement>) {
    const canvas = canvasRef.current!
    const rect = canvas.getBoundingClientRect()
    const scaleX = canvas.width / rect.width
    const scaleY = canvas.height / rect.height
    const x = ((e.clientX - rect.left) * scaleX) / canvas.width
    const y = ((e.clientY - rect.top) * scaleY) / canvas.height

    onChange({
      ...value,
      [`${activeAnchor}_x`]: Math.max(0, Math.min(1, x)),
      [`${activeAnchor}_y`]: Math.max(0, Math.min(1, y)),
    })
  }

  const allSet = ANCHOR_CONFIG.every(({ key }) => {
    const x = value[`${key}_x` as keyof AnchorPoints]
    const y = value[`${key}_y` as keyof AnchorPoints]
    return x > 0 || y > 0
  })

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-sm font-semibold text-gray-700 mb-2">Anchor Point Editor</h3>
        <p className="text-xs text-gray-500">
          Select an anchor type, then click on the glasses image to place it. All three points are required.
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        {ANCHOR_CONFIG.map(({ key, label, color }) => {
          const isSet = value[`${key}_x` as keyof AnchorPoints] > 0 || value[`${key}_y` as keyof AnchorPoints] > 0
          return (
            <button
              key={key}
              type="button"
              onClick={() => setActiveAnchor(key)}
              className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium border transition-all ${
                activeAnchor === key
                  ? 'border-transparent text-white shadow-sm'
                  : 'border-gray-200 text-gray-600 hover:border-gray-300 bg-white'
              }`}
              style={activeAnchor === key ? { backgroundColor: color } : {}}
            >
              <span
                className="w-2.5 h-2.5 rounded-full"
                style={{ backgroundColor: activeAnchor === key ? '#fff' : color }}
              />
              {label}
              {isSet && <span className="ml-1 text-xs">{activeAnchor === key ? '✓' : '✓'}</span>}
            </button>
          )
        })}
      </div>

      <div className="relative border-2 border-dashed border-gray-200 rounded-xl overflow-hidden bg-gray-50 cursor-crosshair">
        <canvas
          ref={canvasRef}
          onClick={handleCanvasClick}
          className="max-w-full block mx-auto"
          style={{ touchAction: 'none' }}
        />
        {imgSize.w === 0 && (
          <div className="absolute inset-0 flex items-center justify-center text-gray-400 text-sm">
            Loading image…
          </div>
        )}
      </div>

      {!allSet && (
        <p className="text-xs text-orange-600 font-medium">
          ⚠ Place all 3 anchor points before saving.
        </p>
      )}

      <div className="text-xs text-gray-400 grid grid-cols-3 gap-2">
        {ANCHOR_CONFIG.map(({ key, label, color }) => {
          const x = value[`${key}_x` as keyof AnchorPoints]
          const y = value[`${key}_y` as keyof AnchorPoints]
          const isSet = x > 0 || y > 0
          return (
            <div key={key} className="bg-gray-50 rounded-lg p-2 border border-gray-100">
              <p className="font-medium" style={{ color }}>{label}</p>
              {isSet ? (
                <p className="font-mono mt-0.5">({x.toFixed(3)}, {y.toFixed(3)})</p>
              ) : (
                <p className="text-gray-300 mt-0.5">not set</p>
              )}
            </div>
          )
        })}
      </div>

      <Button
        type="button"
        variant="ghost"
        size="sm"
        className="text-gray-400"
        onClick={() =>
          onChange({ bridge_x: 0, bridge_y: 0, left_temple_x: 0, left_temple_y: 0, right_temple_x: 0, right_temple_y: 0 })
        }
      >
        Reset all anchors
      </Button>
    </div>
  )
}
