"""
Background scheduler for checking restaurant availability.
"""

import asyncio
import re
from datetime import datetime, timedelta
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session

from models import (
    Restaurant as RestaurantModel,
    WatchConfig as WatchConfigModel,
    AvailabilityCheck as AvailabilityCheckModel,
    SessionLocal
)
from scraper import AvailabilityChecker, AvailableSlot
from notifications import send_availability_notification


class AvailabilityScheduler:
    """Scheduler for checking restaurant availability."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.checker: Optional[AvailabilityChecker] = None
        self.running = False
    
    async def start(self):
        """Start the scheduler."""
        print("Starting availability scheduler...")
        
        # Initialize the scraper
        self.checker = AvailabilityChecker()
        await self.checker.start()
        
        # Add job to check availability every 15 minutes
        self.scheduler.add_job(
            self.check_all_watched_restaurants,
            IntervalTrigger(minutes=15),
            id='check_availability',
            name='Check restaurant availability',
            replace_existing=True
        )
        
        self.scheduler.start()
        self.running = True
        print("Scheduler started - checking every 15 minutes")
    
    async def stop(self):
        """Stop the scheduler."""
        print("Stopping scheduler...")
        self.scheduler.shutdown()
        if self.checker:
            await self.checker.stop()
        self.running = False
    
    async def check_all_watched_restaurants(self):
        """Check availability for all restaurants being watched."""
        print(f"\n[{datetime.now().isoformat()}] Running availability check...")
        
        db = SessionLocal()
        try:
            # Get all active watch configs
            watch_configs = db.query(WatchConfigModel).filter(
                WatchConfigModel.active == True
            ).all()
            
            print(f"Checking {len(watch_configs)} watched restaurants")
            
            for config in watch_configs:
                await self.check_restaurant(db, config)
                # Update last checked time
                config.last_checked = datetime.utcnow()
                db.commit()
                
                # Delay between restaurants to avoid rate limiting
                await asyncio.sleep(5)
        
        except Exception as e:
            print(f"Error during availability check: {e}")
        
        finally:
            db.close()
    
    async def check_restaurant(self, db: Session, config: WatchConfigModel):
        """Check availability for a single restaurant."""
        restaurant = db.query(RestaurantModel).filter(
            RestaurantModel.id == config.restaurant_id
        ).first()
        
        if not restaurant:
            return
        
        print(f"  Checking: {restaurant.name}")
        
        # Generate dates to check
        if config.date_range_start and config.date_range_end:
            dates = self.checker.generate_date_range(
                config.date_range_start,
                config.date_range_end
            )
        else:
            # Default: next 7 days
            dates = self.checker.generate_date_range(
                datetime.now().strftime("%Y-%m-%d"),
                (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
            )
        
        # Limit to 7 dates to avoid too many requests
        dates = dates[:7]
        
        # Check based on booking platform
        slots = []
        
        if restaurant.booking_urls and 'resy' in str(restaurant.booking_urls):
            # Extract slug from Resy URL
            resy_url = restaurant.booking_urls.get('resy', '')
            slug = self._extract_resy_slug(resy_url)
            
            if slug:
                slots = await self.checker.check_resy(
                    slug,
                    dates,
                    party_size=config.party_size,
                    preferred_times=config.preferred_times
                )
        
        # If no Resy slots, try OpenTable
        if not slots and restaurant.booking_urls and 'opentable' in str(restaurant.booking_urls):
            slots = await self.checker.check_opentable(
                restaurant.name,
                dates,
                party_size=config.party_size,
                preferred_times=config.preferred_times
            )
        
        # Process results
        if slots:
            print(f"    Found {len(slots)} available slots!")
            
            # Check for new slots (not already notified)
            new_slots = await self._filter_new_slots(db, restaurant.id, slots)
            
            if new_slots:
                # Save to database
                check_record = AvailabilityCheckModel(
                    restaurant_id=restaurant.id,
                    available_slots=[{
                        'date': s.date,
                        'time': s.time,
                        'party_size': s.party_size,
                        'booking_url': s.booking_url
                    } for s in new_slots],
                    booking_url=new_slots[0].booking_url if new_slots else None
                )
                db.add(check_record)
                db.commit()
                
                # Send notification
                if config.notify_email:
                    await send_availability_notification(
                        email=config.notify_email,
                        restaurant_name=restaurant.name,
                        slots=new_slots
                    )
                    check_record.notified = True
                    db.commit()
        else:
            print(f"    No availability found")
    
    def _extract_resy_slug(self, url: str) -> Optional[str]:
        """Extract restaurant slug from Resy URL."""
        # URL like: https://resy.com/cities/ny/lilia
        match = re.search(r'resy\.com/cities/\w+/([^/?]+)', url)
        return match.group(1) if match else None
    
    async def _filter_new_slots(
        self, 
        db: Session, 
        restaurant_id: int, 
        slots: list[AvailableSlot]
    ) -> list[AvailableSlot]:
        """Filter out slots that were already found and notified."""
        # Get recent checks for this restaurant
        recent_checks = db.query(AvailabilityCheckModel).filter(
            AvailabilityCheckModel.restaurant_id == restaurant_id,
            AvailabilityCheckModel.checked_at > datetime.utcnow() - timedelta(hours=24)
        ).all()
        
        # Build set of already-found slots
        found_slots = set()
        for check in recent_checks:
            if check.available_slots:
                for slot in check.available_slots:
                    found_slots.add((slot['date'], slot['time']))
        
        # Filter to new slots only
        new_slots = [
            s for s in slots 
            if (s.date, s.time) not in found_slots
        ]
        
        return new_slots


# Create a global scheduler instance
scheduler = AvailabilityScheduler()


async def run_scheduler():
    """Run the scheduler as a standalone process."""
    await scheduler.start()
    
    try:
        # Keep the scheduler running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await scheduler.stop()


if __name__ == "__main__":
    asyncio.run(run_scheduler())
