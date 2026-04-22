export type GlassesShape = 'round' | 'square' | 'aviator' | 'cat-eye' | 'oval' | 'rectangle'

export interface Product {
  id: string
  name: string
  brand: string
  price: number
  shape: GlassesShape
  color: string
  description?: string
  image_url: string
  bridge_x: number
  bridge_y: number
  left_temple_x: number
  left_temple_y: number
  right_temple_x: number
  right_temple_y: number
  created_at: string
  updated_at: string
}

export interface ProductFilters {
  shape?: GlassesShape
  color?: string
  min_price?: number
  max_price?: number
  q?: string
}

export interface ProductFormData {
  name: string
  brand: string
  price: number
  shape: GlassesShape
  color: string
  description?: string
  image_url: string
  bridge_x: number
  bridge_y: number
  left_temple_x: number
  left_temple_y: number
  right_temple_x: number
  right_temple_y: number
}
