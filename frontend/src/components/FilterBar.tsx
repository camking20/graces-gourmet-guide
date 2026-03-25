import { useState } from 'react';

type VisitedFilter = 'all' | 'visited' | 'not_visited';

interface FilterBarProps {
  neighborhoods: string[];
  cuisineTypes: string[];
  selectedNeighborhoods: string[];
  selectedCuisines: string[];
  visitedFilter: VisitedFilter;
  onNeighborhoodToggle: (neighborhood: string) => void;
  onCuisineToggle: (cuisine: string) => void;
  onVisitedFilterChange: (filter: VisitedFilter) => void;
  onClearFilters: () => void;
}

export function FilterBar({
  neighborhoods,
  cuisineTypes,
  selectedNeighborhoods,
  selectedCuisines,
  visitedFilter,
  onNeighborhoodToggle,
  onCuisineToggle,
  onVisitedFilterChange,
  onClearFilters,
}: FilterBarProps) {
  const [showNeighborhoods, setShowNeighborhoods] = useState(false);
  const [showCuisines, setShowCuisines] = useState(false);

  const hasFilters = selectedNeighborhoods.length > 0 || selectedCuisines.length > 0 || visitedFilter !== 'all';

  return (
    <div className="mb-8 space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        {/* Neighborhood Filter */}
        <div className="relative">
          <button
            onClick={() => {
              setShowNeighborhoods(!showNeighborhoods);
              setShowCuisines(false);
            }}
            className={`px-4 py-2 border text-sm transition-colors ${
              selectedNeighborhoods.length > 0
                ? 'border-charcoal bg-charcoal text-white'
                : 'border-sand bg-white text-charcoal hover:border-charcoal'
            }`}
          >
            Neighborhood {selectedNeighborhoods.length > 0 && `(${selectedNeighborhoods.length})`}
          </button>

          {showNeighborhoods && (
            <div className="absolute top-full left-0 mt-2 w-64 max-h-80 overflow-y-auto bg-white border border-sand shadow-lg z-50">
              <div className="p-2">
                {neighborhoods.map((neighborhood) => (
                  <label
                    key={neighborhood}
                    className="flex items-center gap-2 px-3 py-2 hover:bg-cream cursor-pointer text-sm"
                  >
                    <input
                      type="checkbox"
                      checked={selectedNeighborhoods.includes(neighborhood)}
                      onChange={() => onNeighborhoodToggle(neighborhood)}
                      className="w-4 h-4 accent-charcoal"
                    />
                    <span className="text-charcoal">{neighborhood}</span>
                  </label>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Cuisine Filter */}
        <div className="relative">
          <button
            onClick={() => {
              setShowCuisines(!showCuisines);
              setShowNeighborhoods(false);
            }}
            className={`px-4 py-2 border text-sm transition-colors ${
              selectedCuisines.length > 0
                ? 'border-charcoal bg-charcoal text-white'
                : 'border-sand bg-white text-charcoal hover:border-charcoal'
            }`}
          >
            Cuisine {selectedCuisines.length > 0 && `(${selectedCuisines.length})`}
          </button>

          {showCuisines && (
            <div className="absolute top-full left-0 mt-2 w-64 max-h-80 overflow-y-auto bg-white border border-sand shadow-lg z-50">
              <div className="p-2">
                {cuisineTypes.map((cuisine) => (
                  <label
                    key={cuisine}
                    className="flex items-center gap-2 px-3 py-2 hover:bg-cream cursor-pointer text-sm"
                  >
                    <input
                      type="checkbox"
                      checked={selectedCuisines.includes(cuisine)}
                      onChange={() => onCuisineToggle(cuisine)}
                      className="w-4 h-4 accent-charcoal"
                    />
                    <span className="text-charcoal">{cuisine}</span>
                  </label>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Visited Filter */}
        <div className="flex border border-sand divide-x divide-sand">
          {([
            ['all', 'All'],
            ['visited', 'Visited'],
            ['not_visited', 'To Visit'],
          ] as [VisitedFilter, string][]).map(([value, label]) => (
            <button
              key={value}
              onClick={() => onVisitedFilterChange(value)}
              className={`px-3 py-1.5 text-sm transition-colors ${
                visitedFilter === value
                  ? 'bg-charcoal text-white'
                  : 'bg-white text-charcoal hover:bg-cream'
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        {hasFilters && (
          <button
            onClick={onClearFilters}
            className="px-4 py-2 text-sm text-stone hover:text-charcoal underline underline-offset-4"
          >
            Clear all
          </button>
        )}
      </div>

      {/* Selected Filter Tags */}
      {(selectedNeighborhoods.length > 0 || selectedCuisines.length > 0) && (
        <div className="flex flex-wrap gap-2">
          {selectedNeighborhoods.map((n) => (
            <span
              key={n}
              className="inline-flex items-center gap-1 px-3 py-1 bg-charcoal/10 text-charcoal text-xs"
            >
              {n}
              <button
                onClick={() => onNeighborhoodToggle(n)}
                className="ml-1 hover:text-charcoal/60"
              >
                &times;
              </button>
            </span>
          ))}
          {selectedCuisines.map((c) => (
            <span
              key={c}
              className="inline-flex items-center gap-1 px-3 py-1 bg-charcoal/10 text-charcoal text-xs"
            >
              {c}
              <button
                onClick={() => onCuisineToggle(c)}
                className="ml-1 hover:text-charcoal/60"
              >
                &times;
              </button>
            </span>
          ))}
        </div>
      )}

      {(showNeighborhoods || showCuisines) && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => {
            setShowNeighborhoods(false);
            setShowCuisines(false);
          }}
        />
      )}
    </div>
  );
}
