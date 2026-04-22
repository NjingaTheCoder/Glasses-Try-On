import { cn } from '@/lib/cn'
import { useProducts } from '@/hooks/useProducts'
import { Skeleton } from '@/components/ui/Skeleton'
import type { Product } from '@/types/product'

interface Props {
  selected: Product | null
  onSelect: (product: Product) => void
}

export function GlassesSidebar({ selected, onSelect }: Props) {
  const { products, loading } = useProducts()

  return (
    <div className="flex flex-col h-full">
      <div className="mb-4 pb-3 border-b border-brand-100">
        <h2 className="font-bold text-brand-900 text-sm uppercase tracking-widest">Select Frame</h2>
        {!loading && (
          <p className="text-xs text-brand-400 mt-0.5">{products.length} styles available</p>
        )}
      </div>

      <ul className="flex-1 overflow-y-auto space-y-1 scrollbar-hide">
        {loading
          ? Array.from({ length: 6 }).map((_, i) => (
              <li key={i}>
                <div className="flex items-center gap-3 px-2 py-2">
                  <Skeleton className="w-14 h-10 rounded-lg shrink-0" />
                  <div className="flex-1 space-y-1.5">
                    <Skeleton className="h-2 w-14" />
                    <Skeleton className="h-3 w-22" />
                  </div>
                </div>
              </li>
            ))
          : products.map((p) => (
              <li key={p.id}>
                <button
                  type="button"
                  onClick={() => onSelect(p)}
                  className={cn(
                    'w-full text-left flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all',
                    selected?.id === p.id
                      ? 'bg-brand-900 ring-1 ring-brand-700'
                      : 'hover:bg-brand-50',
                  )}
                >
                  <div className={cn(
                    'w-14 h-10 rounded-lg overflow-hidden shrink-0 flex items-center justify-center border',
                    selected?.id === p.id
                      ? 'bg-brand-800 border-brand-700'
                      : 'bg-brand-50 border-brand-100',
                  )}>
                    <img
                      src={p.image_url}
                      alt={p.name}
                      className="w-full h-full object-contain p-1"
                      loading="lazy"
                    />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className={cn(
                      'text-[10px] font-bold uppercase tracking-widest truncate',
                      selected?.id === p.id ? 'text-gold-400' : 'text-brand-400',
                    )}>
                      {p.brand}
                    </p>
                    <p className={cn(
                      'text-sm font-semibold truncate leading-snug',
                      selected?.id === p.id ? 'text-white' : 'text-brand-900',
                    )}>
                      {p.name}
                    </p>
                    <p className={cn(
                      'text-xs',
                      selected?.id === p.id ? 'text-brand-300' : 'text-brand-400',
                    )}>
                      ${p.price.toFixed(2)}
                    </p>
                  </div>
                  {selected?.id === p.id && (
                    <span className="ml-auto shrink-0 w-5 h-5 rounded-full bg-gold-400 flex items-center justify-center">
                      <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </span>
                  )}
                </button>
              </li>
            ))}
      </ul>
    </div>
  )
}
