import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { AdminNav } from '@/components/layout/AdminNav'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { PageSpinner } from '@/components/ui/PageSpinner'
import { useAuthStore } from '@/store/authStore'
import { useProducts } from '@/hooks/useProducts'
import api from '@/lib/api'

export default function AdminDashboardPage() {
  const { init } = useAuthStore()
  const { products, loading, error, refetch } = useProducts()
  const [deleting, setDeleting] = useState<string | null>(null)

  useEffect(() => {
    const unsub = init()
    return unsub
  }, [init])

  async function handleDelete(id: string, name: string) {
    if (!confirm(`Delete "${name}"? This cannot be undone.`)) return
    setDeleting(id)
    try {
      await api.delete(`/api/products/${id}`)
      refetch()
    } catch {
      alert('Failed to delete product.')
    } finally {
      setDeleting(null)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <AdminNav />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Products</h1>
          <Link to="/admin/products/new">
            <Button>+ Add Product</Button>
          </Link>
        </div>

        {loading ? (
          <PageSpinner />
        ) : error ? (
          <p className="text-red-500">{error}</p>
        ) : (
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100 bg-gray-50 text-left">
                  <th className="px-4 py-3 font-semibold text-gray-500">Image</th>
                  <th className="px-4 py-3 font-semibold text-gray-500">Name</th>
                  <th className="px-4 py-3 font-semibold text-gray-500">Brand</th>
                  <th className="px-4 py-3 font-semibold text-gray-500">Shape</th>
                  <th className="px-4 py-3 font-semibold text-gray-500">Price</th>
                  <th className="px-4 py-3 font-semibold text-gray-500">Anchors</th>
                  <th className="px-4 py-3 font-semibold text-gray-500">Actions</th>
                </tr>
              </thead>
              <tbody>
                {products.map((p) => {
                  const hasAnchors = p.bridge_x > 0 || p.bridge_y > 0
                  return (
                    <tr key={p.id} className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                      <td className="px-4 py-3">
                        <img
                          src={p.image_url}
                          alt={p.name}
                          className="w-14 h-10 object-contain rounded bg-gray-100"
                        />
                      </td>
                      <td className="px-4 py-3 font-medium text-gray-900">{p.name}</td>
                      <td className="px-4 py-3 text-gray-500">{p.brand}</td>
                      <td className="px-4 py-3">
                        <Badge className="capitalize">{p.shape}</Badge>
                      </td>
                      <td className="px-4 py-3 font-medium">${p.price.toFixed(2)}</td>
                      <td className="px-4 py-3">
                        {hasAnchors ? (
                          <span className="text-green-600 font-medium">✓ Set</span>
                        ) : (
                          <span className="text-orange-500 font-medium">⚠ Missing</span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex gap-2">
                          <Link to={`/admin/products/${p.id}/edit`}>
                            <Button size="sm" variant="secondary">Edit</Button>
                          </Link>
                          <Button
                            size="sm"
                            variant="danger"
                            disabled={deleting === p.id}
                            onClick={() => handleDelete(p.id, p.name)}
                          >
                            {deleting === p.id ? '…' : 'Delete'}
                          </Button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
                {products.length === 0 && (
                  <tr>
                    <td colSpan={7} className="px-4 py-12 text-center text-gray-400">
                      No products yet.{' '}
                      <Link to="/admin/products/new" className="text-brand-500 hover:underline">Add one</Link>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
