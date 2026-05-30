import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import apiClient from '../api/client'
import UploadCard from '../components/UploadCard'
import ProductGrid from '../components/ProductGrid'
import Gallery from '../components/Gallery'
import type { Product, UserImage } from '../types'

export default function TryOn() {
  const [selectedImage, setSelectedImage] = useState<UserImage | null>(null)
  const [selectedStore, setSelectedStore] = useState<number | null>(null)
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null)

  const { data: imagesData } = useQuery({
    queryKey: ['user-images'],
    queryFn: () => apiClient.getUserImages(),
  })

  const { data: storesData } = useQuery({
    queryKey: ['stores'],
    queryFn: () => apiClient.getStores(),
  })

  const completedImages = imagesData?.results.filter((img) => img.status === 'COMPLETED') || []

  const handleTryOn = async () => {
    if (!selectedImage || !selectedProduct) {
      alert('Please select a photo and a product')
      return
    }

    try {
      const result = await apiClient.createGeneration({
        user_image_id: selectedImage.id,
        product_id: selectedProduct.id,
      })

      alert('Try-on generation started! Check the gallery below for results.')
      setSelectedProduct(null)
    } catch (err) {
      alert('Failed to create try-on generation')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link to="/dashboard" className="text-blue-600 hover:underline">
                ← Back to Dashboard
              </Link>
            </div>
            <h1 className="flex items-center text-2xl font-bold">Virtual Try-On</h1>
            <div className="w-32"></div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Step 1: Upload Photo */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Step 1: Upload Your Photo</h2>
          <UploadCard />

          {completedImages.length > 0 && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-3">Your Photos</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {completedImages.map((img) => (
                  <div
                    key={img.id}
                    onClick={() => setSelectedImage(img)}
                    className={`cursor-pointer rounded-lg overflow-hidden border-4 transition-all ${
                      selectedImage?.id === img.id
                        ? 'border-blue-600 shadow-lg'
                        : 'border-transparent hover:border-gray-300'
                    }`}
                  >
                    <img
                      src={img.processed_url}
                      alt="Your photo"
                      className="w-full h-48 object-cover"
                    />
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>

        {/* Step 2: Select Store & Product */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-4">Step 2: Choose a Product</h2>

          <div className="mb-4">
            <label className="label">Select Store</label>
            <select
              className="input max-w-md"
              value={selectedStore || ''}
              onChange={(e) => setSelectedStore(parseInt(e.target.value))}
            >
              <option value="">-- Select a store --</option>
              {storesData?.results.map((store) => (
                <option key={store.id} value={store.id}>
                  {store.name} ({store.product_count} products)
                </option>
              ))}
            </select>
          </div>

          {selectedStore && (
            <ProductGrid
              storeId={selectedStore}
              selectedProduct={selectedProduct}
              onSelectProduct={setSelectedProduct}
            />
          )}
        </section>

        {/* Step 3: Generate */}
        <section className="mb-12">
          <div className="card bg-blue-50 border-2 border-blue-200">
            <h2 className="text-2xl font-bold mb-4">Step 3: Generate Try-On</h2>
            <div className="flex justify-between items-center">
              <div>
                <p className="text-gray-700">
                  {selectedImage ? '✓ Photo selected' : '○ Select a photo'}
                </p>
                <p className="text-gray-700">
                  {selectedProduct ? '✓ Product selected' : '○ Select a product'}
                </p>
              </div>
              <button
                onClick={handleTryOn}
                disabled={!selectedImage || !selectedProduct}
                className="btn btn-primary text-lg px-8 py-3"
              >
                Try It On!
              </button>
            </div>
          </div>
        </section>

        {/* Gallery */}
        <section>
          <h2 className="text-2xl font-bold mb-4">Your Try-On Results</h2>
          <Gallery />
        </section>
      </main>
    </div>
  )
}
