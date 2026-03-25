import type { Restaurant } from '../types';

interface RestaurantCardProps {
  restaurant: Restaurant;
  selectedDate: string;
  partySize: number;
}

function extractResySlug(url: string): string | null {
  const match = url.match(/resy\.com\/cities\/[^/]+\/(?:venues\/)?([^?]+)/);
  return match ? match[1] : null;
}

function buildResyUrl(restaurant: Restaurant, date: string, seats: number): string {
  if (restaurant.booking_urls?.resy) {
    const slug = extractResySlug(restaurant.booking_urls.resy);
    if (slug) {
      return `https://resy.com/cities/new-york-ny/venues/${slug}?date=${date}&seats=${seats}`;
    }
  }
  return `https://resy.com/cities/new-york-ny/search?date=${date}&seats=${seats}&query=${encodeURIComponent(restaurant.name)}`;
}

function buildOpenTableUrl(restaurant: Restaurant, date: string, covers: number): string {
  if (restaurant.booking_urls?.opentable) {
    const base = restaurant.booking_urls.opentable;
    if (base.includes('?')) {
      return `${base}&covers=${covers}&dateTime=${date}T19:00`;
    }
    return `${base}?covers=${covers}&dateTime=${date}T19:00`;
  }
  return `https://www.opentable.com/s?term=${encodeURIComponent(restaurant.name)}&metroId=8&covers=${covers}&dateTime=${date}T19:00`;
}

export function RestaurantCard({ restaurant, selectedDate, partySize }: RestaurantCardProps) {
  const resyUrl = buildResyUrl(restaurant, selectedDate, partySize);
  const opentableUrl = buildOpenTableUrl(restaurant, selectedDate, partySize);
  const googleUrl = `https://www.google.com/search?q=${encodeURIComponent(restaurant.name)}+NYC+reservations`;

  return (
    <div className="bg-white border border-sand/60 p-6 hover:border-stone/30 transition-colors relative">
      {restaurant.visited && (
        <span className="absolute top-3 right-3 flex items-center gap-1 text-[10px] text-stone/70 uppercase tracking-wider">
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-stone/50">
            <path d="M2.5 6.5l2.5 2.5 4.5-5" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          visited
        </span>
      )}

      <h3 className="text-lg font-display font-medium text-charcoal mb-2 pr-16">
        {restaurant.name}
      </h3>

      <div className="flex items-center gap-3 text-xs text-stone mb-4">
        {restaurant.neighborhood && (
          <span>{restaurant.neighborhood}</span>
        )}
        {restaurant.neighborhood && restaurant.cuisine_type && (
          <span className="text-stone/40">&middot;</span>
        )}
        {restaurant.cuisine_type && (
          <span>{restaurant.cuisine_type}</span>
        )}
      </div>

      {restaurant.notes && (
        <p className="text-xs text-stone/70 italic mb-5 leading-relaxed">
          {restaurant.notes}
        </p>
      )}

      <div className="flex items-center gap-4 text-xs pt-4 border-t border-sand/50">
        <span className="text-stone/50 uppercase tracking-wider text-[10px]">Book</span>
        <a
          href={resyUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="text-charcoal hover:opacity-60 transition-opacity underline underline-offset-4"
        >
          Resy
        </a>
        <a
          href={opentableUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="text-charcoal hover:opacity-60 transition-opacity underline underline-offset-4"
        >
          OpenTable
        </a>
        <a
          href={googleUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="text-stone hover:opacity-60 transition-opacity underline underline-offset-4"
        >
          Google
        </a>
      </div>
    </div>
  );
}
