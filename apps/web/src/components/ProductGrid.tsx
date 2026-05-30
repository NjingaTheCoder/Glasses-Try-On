import { useQuery } from '@tanstack/react-query'
import apiClient from '../api/client'
import type { Product } from '../types'

interface ProductGridProps {
  storeId: number
  selectedProduct: Product | null
  onSelectProduct: (product: Product) => void
}

export default function ProductGrid({ storeId, selectedProduct, onSelectProduct }: ProductGridProps) {
  const { data: productsData, isLoading } = useQuery({
    queryKey: ['products', storeId],
    queryFn: () => apiClient.getProducts({ store_id: storeId }),
    enabled: !!storeId,
  })

  if (isLoading) {
    return <div className="text-center py-8">Loading products...</div>
  }

  if (!productsData?.results.length) {
    return (
      <div className="text-center py-8 text-gray-500">
        No products available in this store
      </div>
    )
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {productsData.results.map((product) => (
        <div
          key={product.id}
          onClick={() => onSelectProduct(product)}
          className={`cursor-pointer rounded-lg overflow-hidden border-4 transition-all ${
            selectedProduct?.id === product.id
              ? 'border-blue-600 shadow-lg'
              : 'border-transparent hover:border-gray-300'
          }`}
        >
          <div className="bg-white">
            <img
              src={product.image_url}
              alt={product.title}
              className="w-full h-48 object-cover"
            />
            <div className="p-3">
              <h3 className="font-semibold text-sm mb-1 truncate">{product.title}</h3>
              <p className="text-lg font-bold text-blue-600">${product.price}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
