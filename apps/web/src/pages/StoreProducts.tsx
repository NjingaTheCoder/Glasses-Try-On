import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import apiClient from '../api/client'

export default function StoreProducts() {
  const { id } = useParams<{ id: string }>()
  const storeId = parseInt(id || '0')

  const [showImport, setShowImport] = useState(false)
  const [importType, setImportType] = useState<'shopify' | 'csv'>('csv')
  const [shopifyDomain, setShopifyDomain] = useState('')
  const [shopifyToken, setShopifyToken] = useState('')
  const [csvFile, setCsvFile] = useState<File | null>(null)
  const [importing, setImporting] = useState(false)

  const { data: store } = useQuery({
    queryKey: ['store', storeId],
    queryFn: () => apiClient.getStore(storeId),
  })

  const { data: productsData, refetch } = useQuery({
    queryKey: ['products', storeId],
    queryFn: () => apiClient.getProducts({ store_id: storeId }),
  })

  const handleShopifySync = async (e: React.FormEvent) => {
    e.preventDefault()
    setImporting(true)

    try {
      const result = await apiClient.shopifySync(storeId, {
        shopify_domain: shopifyDomain,
        shopify_access_token: shopifyToken,
      })
      alert(`Sync completed! Created: ${result.stats.created}, Errors: ${result.stats.errors}`)
      setShowImport(false)
      refetch()
    } catch (err) {
      alert('Shopify sync failed')
    } finally {
      setImporting(false)
    }
  }

  const handleCSVImport = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!csvFile) {
      alert('Please select a CSV file')
      return
    }

    setImporting(true)

    try {
      const result = await apiClient.csvImport(storeId, csvFile)
      alert(`Import completed! Created: ${result.stats.created}, Errors: ${result.stats.errors}`)
      setShowImport(false)
      setCsvFile(null)
      refetch()
    } catch (err) {
      alert('CSV import failed')
    } finally {
      setImporting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-4">
              <Link to="/dashboard" className="text-blue-600 hover:underline">
                ← Back to Dashboard
              </Link>
              <h1 className="text-2xl font-bold">{store?.name}</h1>
            </div>
            <div className="flex items-center">
              <button onClick={() => setShowImport(true)} className="btn btn-primary">
                Import Products
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {showImport && (
          <div className="card mb-8">
            <h3 className="text-xl font-bold mb-4">Import Products</h3>

            <div className="flex space-x-4 mb-4">
              <button
                onClick={() => setImportType('csv')}
                className={`btn ${importType === 'csv' ? 'btn-primary' : 'btn-secondary'}`}
              >
                CSV Import
              </button>
              <button
                onClick={() => setImportType('shopify')}
                className={`btn ${importType === 'shopify' ? 'btn-primary' : 'btn-secondary'}`}
              >
                Shopify Sync
              </button>
            </div>

            {importType === 'csv' ? (
              <form onSubmit={handleCSVImport} className="space-y-4">
                <div>
                  <label className="label">CSV File</label>
                  <input
                    type="file"
                    accept=".csv"
                    className="input"
                    onChange={(e) => setCsvFile(e.target.files?.[0] || null)}
                    required
                  />
                  <p className="text-sm text-gray-500 mt-1">
                    CSV should have columns: title, product_url, image_url, price, tags
                  </p>
                </div>
                <div className="flex space-x-2">
                  <button type="submit" className="btn btn-primary" disabled={importing}>
                    {importing ? 'Importing...' : 'Import'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowImport(false)}
                    className="btn btn-secondary"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            ) : (
              <form onSubmit={handleShopifySync} className="space-y-4">
                <div>
                  <label className="label">Shopify Domain</label>
                  <input
                    type="text"
                    className="input"
                    placeholder="mystore.myshopify.com"
                    value={shopifyDomain}
                    onChange={(e) => setShopifyDomain(e.target.value)}
                    required
                  />
                </div>
                <div>
                  <label className="label">Admin API Access Token</label>
                  <input
                    type="password"
                    className="input"
                    value={shopifyToken}
                    onChange={(e) => setShopifyToken(e.target.value)}
                    required
                  />
                </div>
                <div className="flex space-x-2">
                  <button type="submit" className="btn btn-primary" disabled={importing}>
                    {importing ? 'Syncing...' : 'Sync'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowImport(false)}
                    className="btn btn-secondary"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            )}
          </div>
        )}

        <h2 className="text-2xl font-bold mb-6">
          Products ({productsData?.results.length || 0})
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {productsData?.results.map((product) => (
            <div key={product.id} className="card">
              <img
                src={product.image_url}
                alt={product.title}
                className="w-full h-48 object-cover rounded-lg mb-4"
              />
              <h3 className="font-bold mb-2">{product.title}</h3>
              <p className="text-lg font-semibold text-blue-600">${product.price}</p>
              {product.vendor && (
                <p className="text-sm text-gray-500">by {product.vendor}</p>
              )}
            </div>
          ))}
        </div>

        {productsData?.results.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">
              No products yet. Import products to get started!
            </p>
          </div>
        )}
      </main>
    </div>
  )
}
