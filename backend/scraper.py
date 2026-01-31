"""
Playwright-based scraper for checking restaurant availability on Resy and OpenTable.
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeout

@dataclass
class AvailableSlot:
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    party_size: int
    booking_url: str


class ResyScraper:
    """Scraper for Resy availability."""
    
    BASE_URL = "https://resy.com"
    
    def __init__(self, browser: Browser):
        self.browser = browser
    
    async def check_availability(
        self,
        restaurant_slug: str,
        date: str,
        party_size: int = 2,
        preferred_times: list[str] = None
    ) -> list[AvailableSlot]:
        """
        Check availability for a restaurant on Resy.
        
        Args:
            restaurant_slug: The URL slug for the restaurant (e.g., "lilia")
            date: Date to check in YYYY-MM-DD format
            party_size: Number of people
            preferred_times: List of preferred times in HH:MM format
            
        Returns:
            List of available slots
        """
        page = await self.browser.new_page()
        available_slots = []
        
        try:
            # Construct URL with query params
            url = f"{self.BASE_URL}/cities/ny/{restaurant_slug}?date={date}&seats={party_size}"
            
            # Add random delay to avoid detection
            await asyncio.sleep(random.uniform(1, 3))
            
            # Navigate to the page
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Wait for availability slots to load
            try:
                await page.wait_for_selector('[data-test="time-slot"]', timeout=10000)
            except PlaywrightTimeout:
                # No slots available
                return []
            
            # Find all time slots
            slots = await page.query_selector_all('[data-test="time-slot"]')
            
            for slot in slots:
                time_text = await slot.inner_text()
                time_clean = time_text.strip()
                
                # Convert to 24h format
                time_24h = self._convert_to_24h(time_clean)
                
                if time_24h:
                    # Check if it matches preferred times
                    if preferred_times is None or time_24h in preferred_times:
                        booking_url = f"{url}&time={time_24h}"
                        available_slots.append(AvailableSlot(
                            date=date,
                            time=time_24h,
                            party_size=party_size,
                            booking_url=booking_url
                        ))
        
        except Exception as e:
            print(f"Error checking Resy availability: {e}")
        
        finally:
            await page.close()
        
        return available_slots
    
    def _convert_to_24h(self, time_str: str) -> Optional[str]:
        """Convert time like '7:30 PM' to '19:30'."""
        try:
            # Handle various formats
            time_str = time_str.upper().strip()
            
            if 'AM' in time_str or 'PM' in time_str:
                # Parse 12h format
                dt = datetime.strptime(time_str, "%I:%M %p")
                return dt.strftime("%H:%M")
            else:
                # Already in 24h format
                return time_str
        except:
            return None


class OpenTableScraper:
    """Scraper for OpenTable availability."""
    
    BASE_URL = "https://www.opentable.com"
    
    def __init__(self, browser: Browser):
        self.browser = browser
    
    async def check_availability(
        self,
        restaurant_name: str,
        date: str,
        party_size: int = 2,
        preferred_times: list[str] = None
    ) -> list[AvailableSlot]:
        """
        Check availability for a restaurant on OpenTable.
        
        Args:
            restaurant_name: Name of the restaurant to search
            date: Date to check in YYYY-MM-DD format
            party_size: Number of people
            preferred_times: List of preferred times in HH:MM format
            
        Returns:
            List of available slots
        """
        page = await self.browser.new_page()
        available_slots = []
        
        try:
            # Search URL
            search_term = restaurant_name.replace(" ", "+")
            url = f"{self.BASE_URL}/s?term={search_term}&covers={party_size}&dateTime={date}T19%3A00&metroId=8"
            
            # Add random delay
            await asyncio.sleep(random.uniform(1, 3))
            
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Look for availability buttons
            try:
                await page.wait_for_selector('[data-test="times-702"]', timeout=10000)
            except PlaywrightTimeout:
                # Try alternative selector
                try:
                    await page.wait_for_selector('.timeSlot', timeout=5000)
                except PlaywrightTimeout:
                    return []
            
            # Find all time slots
            slots = await page.query_selector_all('.timeSlot, [data-test^="time-"]')
            
            for slot in slots:
                time_text = await slot.inner_text()
                time_clean = time_text.strip()
                time_24h = self._convert_to_24h(time_clean)
                
                if time_24h:
                    if preferred_times is None or time_24h in preferred_times:
                        href = await slot.get_attribute('href')
                        booking_url = href if href else url
                        
                        available_slots.append(AvailableSlot(
                            date=date,
                            time=time_24h,
                            party_size=party_size,
                            booking_url=booking_url
                        ))
        
        except Exception as e:
            print(f"Error checking OpenTable availability: {e}")
        
        finally:
            await page.close()
        
        return available_slots
    
    def _convert_to_24h(self, time_str: str) -> Optional[str]:
        """Convert time like '7:30 PM' to '19:30'."""
        try:
            time_str = time_str.upper().strip()
            if 'AM' in time_str or 'PM' in time_str:
                dt = datetime.strptime(time_str, "%I:%M %p")
                return dt.strftime("%H:%M")
            return time_str
        except:
            return None


class AvailabilityChecker:
    """Main class for checking availability across platforms."""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.resy_scraper: Optional[ResyScraper] = None
        self.opentable_scraper: Optional[OpenTableScraper] = None
    
    async def start(self):
        """Initialize the browser and scrapers."""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
            ]
        )
        self.resy_scraper = ResyScraper(self.browser)
        self.opentable_scraper = OpenTableScraper(self.browser)
    
    async def stop(self):
        """Close the browser."""
        if self.browser:
            await self.browser.close()
    
    async def check_resy(
        self,
        restaurant_slug: str,
        dates: list[str],
        party_size: int = 2,
        preferred_times: list[str] = None
    ) -> list[AvailableSlot]:
        """Check Resy availability for multiple dates."""
        all_slots = []
        
        for date in dates:
            slots = await self.resy_scraper.check_availability(
                restaurant_slug, date, party_size, preferred_times
            )
            all_slots.extend(slots)
            
            # Random delay between requests
            await asyncio.sleep(random.uniform(2, 5))
        
        return all_slots
    
    async def check_opentable(
        self,
        restaurant_name: str,
        dates: list[str],
        party_size: int = 2,
        preferred_times: list[str] = None
    ) -> list[AvailableSlot]:
        """Check OpenTable availability for multiple dates."""
        all_slots = []
        
        for date in dates:
            slots = await self.opentable_scraper.check_availability(
                restaurant_name, date, party_size, preferred_times
            )
            all_slots.extend(slots)
            
            await asyncio.sleep(random.uniform(2, 5))
        
        return all_slots
    
    def generate_date_range(self, start: str, end: str) -> list[str]:
        """Generate list of dates between start and end."""
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
        
        dates = []
        current = start_date
        while current <= end_date:
            dates.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)
        
        return dates


# Utility function for quick testing
async def test_scraper():
    """Test the scraper with a sample restaurant."""
    checker = AvailabilityChecker()
    await checker.start()
    
    try:
        # Test Resy
        print("Checking Lilia on Resy...")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        slots = await checker.check_resy(
            "lilia",
            [tomorrow],
            party_size=2,
            preferred_times=["18:00", "19:00", "20:00"]
        )
        
        if slots:
            print(f"Found {len(slots)} slots:")
            for slot in slots:
                print(f"  {slot.date} at {slot.time} for {slot.party_size}")
        else:
            print("No availability found")
    
    finally:
        await checker.stop()


if __name__ == "__main__":
    asyncio.run(test_scraper())
