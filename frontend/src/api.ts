import type { Restaurant, Stats, PaginatedResponse, WatchConfig } from './types';

const API_BASE = import.meta.env.VITE_API_BASE_URL 
  ? `${import.meta.env.VITE_API_BASE_URL}/api`
  : 'http://localhost:8000/api';

export async function fetchRestaurants(params: {
  query?: string;
  neighborhood?: string;
  cuisine_type?: string;
  visited?: boolean;
  monitor_enabled?: boolean;
  page?: number;
  per_page?: number;
}): Promise<PaginatedResponse> {
  const searchParams = new URLSearchParams();
  
  if (params.query) searchParams.set('query', params.query);
  if (params.neighborhood) searchParams.set('neighborhood', params.neighborhood);
  if (params.cuisine_type) searchParams.set('cuisine_type', params.cuisine_type);
  if (params.visited !== undefined) searchParams.set('visited', String(params.visited));
  if (params.monitor_enabled !== undefined) searchParams.set('monitor_enabled', String(params.monitor_enabled));
  if (params.page) searchParams.set('page', String(params.page));
  if (params.per_page) searchParams.set('per_page', String(params.per_page));
  
  const response = await fetch(`${API_BASE}/restaurants?${searchParams}`);
  if (!response.ok) throw new Error('Failed to fetch restaurants');
  return response.json();
}

export async function fetchStats(): Promise<Stats> {
  const response = await fetch(`${API_BASE}/stats`);
  if (!response.ok) throw new Error('Failed to fetch stats');
  return response.json();
}

export async function toggleVisited(id: number): Promise<Restaurant> {
  const response = await fetch(`${API_BASE}/restaurants/${id}/toggle-visited`, {
    method: 'PATCH',
  });
  if (!response.ok) throw new Error('Failed to toggle visited');
  return response.json();
}

export async function updateRestaurant(id: number, data: Partial<Restaurant>): Promise<Restaurant> {
  const response = await fetch(`${API_BASE}/restaurants/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to update restaurant');
  return response.json();
}

export async function createWatchConfig(data: {
  restaurant_id: number;
  party_size: number;
  date_range_start?: string;
  date_range_end?: string;
  preferred_times: string[];
  notify_email?: string;
}): Promise<WatchConfig> {
  const response = await fetch(`${API_BASE}/watch-configs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to create watch config');
  return response.json();
}

export async function deleteWatchConfig(id: number): Promise<void> {
  const response = await fetch(`${API_BASE}/watch-configs/${id}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete watch config');
}

export async function fetchWatchConfigs(): Promise<WatchConfig[]> {
  const response = await fetch(`${API_BASE}/watch-configs`);
  if (!response.ok) throw new Error('Failed to fetch watch configs');
  return response.json();
}

export interface AvailabilitySlot {
  time: string;
  booking_url: string;
  platform: string;
}

export interface AvailabilityResults {
  results: Record<number, AvailabilitySlot[]>;
  date: string;
  party_size: number;
}

export async function searchAvailability(params: {
  restaurant_ids: number[];
  date: string;
  time: string;
  party_size: number;
}): Promise<AvailabilityResults> {
  const response = await fetch(`${API_BASE}/availability/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });
  if (!response.ok) throw new Error('Failed to search availability');
  return response.json();
}
