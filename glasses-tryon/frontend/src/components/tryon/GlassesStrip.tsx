import { cn } from '@/lib/cn'
import { useProducts } from '@/hooks/useProducts'
import { Skeleton } from '@/components/ui/Skeleton'
import type { Product } from '@/types/product'

interface Props {
  selected: Product | null
  onSelect: (product: Product) => void
}

export function GlassesStrip({ selected, onSelect }: Props) {
  const { products, loading } = useProducts()

  return (
    <div className="bg-brand-900 border-t border-brand-800">
      <div className="flex items-center gap-2 px-4 py-2 border-b border-brand-800">
        <span className="text-[10px] font-bold text-brand-400 uppercase tracking-[0.2em]">
          Select Frame
        </span>
        <span className="text-[10px] text-brand-600">· {products.length} styles</span>
      </div>

      <div className="flex overflow-x-auto scrollbar-hide gap-2 p-3">
        {loading
          ? Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="w-20 h-14 shrink-0 rounded-xl opacity-30" />
            ))
          : products.map((p) => (
              <button
                key={p.id}
                type="button"
                onClick={() => onSelect(p)}
                title={`${p.brand} ${p.name}`}
                className={cn(
                  'shrink-0 w-20 h-14 rounded-xl border-2 transition-all overflow-hidden flex items-center justify-center',
                  selected?.id === p.id
                    ? 'border-gold-400 ring-2 ring-gold-400/30 bg-brand-800'
                    : 'border-brand-700 hover:border-brand-500 bg-brand-800',
                )}
              >
                <img
                  src={p.image_url}
                  alt={p.name}
                  className="w-full h-full object-contain p-1.5"
                  loading="lazy"
                />
              </button>
            ))}
      </div>

      {selected && (
        <div className="px-4 pb-3 flex items-center justify-between">
          <p className="text-xs text-brand-400">
            <span className="font-semibold text-white">{selected.name}</span>
            <span className="mx-1 text-brand-600">·</span>
            <span className="text-gold-400">${selected.price.toFixed(2)}</span>
          </p>
        </div>
      )}
    </div>
  )
}
