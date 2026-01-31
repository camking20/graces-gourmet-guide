import { useState } from 'react';

interface FilterBarProps {
  neighborhoods: string[];
  cuisineTypes: string[];
  selectedNeighborhoods: string[];
  selectedCuisines: string[];
  onNeighborhoodToggle: (neighborhood: string) => void;
  onCuisineToggle: (cuisine: string) => void;
  onClearFilters: () => void;
}

export function FilterBar({
  neighborhoods,
  cuisineTypes,
  selectedNeighborhoods,
  selectedCuisines,
  onNeighborhoodToggle,
  onCuisineToggle,
  onClearFilters,
}: FilterBarProps) {
  const [showNeighborhoods, setShowNeighborhoods] = useState(false);
  const [showCuisines, setShowCuisines] = useState(false);

  const hasFilters = selectedNeighborhoods.length > 0 || selectedCuisines.length > 0;

  return (
    <div className="mb-8 space-y-4">
      <div className="flex flex-wrap items-center gap-4">
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

        {/* Clear Filters */}
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
      {hasFilters && (
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
                ×
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
                ×
              </button>
            </span>
          ))}
        </div>
      )}

      {/* Click outside to close */}
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
