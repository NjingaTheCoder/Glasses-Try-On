import { useState } from 'react'
import { Navbar } from '@/components/layout/Navbar'
import { FilterSidebar } from '@/components/catalog/FilterSidebar'
import { ProductCard } from '@/components/catalog/ProductCard'
import { ProductCardSkeleton } from '@/components/ui/Skeleton'
import { Button } from '@/components/ui/Button'
import { useProducts } from '@/hooks/useProducts'
import type { ProductFilters } from '@/types/product'

export default function CatalogPage() {
  const [filters, setFilters] = useState<ProductFilters>({})
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false)
  const { products, total, loading, error } = useProducts(filters)

  const activeCount = Object.values(filters).filter(
    (v) => v !== undefined && v !== '' && v !== null,
  ).length

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#fafaf8' }}>
      <Navbar />

      {/* Hero banner */}
      <div className="bg-brand-900 relative overflow-hidden">
        <div className="absolute inset-0 opacity-10"
          style={{
            backgroundImage: 'radial-gradient(circle at 20% 50%, #d4911f 0%, transparent 60%), radial-gradient(circle at 80% 20%, #3d65c4 0%, transparent 50%)',
          }}
        />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-14">
          <p className="text-gold-300 text-xs font-semibold tracking-[0.3em] uppercase mb-3">
            Humaine Optical — 2025 Collection
          </p>
          <h1 className="text-4xl sm:text-5xl font-bold text-white leading-tight text-balance">
            Find Your Perfect Pair
          </h1>
          <p className="text-brand-200 mt-3 text-base max-w-xl leading-relaxed">
            Premium eyewear curated for every style. Try any frame on instantly with our AI-powered virtual try-on.
          </p>
          <div className="mt-6 flex flex-wrap gap-2">
            {['Round', 'Square', 'Aviator', 'Cat-Eye', 'Oval', 'Rectangle'].map((shape) => (
              <button
                key={shape}
                onClick={() => setFilters((f) => ({ ...f, shape: shape.toLowerCase() as any }))}
                className="px-4 py-1.5 rounded-full text-xs font-semibold border border-brand-700 text-brand-200 hover:border-gold-400 hover:text-gold-300 transition-colors"
              >
                {shape}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* Toolbar */}
        <div className="mb-6 flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-3">
            {!loading && !error && (
              <p className="text-sm text-brand-400 font-medium">
                <span className="text-brand-800 font-bold">{total}</span>{' '}
                {total === 1 ? 'frame' : 'frames'} available
              </p>
            )}
            {activeCount > 0 && (
              <button
                className="text-xs text-gold-500 hover:text-gold-600 font-semibold underline underline-offset-2"
                onClick={() => setFilters({})}
              >
                Clear filters ({activeCount})
              </button>
            )}
          </div>

          {/* Mobile filter toggle */}
          <button
            className="lg:hidden flex items-center gap-2 px-4 py-2 bg-white border border-brand-200 rounded-xl text-sm font-semibold text-brand-700 shadow-card"
            onClick={() => setMobileFiltersOpen((v) => !v)}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 4h18M7 12h10M11 20h2" />
            </svg>
            Filters
            {activeCount > 0 && (
              <span className="inline-flex items-center justify-center w-4 h-4 text-[10px] font-bold bg-gold-400 text-white rounded-full">
                {activeCount}
              </span>
            )}
          </button>
        </div>

        {/* Mobile filter drawer */}
        {mobileFiltersOpen && (
          <div className="lg:hidden mb-6 bg-white rounded-2xl border border-brand-100 shadow-card p-5">
            <FilterSidebar filters={filters} onChange={(f) => setFilters(f)} />
            <div className="mt-4 flex justify-end">
              <Button size="sm" variant="secondary" onClick={() => setMobileFiltersOpen(false)}>
                Apply & close
              </Button>
            </div>
          </div>
        )}

        <div className="flex flex-col lg:flex-row gap-10">
          {/* Desktop sidebar */}
          <div className="hidden lg:block">
            <FilterSidebar filters={filters} onChange={setFilters} />
          </div>

          {/* Grid */}
          <main className="flex-1 min-w-0">
            {loading && (
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
                {Array.from({ length: 6 }).map((_, i) => <ProductCardSkeleton key={i} />)}
              </div>
            )}

            {!loading && error && (
              <div className="text-center py-24">
                <div className="w-14 h-14 rounded-2xl bg-red-50 flex items-center justify-center mx-auto mb-4">
                  <svg className="w-7 h-7 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.5">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                  </svg>
                </div>
                <p className="text-brand-600 font-semibold">{error}</p>
              </div>
            )}

            {!loading && !error && products.length === 0 && (
              <div className="text-center py-24">
                <div className="w-14 h-14 rounded-2xl bg-brand-50 flex items-center justify-center mx-auto mb-4">
                  <svg className="w-7 h-7 text-brand-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="1.5">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
                  </svg>
                </div>
                <p className="text-brand-700 font-semibold text-lg">No frames match your filters</p>
                <p className="text-brand-400 text-sm mt-1">Try adjusting your search criteria</p>
                <button
                  className="mt-4 text-sm text-gold-500 hover:text-gold-600 font-semibold underline underline-offset-2"
                  onClick={() => setFilters({})}
                >
                  Clear all filters
                </button>
              </div>
            )}

            {!loading && !error && products.length > 0 && (
              <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-6">
                {products.map((p) => <ProductCard key={p.id} product={p} />)}
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  )
}
