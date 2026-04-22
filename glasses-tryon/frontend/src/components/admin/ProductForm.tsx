import { useState, useRef, type ChangeEvent, type FormEvent } from 'react'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Button } from '@/components/ui/Button'
import { AnchorPointEditor, type AnchorPoints } from './AnchorPointEditor'
import { uploadGlassesPng } from '@/lib/storage'
import type { GlassesShape, ProductFormData } from '@/types/product'

const SHAPES: GlassesShape[] = ['round', 'square', 'aviator', 'cat-eye', 'oval', 'rectangle']

interface Props {
  initialData?: Partial<ProductFormData>
  onSubmit: (data: ProductFormData) => Promise<void>
  submitLabel?: string
}

const EMPTY_ANCHORS: AnchorPoints = {
  bridge_x: 0, bridge_y: 0,
  left_temple_x: 0, left_temple_y: 0,
  right_temple_x: 0, right_temple_y: 0,
}

export function ProductForm({ initialData, onSubmit, submitLabel = 'Save Product' }: Props) {
  const [name, setName] = useState(initialData?.name ?? '')
  const [brand, setBrand] = useState(initialData?.brand ?? '')
  const [price, setPrice] = useState(String(initialData?.price ?? ''))
  const [shape, setShape] = useState<GlassesShape>(initialData?.shape ?? 'round')
  const [color, setColor] = useState(initialData?.color ?? '')
  const [description, setDescription] = useState(initialData?.description ?? '')
  const [imageUrl, setImageUrl] = useState(initialData?.image_url ?? '')
  const [anchors, setAnchors] = useState<AnchorPoints>(
    initialData
      ? {
          bridge_x: initialData.bridge_x ?? 0,
          bridge_y: initialData.bridge_y ?? 0,
          left_temple_x: initialData.left_temple_x ?? 0,
          left_temple_y: initialData.left_temple_y ?? 0,
          right_temple_x: initialData.right_temple_x ?? 0,
          right_temple_y: initialData.right_temple_y ?? 0,
        }
      : EMPTY_ANCHORS,
  )

  const [uploading, setUploading] = useState(false)
  const [uploadPct, setUploadPct] = useState(0)
  const [submitting, setSubmitting] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})
  const fileInputRef = useRef<HTMLInputElement>(null)

  async function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    if (file.type !== 'image/png') {
      setErrors((prev) => ({ ...prev, image: 'Only PNG files are accepted.' }))
      return
    }
    setUploading(true)
    setErrors((prev) => ({ ...prev, image: '' }))
    try {
      const url = await uploadGlassesPng(file, setUploadPct)
      setImageUrl(url)
      setAnchors(EMPTY_ANCHORS) // reset anchors for new image
    } catch {
      setErrors((prev) => ({ ...prev, image: 'Upload failed. Check Firebase Storage rules.' }))
    } finally {
      setUploading(false)
    }
  }

  function validate(): boolean {
    const e: Record<string, string> = {}
    if (!name.trim()) e.name = 'Required'
    if (!brand.trim()) e.brand = 'Required'
    if (!price || isNaN(Number(price)) || Number(price) <= 0) e.price = 'Enter a valid price'
    if (!color.trim()) e.color = 'Required'
    if (!imageUrl) e.image = 'Upload a glasses PNG first'
    // A placed anchor has at least one non-zero coordinate (x=0 center is valid, but y=0 top is also edge)
    // We track placement via the editor — just ensure not all-zero per pair
    const allAnchorsSet = (['bridge', 'left_temple', 'right_temple'] as const).every(
      (k) => anchors[`${k}_x` as keyof AnchorPoints] !== 0 || anchors[`${k}_y` as keyof AnchorPoints] !== 0,
    )
    if (!allAnchorsSet) e.anchors = 'Set all 3 anchor points on the image'
    setErrors(e)
    return Object.keys(e).length === 0
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!validate()) return
    setSubmitting(true)
    try {
      await onSubmit({
        name, brand, price: Number(price), shape, color,
        description: description || undefined,
        image_url: imageUrl,
        ...anchors,
      })
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6 max-w-2xl">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Input
          id="name" label="Name *"
          value={name} onChange={(e) => setName(e.target.value)}
          error={errors.name}
        />
        <Input
          id="brand" label="Brand *"
          value={brand} onChange={(e) => setBrand(e.target.value)}
          error={errors.brand}
        />
        <Input
          id="price" label="Price *" type="number" min="0.01" step="0.01"
          value={price} onChange={(e) => setPrice(e.target.value)}
          error={errors.price}
        />
        <Select
          id="shape" label="Shape *"
          value={shape}
          onChange={(e) => setShape(e.target.value as GlassesShape)}
        >
          {SHAPES.map((s) => <option key={s} value={s} className="capitalize">{s}</option>)}
        </Select>
        <Input
          id="color" label="Color *"
          value={color} onChange={(e) => setColor(e.target.value)}
          error={errors.color}
        />
      </div>

      <div className="flex flex-col gap-1">
        <label className="text-sm font-medium text-gray-700">Description</label>
        <textarea
          rows={3}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 resize-none"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Optional product description…"
        />
      </div>

      {/* Image upload */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700">Glasses PNG *</label>
        <div className="flex items-center gap-3">
          <Button
            type="button"
            variant="secondary"
            size="sm"
            disabled={uploading}
            onClick={() => fileInputRef.current?.click()}
          >
            {uploading ? `Uploading ${Math.round(uploadPct)}%…` : 'Upload PNG'}
          </Button>
          {imageUrl && (
            <img
              src={imageUrl}
              alt="Uploaded glasses"
              className="h-12 object-contain bg-gray-100 rounded px-2"
            />
          )}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/png"
            className="hidden"
            onChange={handleFileChange}
          />
        </div>
        {errors.image && <p className="text-xs text-red-600">{errors.image}</p>}
      </div>

      {/* Anchor point editor — shown only after image is uploaded */}
      {imageUrl && (
        <div className="border border-gray-100 rounded-2xl p-5 bg-gray-50">
          <AnchorPointEditor
            imageUrl={imageUrl}
            value={anchors}
            onChange={setAnchors}
          />
          {errors.anchors && <p className="text-xs text-red-600 mt-2">{errors.anchors}</p>}
        </div>
      )}

      <div className="pt-2">
        <Button type="submit" size="lg" disabled={submitting || uploading}>
          {submitting ? 'Saving…' : submitLabel}
        </Button>
      </div>
    </form>
  )
}

