import { Link } from 'react-router-dom'
import type { Product } from '@/types/product'

interface Props {
  product: Product
}

export function ProductCard({ product }: Props) {
  return (
    <div className="group bg-white rounded-2xl overflow-hidden border border-brand-100 shadow-card hover:shadow-card-hover transition-all duration-300 flex flex-col">
      {/* Image */}
      <Link
        to={`/product/${product.id}`}
        className="block overflow-hidden bg-gradient-to-br from-brand-50 to-brand-100 aspect-[4/3] relative"
      >
        <img
          src={product.image_url}
          alt={product.name}
          className="w-full h-full object-contain p-6 group-hover:scale-105 transition-transform duration-500"
          loading="lazy"
        />
        {/* Shape badge overlay */}
        <span className="absolute top-3 left-3 px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-widest bg-white/80 backdrop-blur-sm text-brand-700 border border-brand-100">
          {product.shape}
        </span>
      </Link>

      {/* Info */}
      <div className="p-5 flex flex-col gap-3 flex-1">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-gold-500">
            {product.brand}
          </p>
          <h3 className="font-bold text-brand-900 leading-snug mt-0.5 text-base">
            {product.name}
          </h3>
        </div>

        {/* Color swatch */}
        <div className="flex items-center gap-2 text-sm text-brand-400">
          <span
            className="w-3.5 h-3.5 rounded-full border border-brand-200 shadow-sm inline-block shrink-0"
            style={{ backgroundColor: product.color }}
          />
          <span className="capitalize text-xs font-medium">{product.color}</span>
        </div>

        {/* Price + actions */}
        <div className="mt-auto pt-3 border-t border-brand-50 flex items-center justify-between gap-3">
          <span className="text-xl font-bold text-brand-900">
            ${product.price.toFixed(2)}
          </span>
          <div className="flex gap-2">
            <Link to={`/product/${product.id}`}>
              <button className="px-3 py-1.5 rounded-lg text-xs font-semibold border border-brand-200 text-brand-600 hover:bg-brand-50 transition-colors">
                Details
              </button>
            </Link>
            <Link to={`/try-on/${product.id}`}>
              <button className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-gold-400 text-white hover:bg-gold-500 transition-all shadow-sm hover:shadow-gold active:scale-95">
                Try On
              </button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
