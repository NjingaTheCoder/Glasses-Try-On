import { useNavigate } from 'react-router-dom'
import { AdminNav } from '@/components/layout/AdminNav'
import { ProductForm } from '@/components/admin/ProductForm'
import api from '@/lib/api'
import type { ProductFormData } from '@/types/product'

export default function AdminNewProductPage() {
  const navigate = useNavigate()

  async function handleSubmit(data: ProductFormData) {
    await api.post('/api/products', data)
    navigate('/admin')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <AdminNav />
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">New Product</h1>
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
          <ProductForm onSubmit={handleSubmit} submitLabel="Create Product" />
        </div>
      </div>
    </div>
  )
}
