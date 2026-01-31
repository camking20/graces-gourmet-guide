interface FilterBarProps {
  neighborhoods: string[];
  cuisineTypes: string[];
  selectedNeighborhood: string;
  selectedCuisine: string;
  onNeighborhoodChange: (value: string) => void;
  onCuisineChange: (value: string) => void;
}

export function FilterBar({
  neighborhoods,
  cuisineTypes,
  selectedNeighborhood,
  selectedCuisine,
  onNeighborhoodChange,
  onCuisineChange,
}: FilterBarProps) {
  const selectClass = `px-0 py-2 bg-transparent border-b border-sand text-sm text-charcoal
                       focus:outline-none focus:border-charcoal cursor-pointer transition-colors
                       appearance-none pr-6 bg-[url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2212%22%20height%3D%2212%22%20viewBox%3D%220%200%2012%2012%22%3E%3Cpath%20fill%3D%22%23737373%22%20d%3D%22M6%208L1%203h10z%22%2F%3E%3C%2Fsvg%3E')] bg-no-repeat bg-right`;

  return (
    <div className="flex flex-wrap items-center gap-8">
      <div className="flex items-center gap-3">
        <label className="text-xs text-stone uppercase tracking-wider">Neighborhood</label>
        <select
          value={selectedNeighborhood}
          onChange={(e) => onNeighborhoodChange(e.target.value)}
          className={selectClass}
        >
          <option value="">All</option>
          {neighborhoods.map((n) => (
            <option key={n} value={n}>{n}</option>
          ))}
        </select>
      </div>

      <div className="flex items-center gap-3">
        <label className="text-xs text-stone uppercase tracking-wider">Cuisine</label>
        <select
          value={selectedCuisine}
          onChange={(e) => onCuisineChange(e.target.value)}
          className={selectClass}
        >
          <option value="">All</option>
          {cuisineTypes.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>

      {(selectedNeighborhood || selectedCuisine) && (
        <button
          onClick={() => {
            onNeighborhoodChange('');
            onCuisineChange('');
          }}
          className="text-xs text-stone hover:text-charcoal transition-colors underline underline-offset-4"
        >
          Clear all
        </button>
      )}
    </div>
  );
}
