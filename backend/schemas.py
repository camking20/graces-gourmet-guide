"""
Pydantic schemas for API request/response validation.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class BookingUrls(BaseModel):
    resy: Optional[str] = None
    opentable: Optional[str] = None
    google: Optional[str] = None


class RestaurantBase(BaseModel):
    name: str
    visited: bool = False
    notes: str = ""
    neighborhood: Optional[str] = None
    cuisine_type: Optional[str] = None
    booking_urls: BookingUrls = BookingUrls()
    monitor_enabled: bool = False
    priority: str = "normal"


class RestaurantCreate(RestaurantBase):
    pass


class RestaurantUpdate(BaseModel):
    name: Optional[str] = None
    visited: Optional[bool] = None
    notes: Optional[str] = None
    neighborhood: Optional[str] = None
    cuisine_type: Optional[str] = None
    booking_urls: Optional[BookingUrls] = None
    monitor_enabled: Optional[bool] = None
    priority: Optional[str] = None


class Restaurant(RestaurantBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WatchConfigBase(BaseModel):
    party_size: int = 2
    date_range_start: Optional[str] = None
    date_range_end: Optional[str] = None
    preferred_times: List[str] = Field(default_factory=lambda: ["18:00", "19:00", "20:00"])
    notify_email: Optional[str] = None
    notify_sms: Optional[str] = None
    active: bool = True


class WatchConfigCreate(WatchConfigBase):
    restaurant_id: int


class WatchConfigUpdate(BaseModel):
    party_size: Optional[int] = None
    date_range_start: Optional[str] = None
    date_range_end: Optional[str] = None
    preferred_times: Optional[List[str]] = None
    notify_email: Optional[str] = None
    notify_sms: Optional[str] = None
    active: Optional[bool] = None


class WatchConfig(WatchConfigBase):
    id: int
    restaurant_id: int
    last_checked: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AvailabilitySlot(BaseModel):
    date: str
    time: str
    party_size: int
    booking_url: Optional[str] = None


class AvailabilityCheck(BaseModel):
    id: int
    restaurant_id: int
    checked_at: datetime
    available_slots: List[AvailabilitySlot]
    notified: bool
    booking_url: Optional[str] = None
    
    class Config:
        from_attributes = True


class RestaurantWithWatch(Restaurant):
    watch_config: Optional[WatchConfig] = None


class SearchFilters(BaseModel):
    query: Optional[str] = None
    neighborhood: Optional[str] = None
    cuisine_type: Optional[str] = None
    visited: Optional[bool] = None
    monitor_enabled: Optional[bool] = None


class PaginatedResponse(BaseModel):
    items: List[Restaurant]
    total: int
    page: int
    per_page: int
    total_pages: int


class Stats(BaseModel):
    total_restaurants: int
    visited: int
    not_visited: int
    monitored: int
    neighborhoods: List[str]
    cuisine_types: List[str]
