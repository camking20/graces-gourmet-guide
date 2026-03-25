import { useState, useMemo, useCallback } from 'react';
import type { Restaurant } from '../types';
import { toggleVisited } from '../api';

interface GracesListProps {
  restaurants: Restaurant[];
  onRestaurantUpdated: (updated: Restaurant) => void;
}

type VisitedFilter = 'all' | 'visited' | 'not_visited';

export function GracesList({ restaurants, onRestaurantUpdated }: GracesListProps) {
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<VisitedFilter>('all');
  const [togglingId, setTogglingId] = useState<number | null>(null);

  const visitedCount = useMemo(() => restaurants.filter(r => r.visited).length, [restaurants]);
  const totalCount = restaurants.length;
  const pct = totalCount > 0 ? Math.round((visitedCount / totalCount) * 100) : 0;

  const filtered = useMemo(() => {
    let items = [...restaurants];

    if (search) {
      const q = search.toLowerCase();
      items = items.filter(r =>
        r.name.toLowerCase().includes(q) ||
        (r.neighborhood && r.neighborhood.toLowerCase().includes(q)) ||
        (r.cuisine_type && r.cuisine_type.toLowerCase().includes(q)) ||
        (r.notes && r.notes.toLowerCase().includes(q))
      );
    }

    if (filter === 'visited') items = items.filter(r => r.visited);
    if (filter === 'not_visited') items = items.filter(r => !r.visited);

    items.sort((a, b) => {
      if (a.visited !== b.visited) return a.visited ? 1 : -1;
      return a.name.localeCompare(b.name);
    });

    return items;
  }, [restaurants, search, filter]);

  const handleToggle = useCallback(async (id: number) => {
    setTogglingId(id);
    try {
      const updated = await toggleVisited(id);
      onRestaurantUpdated(updated);
    } catch (err) {
      console.error('Failed to toggle visited:', err);
    } finally {
      setTogglingId(null);
    }
  }, [onRestaurantUpdated]);

  return (
    <div>
      {/* Progress section */}
      <div className="bg-white border border-sand/60 p-6 mb-8">
        <div className="flex items-baseline justify-between mb-3">
          <p className="text-xs text-stone uppercase tracking-wider">Grace's Progress</p>
          <p className="text-sm text-charcoal">
            <span className="font-display text-2xl font-medium">{visitedCount}</span>
            <span className="text-stone mx-1">/</span>
            <span className="text-stone">{totalCount}</span>
            <span className="text-stone text-xs ml-2">({pct}%)</span>
          </p>
        </div>
        <div className="w-full h-1.5 bg-sand/50 overflow-hidden">
          <div
            className="h-full bg-charcoal transition-all duration-500 ease-out"
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>

      {/* Search and filter */}
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <div className="relative flex-1">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search the list..."
            className="w-full px-0 py-3 text-sm bg-transparent border-b border-sand
                       focus:outline-none focus:border-charcoal placeholder:text-stone/50 transition-colors"
          />
          {search && (
            <button
              onClick={() => setSearch('')}
              className="absolute right-0 top-1/2 -translate-y-1/2 text-stone hover:text-charcoal text-xs"
            >
              Clear
            </button>
          )}
        </div>

        <div className="flex gap-2">
          {([
            ['all', 'All'],
            ['not_visited', 'To Visit'],
            ['visited', 'Visited'],
          ] as [VisitedFilter, string][]).map(([value, label]) => (
            <button
              key={value}
              onClick={() => setFilter(value)}
              className={`px-4 py-2 text-xs uppercase tracking-wider border transition-colors ${
                filter === value
                  ? 'border-charcoal bg-charcoal text-white'
                  : 'border-sand bg-white text-charcoal hover:border-charcoal'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Results count */}
      <p className="text-xs text-stone mb-4 tracking-wide uppercase">
        {filtered.length} {filtered.length === 1 ? 'restaurant' : 'restaurants'}
        {filter !== 'all' || search ? ' (filtered)' : ''}
      </p>

      {/* Checklist */}
      <div className="border border-sand/60 bg-white divide-y divide-sand/40">
        {filtered.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-stone text-sm">No restaurants found</p>
          </div>
        ) : (
          filtered.map((r) => (
            <div
              key={r.id}
              className={`flex items-center gap-4 px-5 py-3.5 hover:bg-cream/50 transition-colors ${
                r.visited ? 'opacity-60' : ''
              }`}
            >
              <button
                onClick={() => handleToggle(r.id)}
                disabled={togglingId === r.id}
                className="flex-shrink-0 w-5 h-5 border border-stone/30 flex items-center justify-center
                           hover:border-charcoal transition-colors disabled:opacity-50"
              >
                {togglingId === r.id ? (
                  <div className="w-3 h-3 border border-stone/30 border-t-charcoal rounded-full animate-spin" />
                ) : r.visited ? (
                  <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M2 6l3 3 5-5.5" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                ) : null}
              </button>

              <div className="flex-1 min-w-0">
                <p className={`text-sm ${r.visited ? 'line-through text-stone' : 'text-charcoal'}`}>
                  {r.name}
                </p>
              </div>

              <div className="hidden sm:flex items-center gap-3 text-xs text-stone/70 flex-shrink-0">
                {r.neighborhood && <span>{r.neighborhood}</span>}
                {r.cuisine_type && <span>{r.cuisine_type}</span>}
              </div>

              {r.notes && (
                <span className="hidden md:block text-[11px] text-stone/50 italic max-w-48 truncate flex-shrink-0">
                  {r.notes}
                </span>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
