import { useState, useEffect, useCallback } from 'react';
import type { Restaurant, Stats } from './types';
import { fetchRestaurants, fetchStats } from './api';
import { SearchBar } from './components/SearchBar';
import { FilterBar } from './components/FilterBar';
import { RestaurantCard } from './components/RestaurantCard';
import { GracesList } from './components/GracesList';

type View = 'restaurants' | 'graces-list';
type VisitedFilter = 'all' | 'visited' | 'not_visited';

function App() {
  const [view, setView] = useState<View>('restaurants');
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [allRestaurants, setAllRestaurants] = useState<Restaurant[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);

  const [selectedDate, setSelectedDate] = useState(() => {
    return new Date().toISOString().split('T')[0];
  });
  const [partySize, setPartySize] = useState(2);

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedNeighborhoods, setSelectedNeighborhoods] = useState<string[]>([]);
  const [selectedCuisines, setSelectedCuisines] = useState<string[]>([]);
  const [visitedFilter, setVisitedFilter] = useState<VisitedFilter>('all');

  const loadRestaurants = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetchRestaurants({
        query: searchQuery || undefined,
        page: 1,
        per_page: 1000,
      });

      setAllRestaurants(response.items);
      let filteredItems = response.items;

      if (selectedNeighborhoods.length > 0) {
        filteredItems = filteredItems.filter(r =>
          r.neighborhood && selectedNeighborhoods.includes(r.neighborhood)
        );
      }
      if (selectedCuisines.length > 0) {
        filteredItems = filteredItems.filter(r =>
          r.cuisine_type && selectedCuisines.includes(r.cuisine_type)
        );
      }
      if (visitedFilter === 'visited') {
        filteredItems = filteredItems.filter(r => r.visited);
      } else if (visitedFilter === 'not_visited') {
        filteredItems = filteredItems.filter(r => !r.visited);
      }

      setRestaurants(filteredItems);
      setTotal(filteredItems.length);
      setError(null);
    } catch (err) {
      setError('Failed to load restaurants. Make sure the backend is running.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [searchQuery, selectedNeighborhoods, selectedCuisines, visitedFilter]);

  const loadStats = useCallback(async () => {
    try {
      const data = await fetchStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  }, []);

  useEffect(() => {
    loadRestaurants();
  }, [loadRestaurants]);

  useEffect(() => {
    loadStats();
  }, [loadStats]);

  const handleNeighborhoodToggle = useCallback((neighborhood: string) => {
    setSelectedNeighborhoods(prev =>
      prev.includes(neighborhood)
        ? prev.filter(n => n !== neighborhood)
        : [...prev, neighborhood]
    );
  }, []);

  const handleCuisineToggle = useCallback((cuisine: string) => {
    setSelectedCuisines(prev =>
      prev.includes(cuisine)
        ? prev.filter(c => c !== cuisine)
        : [...prev, cuisine]
    );
  }, []);

  const clearFilters = useCallback(() => {
    setSelectedNeighborhoods([]);
    setSelectedCuisines([]);
    setVisitedFilter('all');
  }, []);

  const handleRestaurantUpdated = useCallback((updated: Restaurant) => {
    setAllRestaurants(prev => prev.map(r => r.id === updated.id ? updated : r));
    setRestaurants(prev => prev.map(r => r.id === updated.id ? updated : r));
    loadStats();
  }, [loadStats]);

  const hasFilters = selectedNeighborhoods.length > 0 || selectedCuisines.length > 0 || visitedFilter !== 'all';

  return (
    <div className="min-h-screen bg-cream">
      <header className="pattern-header h-32 md:h-40 relative">
        <div className="relative h-full flex items-center justify-center">
          <div className="text-center bg-white/90 px-8 py-4">
            <h1 className="text-3xl md:text-4xl font-display font-medium tracking-wide text-charcoal">
              Grace's Gourmet Guide
            </h1>
            <p className="text-stone text-sm mt-1 tracking-widest uppercase font-light">
              New York City
            </p>
          </div>
        </div>
      </header>

      {/* Navigation tabs */}
      <nav className="border-b border-sand bg-white sticky top-0 z-30">
        <div className="max-w-5xl mx-auto px-6 flex">
          {([
            ['restaurants', 'All Restaurants'],
            ['graces-list', "Grace's List"],
          ] as [View, string][]).map(([v, label]) => (
            <button
              key={v}
              onClick={() => setView(v)}
              className={`px-5 py-3.5 text-xs uppercase tracking-widest transition-colors relative ${
                view === v
                  ? 'text-charcoal'
                  : 'text-stone hover:text-charcoal'
              }`}
            >
              {label}
              {v === 'graces-list' && stats && (
                <span className="ml-2 text-stone/50">{stats.visited}/{stats.total_restaurants}</span>
              )}
              {view === v && (
                <span className="absolute bottom-0 left-0 right-0 h-px bg-charcoal" />
              )}
            </button>
          ))}
        </div>
      </nav>

      <main className="max-w-5xl mx-auto px-6 py-12">
        {view === 'restaurants' && (
          <>
            <div className="mb-8">
              <SearchBar
                value={searchQuery}
                onChange={setSearchQuery}
                placeholder="Search restaurants..."
              />
            </div>

            {/* Reservation Details */}
            <div className="bg-white border border-sand/60 p-6 mb-8">
              <p className="text-xs text-stone uppercase tracking-wider mb-4">Reservation Details</p>
              <div className="flex flex-wrap items-center gap-6">
                <div className="flex items-center gap-3">
                  <label className="text-sm text-charcoal">Date</label>
                  <input
                    type="date"
                    value={selectedDate}
                    onChange={(e) => setSelectedDate(e.target.value)}
                    min={new Date().toISOString().split('T')[0]}
                    className="px-3 py-2 border border-sand bg-transparent text-charcoal text-sm
                             focus:outline-none focus:border-charcoal transition-colors"
                  />
                </div>
                <div className="flex items-center gap-3">
                  <label className="text-sm text-charcoal">Party Size</label>
                  <select
                    value={partySize}
                    onChange={(e) => setPartySize(Number(e.target.value))}
                    className="px-3 py-2 border border-sand bg-transparent text-charcoal text-sm
                             focus:outline-none focus:border-charcoal transition-colors"
                  >
                    {[1, 2, 3, 4, 5, 6, 7, 8].map(n => (
                      <option key={n} value={n}>{n} {n === 1 ? 'guest' : 'guests'}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* Filters */}
            {stats && (
              <FilterBar
                neighborhoods={stats.neighborhoods}
                cuisineTypes={stats.cuisine_types}
                selectedNeighborhoods={selectedNeighborhoods}
                selectedCuisines={selectedCuisines}
                visitedFilter={visitedFilter}
                onNeighborhoodToggle={handleNeighborhoodToggle}
                onCuisineToggle={handleCuisineToggle}
                onVisitedFilterChange={setVisitedFilter}
                onClearFilters={clearFilters}
              />
            )}

            {!loading && (
              <p className="text-xs text-stone mb-6 tracking-wide uppercase">
                {total} results {hasFilters || searchQuery ? '(filtered)' : ''}
              </p>
            )}

            {error && (
              <div className="border border-stone/20 p-8 text-center mb-8">
                <p className="text-stone text-sm">{error}</p>
                <button
                  onClick={() => { setError(null); loadRestaurants(); }}
                  className="mt-4 text-sm text-charcoal underline underline-offset-4 hover:no-underline"
                >
                  Try again
                </button>
              </div>
            )}

            {loading && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[...Array(12)].map((_, i) => (
                  <div key={i} className="animate-pulse">
                    <div className="h-5 bg-sand/50 w-3/4 mb-3" />
                    <div className="h-4 bg-sand/30 w-1/2 mb-6" />
                    <div className="h-px bg-sand w-full mb-4" />
                    <div className="flex gap-4">
                      <div className="h-4 bg-sand/30 w-12" />
                      <div className="h-4 bg-sand/30 w-16" />
                    </div>
                  </div>
                ))}
              </div>
            )}

            {!loading && !error && (
              restaurants.length === 0 ? (
                <div className="text-center py-20">
                  <p className="text-stone text-sm">No restaurants found</p>
                  <p className="text-stone/60 text-xs mt-2">Try adjusting your filters</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                  {restaurants.map((restaurant) => (
                    <RestaurantCard
                      key={restaurant.id}
                      restaurant={restaurant}
                      selectedDate={selectedDate}
                      partySize={partySize}
                    />
                  ))}
                </div>
              )
            )}
          </>
        )}

        {view === 'graces-list' && (
          <GracesList
            restaurants={allRestaurants}
            onRestaurantUpdated={handleRestaurantUpdated}
          />
        )}
      </main>

      <footer className="border-t border-sand py-8 mt-16">
        <div className="max-w-5xl mx-auto px-6 text-center">
          <p className="text-xs text-stone tracking-widest uppercase">
            Grace's Gourmet Guide
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
