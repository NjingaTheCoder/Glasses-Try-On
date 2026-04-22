import { useState, useEffect, useCallback } from 'react'
import api from '@/lib/api'
import type { Product, ProductFilters } from '@/types/product'

interface UseProductsResult {
  products: Product[]
  total: number
  loading: boolean
  error: string | null
  refetch: () => void
}

export function useProducts(filters: ProductFilters = {}): UseProductsResult {
  const [products, setProducts] = useState<Product[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Serialize filters to a stable string for useEffect deps
  const filterKey = JSON.stringify(filters)

  const fetch = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const params = Object.fromEntries(
        Object.entries(JSON.parse(filterKey)).filter(
          ([, v]) => v !== undefined && v !== '' && v !== null,
        ),
      )
      const { data } = await api.get('/api/products', { params })
      setProducts(data.items)
      setTotal(data.total)
    } catch {
      setError('Failed to load products. Is the backend running?')
    } finally {
      setLoading(false)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filterKey])

  useEffect(() => {
    fetch()
  }, [fetch])

  return { products, total, loading, error, refetch: fetch }
}

export function useProduct(id: string | undefined) {
  const [product, setProduct] = useState<Product | null>(null)
  const [loading, setLoading] = useState(!!id)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) {
      setLoading(false)
      return
    }
    setLoading(true)
    api
      .get(`/api/products/${id}`)
      .then(({ data }) => setProduct(data))
      .catch(() => setError('Product not found'))
      .finally(() => setLoading(false))
  }, [id])

  return { product, loading, error }
}
