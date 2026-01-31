import type { Restaurant } from '../types';

interface RestaurantCardProps {
  restaurant: Restaurant;
}

export function RestaurantCard({ restaurant }: RestaurantCardProps) {
  return (
    <div className="bg-white border border-sand/60 p-6 hover:border-stone/30 transition-colors">
      <h3 className="text-lg font-display font-medium text-charcoal mb-2">
        {restaurant.name}
      </h3>
      
      <div className="flex items-center gap-3 text-xs text-stone mb-4">
        {restaurant.neighborhood && (
          <span>{restaurant.neighborhood}</span>
        )}
        {restaurant.neighborhood && restaurant.cuisine_type && (
          <span className="text-stone/40">·</span>
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
        {restaurant.booking_urls.resy && (
          <a
            href={restaurant.booking_urls.resy}
            target="_blank"
            rel="noopener noreferrer"
            className="text-charcoal hover:opacity-60 transition-opacity underline underline-offset-4"
          >
            Resy
          </a>
        )}
        
        {restaurant.booking_urls.opentable && (
          <a
            href={restaurant.booking_urls.opentable}
            target="_blank"
            rel="noopener noreferrer"
            className="text-charcoal hover:opacity-60 transition-opacity underline underline-offset-4"
          >
            OpenTable
          </a>
        )}
        
        {restaurant.booking_urls.google && (
          <a
            href={restaurant.booking_urls.google}
            target="_blank"
            rel="noopener noreferrer"
            className="text-stone hover:opacity-60 transition-opacity underline underline-offset-4"
          >
            Google
          </a>
        )}
      </div>
    </div>
  );
}
