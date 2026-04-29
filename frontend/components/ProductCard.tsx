'use client'

import { Star, Package } from 'lucide-react'

interface Product {
  sku: string
  name: string
  brand: string
  category: string
  price: number
  rating: number
  in_stock: boolean
  description: string
}

export default function ProductCard({ product }: { product: Product }) {
  const stars = Math.round(product.rating)

  return (
    <div className="card-lift bg-[#111] border border-white/8 rounded p-4 flex flex-col gap-3 hover:border-[#76b900]/25 transition-all">
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-[10px] font-mono text-[#76b900]/60 tracking-widest mb-0.5">
            {product.brand.toUpperCase()} · {product.sku}
          </p>
          <h3 className="text-sm font-mono font-bold text-white leading-snug">
            {product.name}
          </h3>
        </div>
        <span className={`flex-shrink-0 text-[10px] font-mono px-1.5 py-0.5 rounded border ${
          product.in_stock
            ? 'border-[#76b900]/30 text-[#76b900]/70 bg-[#76b900]/5'
            : 'border-red-800/40 text-red-400/60 bg-red-900/5'
        }`}>
          {product.in_stock ? 'IN STOCK' : 'OOS'}
        </span>
      </div>

      {/* Description */}
      <p className="text-xs font-mono text-white/40 leading-relaxed line-clamp-3">
        {product.description}
      </p>

      {/* Footer */}
      <div className="flex items-center justify-between mt-auto pt-2 border-t border-white/5">
        <div className="flex items-center gap-0.5">
          {Array.from({ length: 5 }).map((_, i) => (
            <Star
              key={i}
              size={10}
              className={i < stars ? 'text-[#76b900] fill-[#76b900]' : 'text-white/15'}
            />
          ))}
          <span className="text-[10px] font-mono text-white/30 ml-1">{product.rating}</span>
        </div>
        <span className="font-mono text-white font-bold text-sm">
          {product.price === 0
            ? 'Subscription'
            : `$${product.price.toLocaleString('en-US', { minimumFractionDigits: 2 })}`}
        </span>
      </div>

      {/* Category pill */}
      <div className="flex items-center gap-1">
        <Package size={9} className="text-white/20" />
        <span className="text-[10px] font-mono text-white/25 capitalize">{product.category}</span>
      </div>
    </div>
  )
}
