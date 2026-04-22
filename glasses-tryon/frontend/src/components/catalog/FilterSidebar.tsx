import { type ChangeEvent, useState, useEffect } from 'react'
import { Input } from '@/components/ui/Input'
import { Select } from '@/components/ui/Select'
import { Button } from '@/components/ui/Button'
import { useDebounce } from '@/hooks/useDebounce'
import type { GlassesShape, ProductFilters } from '@/types/product'

const SHAPES: GlassesShape[] = ['round', 'square', 'aviator', 'cat-eye', 'oval', 'rectangle']

interface Props {
  filters: ProductFilters
  onChange: (filters: ProductFilters) => void
}

export function FilterSidebar({ filters, onChange }: Props) {
  // Local state for search so we can debounce without blocking the input
  const [searchInput, setSearchInput] = useState(filters.q ?? '')
  const debouncedSearch = useDebounce(searchInput, 350)

  useEffect(() => {
    onChange({ ...filters, q: debouncedSearch || undefined })
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedSearch])

  // Keep local search in sync when filters are cleared externally
  useEffect(() => {
    if (!filters.q) setSearchInput('')
  }, [filters.q])

  function set<K extends keyof ProductFilters>(key: K, value: ProductFilters[K]) {
    onChange({ ...filters, [key]: value || undefined })
  }

  function clearAll() {
    setSearchInput('')
    onChange({})
  }

  const activeCount = Object.values(filters).filter(
    (v) => v !== undefined && v !== '' && v !== null,
  ).length

  return (
    <aside className="w-full lg:w-64 shrink-0 space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
          Filters
        </h2>
        {activeCount > 0 && (
          <span className="inline-flex items-center justify-center w-5 h-5 text-xs font-bold bg-brand-500 text-white rounded-full">
            {activeCount}
          </span>
        )}
      </div>

      <Input
        label="Search"
        placeholder="Name or brand…"
        value={searchInput}
        onChange={(e: ChangeEvent<HTMLInputElement>) => setSearchInput(e.target.value)}
      />

      <Select
        label="Shape"
        value={filters.shape ?? ''}
        onChange={(e: ChangeEvent<HTMLSelectElement>) =>
          set('shape', e.target.value as GlassesShape)
        }
      >
        <option value="">All shapes</option>
        {SHAPES.map((s) => (
          <option key={s} value={s} className="capitalize">
            {s}
          </option>
        ))}
      </Select>

      <Input
        label="Color"
        placeholder="e.g. black, gold…"
        value={filters.color ?? ''}
        onChange={(e: ChangeEvent<HTMLInputElement>) => set('color', e.target.value)}
      />

      <div className="grid grid-cols-2 gap-2">
        <Input
          label="Min $"
          type="number"
          min={0}
          placeholder="0"
          value={filters.min_price ?? ''}
          onChange={(e: ChangeEvent<HTMLInputElement>) =>
            set('min_price', e.target.value ? Number(e.target.value) : undefined)
          }
        />
        <Input
          label="Max $"
          type="number"
          min={0}
          placeholder="999"
          value={filters.max_price ?? ''}
          onChange={(e: ChangeEvent<HTMLInputElement>) =>
            set('max_price', e.target.value ? Number(e.target.value) : undefined)
          }
        />
      </div>

      {activeCount > 0 && (
        <Button variant="ghost" size="sm" className="w-full text-gray-400" onClick={clearAll}>
          ✕ Clear all filters
        </Button>
      )}
    </aside>
  )
}
