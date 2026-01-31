# NYC Restaurant Reservation Notifier 🍽️

A personal tool to search, track, and get notified about restaurant availability at your favorite NYC spots.

## Features

- **Searchable Database**: 489 restaurants with filters for neighborhood, cuisine type, and visited status
- **One-Click Booking Links**: Direct links to Resy, OpenTable, and Google for each restaurant
- **Availability Monitoring**: Automated scraping to check for open reservations
- **Email Notifications**: Get alerted when hard-to-book restaurants have openings

## Quick Start

### 1. Start the Backend

```bash
cd backend
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. Start the Frontend

```bash
cd frontend
npm run dev
```

### 3. Open the App

Visit [http://localhost:5173](http://localhost:5173)

## Architecture

```
restaurant-notifier/
├── backend/
│   ├── main.py           # FastAPI server
│   ├── models.py         # SQLAlchemy database models
│   ├── schemas.py        # Pydantic validation schemas
│   ├── scraper.py        # Playwright availability scraper
│   ├── scheduler.py      # Background job scheduler
│   ├── notifications.py  # Email notification service
│   └── data/
│       ├── restaurants.json  # Parsed restaurant data
│       └── restaurants.db    # SQLite database
│
└── frontend/
    └── src/
        ├── App.tsx           # Main React component
        ├── api.ts            # API client
        └── components/       # UI components
```

## Setting Up Notifications

### Email (SendGrid)

1. Create a free SendGrid account at [sendgrid.com](https://sendgrid.com)
2. Generate an API key
3. Create a `.env` file in the backend directory:

```env
SENDGRID_API_KEY=your_api_key_here
NOTIFICATION_FROM_EMAIL=your-email@example.com
```

### Installing Playwright Browsers

The scraper uses Playwright for browser automation. Install browsers with:

```bash
cd backend
source venv/bin/activate
playwright install chromium
```

## Using the Availability Monitor

### Via the UI

1. Click the bell icon on any restaurant card
2. Set your party size, date range, and preferred times
3. Enter your email address
4. Click "Start Watching"

### Via the API

Start the scheduler:
```bash
curl -X POST http://localhost:8000/api/scheduler/start
```

Check scheduler status:
```bash
curl http://localhost:8000/api/scheduler/status
```

Trigger an immediate check:
```bash
curl -X POST http://localhost:8000/api/scheduler/check-now
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/restaurants` | GET | List restaurants with filters |
| `/api/restaurants/{id}` | GET | Get single restaurant |
| `/api/restaurants/{id}/toggle-visited` | PATCH | Toggle visited status |
| `/api/stats` | GET | Get collection statistics |
| `/api/watch-configs` | GET/POST | Manage watch configurations |
| `/api/scheduler/start` | POST | Start the availability checker |
| `/api/scheduler/stop` | POST | Stop the scheduler |
| `/api/test-notification` | POST | Send a test email |

## Important Notes

⚠️ **Scraping Disclaimer**: The availability monitoring feature scrapes Resy and OpenTable websites. This may violate their Terms of Service. Use at your own risk and be mindful of rate limits.

## Tech Stack

- **Frontend**: React, TypeScript, Vite, Tailwind CSS
- **Backend**: Python, FastAPI, SQLAlchemy, SQLite
- **Scraping**: Playwright
- **Notifications**: SendGrid
- **Scheduling**: APScheduler
