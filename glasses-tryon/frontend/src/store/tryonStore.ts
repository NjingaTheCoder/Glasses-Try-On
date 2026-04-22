import { create } from 'zustand'
import type { Product } from '@/types/product'

interface TryOnState {
  facePhoto: File | null
  facePhotoUrl: string | null
  selectedProduct: Product | null
  setFacePhoto: (file: File, url: string) => void
  setSelectedProduct: (product: Product) => void
  reset: () => void
}

export const useTryOnStore = create<TryOnState>((set) => ({
  facePhoto: null,
  facePhotoUrl: null,
  selectedProduct: null,

  setFacePhoto: (file, url) => set({ facePhoto: file, facePhotoUrl: url }),
  setSelectedProduct: (product) => set({ selectedProduct: product }),
  reset: () => set({ facePhoto: null, facePhotoUrl: null, selectedProduct: null }),
}))
