import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'
import apiClient from '../api/client'
import type { User } from '../types'

export default function Dashboard() {
  const navigate = useNavigate()
  const [showCreateStore, setShowCreateStore] = useState(false)
  const [storeName, setStoreName] = useState('')
  const [storeDescription, setStoreDescription] = useState('')

  const user: User = JSON.parse(localStorage.getItem('user') || '{}')

  const { data: storesData, refetch } = useQuery({
    queryKey: ['stores'],
    queryFn: () => apiClient.getStores(),
  })

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
    navigate('/login')
  }

  const handleCreateStore = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await apiClient.createStore({
        name: storeName,
        description: storeDescription,
      })
      setShowCreateStore(false)
      setStoreName('')
      setStoreDescription('')
      refetch()
    } catch (err) {
      alert('Failed to create store')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-blue-600">WearLens</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">
                {user.email} ({user.role})
              </span>
              <Link to="/tryon" className="btn btn-secondary">
                Try On
              </Link>
              <button onClick={handleLogout} className="btn btn-secondary">
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900">My Stores</h2>
          {user.role === 'MERCHANT' && (
            <button
              onClick={() => setShowCreateStore(true)}
              className="btn btn-primary"
            >
              Create Store
            </button>
          )}
        </div>

        {showCreateStore && (
          <div className="card mb-8">
            <h3 className="text-xl font-bold mb-4">Create New Store</h3>
            <form onSubmit={handleCreateStore} className="space-y-4">
              <div>
                <label className="label">Store Name</label>
                <input
                  type="text"
                  className="input"
                  value={storeName}
                  onChange={(e) => setStoreName(e.target.value)}
                  required
                />
              </div>
              <div>
                <label className="label">Description</label>
                <textarea
                  className="input"
                  rows={3}
                  value={storeDescription}
                  onChange={(e) => setStoreDescription(e.target.value)}
                />
              </div>
              <div className="flex space-x-2">
                <button type="submit" className="btn btn-primary">
                  Create
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateStore(false)}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {storesData?.results.map((store) => (
            <Link
              key={store.id}
              to={`/store/${store.id}/products`}
              className="card hover:shadow-lg transition-shadow"
            >
              <h3 className="text-xl font-bold mb-2">{store.name}</h3>
              <p className="text-gray-600 mb-4">{store.description}</p>
              <div className="flex justify-between text-sm text-gray-500">
                <span>{store.product_count} products</span>
                <span className="capitalize">{store.integration_type.toLowerCase()}</span>
              </div>
            </Link>
          ))}
        </div>

        {storesData?.results.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No stores yet. Create one to get started!</p>
          </div>
        )}
      </main>
    </div>
  )
}
