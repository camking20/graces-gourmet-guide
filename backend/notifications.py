"""
Email notification service for availability alerts.
"""

import os
from datetime import datetime
from typing import Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, HtmlContent

# Load from environment
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '')
FROM_EMAIL = os.getenv('NOTIFICATION_FROM_EMAIL', 'noreply@restaurant-notifier.local')


def format_time_12h(time_24h: str) -> str:
    """Convert 24h time to 12h format."""
    try:
        dt = datetime.strptime(time_24h, "%H:%M")
        return dt.strftime("%I:%M %p").lstrip("0")
    except:
        return time_24h


def format_date_readable(date_str: str) -> str:
    """Convert YYYY-MM-DD to readable format."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%A, %B %d")
    except:
        return date_str


async def send_availability_notification(
    email: str,
    restaurant_name: str,
    slots: list,  # List of AvailableSlot
    sms_number: Optional[str] = None
):
    """
    Send notification about available reservation slots.
    
    Args:
        email: Recipient email address
        restaurant_name: Name of the restaurant
        slots: List of available slots
        sms_number: Optional phone number for SMS notification
    """
    if not SENDGRID_API_KEY:
        print(f"[NOTIFICATION] Would send email to {email} about {restaurant_name}")
        print(f"  Available slots: {len(slots)}")
        for slot in slots:
            print(f"    - {slot.date} at {slot.time}")
        return
    
    # Build email content
    subject = f"🍽️ {restaurant_name} has availability!"
    
    # Build HTML content
    slots_html = ""
    for slot in slots[:5]:  # Limit to 5 slots
        formatted_date = format_date_readable(slot.date)
        formatted_time = format_time_12h(slot.time)
        
        slots_html += f"""
        <tr>
            <td style="padding: 12px 16px; border-bottom: 1px solid #eee;">
                <strong>{formatted_date}</strong><br>
                <span style="color: #666;">{formatted_time} • Party of {slot.party_size}</span>
            </td>
            <td style="padding: 12px 16px; border-bottom: 1px solid #eee; text-align: right;">
                <a href="{slot.booking_url}" 
                   style="display: inline-block; padding: 8px 16px; background: #C45D3A; 
                          color: white; text-decoration: none; border-radius: 6px;
                          font-weight: 500;">
                    Book Now
                </a>
            </td>
        </tr>
        """
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                 background-color: #FDF8F3; margin: 0; padding: 20px;">
        <div style="max-width: 500px; margin: 0 auto; background: white; border-radius: 16px; 
                    overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #C45D3A 0%, #722F37 100%); 
                        padding: 32px 24px; text-align: center;">
                <h1 style="margin: 0; color: white; font-size: 24px; font-weight: 600;">
                    {restaurant_name}
                </h1>
                <p style="margin: 8px 0 0; color: rgba(255,255,255,0.9); font-size: 16px;">
                    has availability! 🎉
                </p>
            </div>
            
            <!-- Content -->
            <div style="padding: 24px;">
                <p style="margin: 0 0 20px; color: #333; font-size: 15px;">
                    Great news! We found open reservation slots at <strong>{restaurant_name}</strong>. 
                    Book quickly before they're gone!
                </p>
                
                <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                    {slots_html}
                </table>
                
                {f'<p style="color: #666; font-size: 13px;">+ {len(slots) - 5} more slots available</p>' if len(slots) > 5 else ''}
            </div>
            
            <!-- Footer -->
            <div style="padding: 16px 24px; background: #f9f9f9; border-top: 1px solid #eee; 
                        text-align: center;">
                <p style="margin: 0; color: #999; font-size: 12px;">
                    You're receiving this because you set up alerts for {restaurant_name}.<br>
                    <a href="#" style="color: #C45D3A;">Manage notifications</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text fallback
    plain_content = f"""
{restaurant_name} has availability!

We found the following open slots:

"""
    for slot in slots[:5]:
        formatted_date = format_date_readable(slot.date)
        formatted_time = format_time_12h(slot.time)
        plain_content += f"• {formatted_date} at {formatted_time} for {slot.party_size}\n"
        plain_content += f"  Book: {slot.booking_url}\n\n"
    
    # Send via SendGrid
    try:
        message = Mail(
            from_email=Email(FROM_EMAIL, "Restaurant Notifier"),
            to_emails=To(email),
            subject=subject,
            html_content=HtmlContent(html_content),
            plain_text_content=Content("text/plain", plain_content)
        )
        
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        
        print(f"[NOTIFICATION] Email sent to {email} (status: {response.status_code})")
        return response.status_code == 202
    
    except Exception as e:
        print(f"[NOTIFICATION] Failed to send email: {e}")
        return False


async def send_test_notification(email: str):
    """Send a test notification email."""
    from scraper import AvailableSlot
    
    test_slots = [
        AvailableSlot(
            date="2026-02-15",
            time="19:00",
            party_size=2,
            booking_url="https://resy.com/cities/ny/lilia?date=2026-02-15&seats=2"
        ),
        AvailableSlot(
            date="2026-02-15",
            time="20:30",
            party_size=2,
            booking_url="https://resy.com/cities/ny/lilia?date=2026-02-15&seats=2"
        ),
    ]
    
    await send_availability_notification(
        email=email,
        restaurant_name="Lilia (TEST)",
        slots=test_slots
    )


if __name__ == "__main__":
    import asyncio
    # Test the notification system
    asyncio.run(send_test_notification("test@example.com"))
