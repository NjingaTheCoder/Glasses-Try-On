import { useParams, Link } from 'react-router-dom'
import { Navbar } from '@/components/layout/Navbar'
import { Button } from '@/components/ui/Button'
import { PageSpinner } from '@/components/ui/PageSpinner'
import { useProduct } from '@/hooks/useProducts'

export default function ProductDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { product, loading, error } = useProduct(id)

  if (loading) return <><Navbar /><PageSpinner /></>

  if (error || !product) {
    return (
      <>
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 py-20 text-center">
          <p className="text-brand-500 text-lg font-medium">Product not found.</p>
          <Link to="/" className="mt-4 inline-block text-gold-500 hover:text-gold-600 font-semibold underline underline-offset-2">
            Back to collection
          </Link>
        </div>
      </>
    )
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#fafaf8' }}>
      <Navbar />

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-2 text-sm text-brand-400 mb-8">
          <Link to="/" className="hover:text-gold-500 transition-colors font-medium">Collection</Link>
          <span className="text-brand-200">/</span>
          <span className="text-brand-700 font-semibold">{product.name}</span>
        </nav>

        <div className="bg-white rounded-3xl shadow-card overflow-hidden border border-brand-100">
          <div className="grid md:grid-cols-2">
            {/* Image panel */}
            <div className="bg-gradient-to-br from-brand-50 to-brand-100 flex items-center justify-center p-12 min-h-[360px]">
              <img
                src={product.image_url}
                alt={product.name}
                className="max-w-full max-h-80 object-contain drop-shadow-lg"
              />
            </div>

            {/* Info panel */}
            <div className="p-10 flex flex-col gap-6 border-l border-brand-50">
              {/* Brand + name */}
              <div>
                <p className="text-[10px] font-bold uppercase tracking-[0.25em] text-gold-500 mb-1">
                  {product.brand}
                </p>
                <h1 className="text-3xl font-bold text-brand-900 leading-tight">
                  {product.name}
                </h1>
                <p className="text-4xl font-bold text-brand-900 mt-4">
                  <span className="text-gold-500 text-2xl font-semibold mr-1">$</span>
                  {product.price.toFixed(2)}
                </p>
              </div>

              {/* Attributes */}
              <div className="flex flex-wrap gap-2">
                <span className="px-3 py-1.5 rounded-full text-xs font-bold uppercase tracking-wide bg-brand-50 text-brand-700 border border-brand-100">
                  {product.shape}
                </span>
                <span className="px-3 py-1.5 rounded-full text-xs font-bold uppercase tracking-wide bg-brand-50 text-brand-700 border border-brand-100 flex items-center gap-1.5">
                  <span
                    className="w-3 h-3 rounded-full border border-brand-200 inline-block"
                    style={{ backgroundColor: product.color }}
                  />
                  {product.color}
                </span>
              </div>

              {/* Divider */}
              <div className="border-t border-brand-50" />

              {/* Description */}
              {product.description && (
                <p className="text-brand-500 leading-relaxed text-sm">{product.description}</p>
              )}

              {/* Features */}
              <ul className="space-y-2">
                {['Lightweight premium frame', 'UV400 lens protection', 'AI virtual try-on included'].map((f) => (
                  <li key={f} className="flex items-center gap-2.5 text-sm text-brand-600">
                    <span className="w-4 h-4 rounded-full bg-gold-100 flex items-center justify-center shrink-0">
                      <svg className="w-2.5 h-2.5 text-gold-500" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </span>
                    {f}
                  </li>
                ))}
              </ul>

              {/* CTA */}
              <div className="flex flex-col sm:flex-row gap-3 mt-auto pt-2">
                <Link to={`/try-on/${product.id}`} className="flex-1">
                  <Button size="lg" className="w-full">
                    ✨ Virtual Try-On
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
