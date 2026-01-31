export interface BookingUrls {
  resy?: string;
  opentable?: string;
  google?: string;
}

export interface Restaurant {
  id: number;
  name: string;
  visited: boolean;
  notes: string;
  neighborhood: string | null;
  cuisine_type: string | null;
  booking_urls: BookingUrls;
  monitor_enabled: boolean;
  priority: string;
  created_at: string;
  updated_at: string;
}

export interface WatchConfig {
  id: number;
  restaurant_id: number;
  party_size: number;
  date_range_start: string | null;
  date_range_end: string | null;
  preferred_times: string[];
  notify_email: string | null;
  notify_sms: string | null;
  active: boolean;
  last_checked: string | null;
  created_at: string;
}

export interface Stats {
  total_restaurants: number;
  visited: number;
  not_visited: number;
  monitored: number;
  neighborhoods: string[];
  cuisine_types: string[];
}

export interface PaginatedResponse {
  items: Restaurant[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface Filters {
  query: string;
  neighborhood: string;
  cuisine_type: string;
  visited: string;
  monitor_enabled: string;
}
