import { useParams, useNavigate, Link } from 'react-router-dom'
import { AdminNav } from '@/components/layout/AdminNav'
import { ProductForm } from '@/components/admin/ProductForm'
import { PageSpinner } from '@/components/ui/PageSpinner'
import { useProduct } from '@/hooks/useProducts'
import api from '@/lib/api'
import type { ProductFormData } from '@/types/product'

export default function AdminEditProductPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { product, loading, error } = useProduct(id)

  async function handleSubmit(data: ProductFormData) {
    await api.put(`/api/products/${id}`, data)
    navigate('/admin')
  }

  if (loading) return <><AdminNav /><PageSpinner /></>

  if (error || !product) {
    return (
      <>
        <AdminNav />
        <div className="max-w-3xl mx-auto px-4 py-20 text-center">
          <p className="text-gray-500">Product not found.</p>
          <Link to="/admin" className="mt-4 inline-block text-brand-500 hover:underline">Back</Link>
        </div>
      </>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <AdminNav />
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Edit — {product.name}</h1>
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <ProductForm
            initialData={product}
            onSubmit={handleSubmit}
            submitLabel="Update Product"
          />
        </div>
      </div>
    </div>
  )
}
