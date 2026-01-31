"""
FastAPI backend for Grace's Gourmet Guide.
"""

import os
import json
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_

from models import (
    Restaurant as RestaurantModel,
    init_db, get_db
)
from schemas import (
    Restaurant, RestaurantCreate, RestaurantUpdate,
    PaginatedResponse, Stats
)

app = FastAPI(
    title="Grace's Gourmet Guide API",
    description="NYC Restaurant Guide",
    version="1.0.0"
)

# CORS configuration - allow all origins for simplicity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    init_db()
    
    db = next(get_db())
    count = db.query(RestaurantModel).count()
    if count == 0:
        load_initial_data(db)
    db.close()


def load_initial_data(db: Session):
    """Load restaurants from JSON file into database."""
    json_path = Path("data/restaurants.json")
    if not json_path.exists():
        print(f"Warning: {json_path} not found")
        return
    
    with open(json_path) as f:
        restaurants = json.load(f)
    
    for r in restaurants:
        restaurant = RestaurantModel(
            name=r["name"],
            visited=r.get("visited", False),
            notes=r.get("notes", ""),
            neighborhood=r.get("neighborhood"),
            cuisine_type=r.get("cuisine_type"),
            booking_urls=r.get("booking_urls", {}),
            monitor_enabled=r.get("monitor_enabled", False),
            priority=r.get("priority", "normal")
        )
        db.add(restaurant)
    
    db.commit()
    print(f"Loaded {len(restaurants)} restaurants into database")


@app.get("/api/restaurants", response_model=PaginatedResponse)
def get_restaurants(
    query: Optional[str] = None,
    neighborhood: Optional[str] = None,
    cuisine_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all restaurants with optional filters and pagination."""
    q = db.query(RestaurantModel)
    
    if query:
        search = f"%{query}%"
        q = q.filter(
            or_(
                RestaurantModel.name.ilike(search),
                RestaurantModel.notes.ilike(search),
                RestaurantModel.neighborhood.ilike(search),
                RestaurantModel.cuisine_type.ilike(search)
            )
        )
    
    if neighborhood:
        q = q.filter(RestaurantModel.neighborhood == neighborhood)
    
    if cuisine_type:
        q = q.filter(RestaurantModel.cuisine_type == cuisine_type)
    
    total = q.count()
    offset = (page - 1) * per_page
    restaurants = q.order_by(RestaurantModel.name).offset(offset).limit(per_page).all()
    total_pages = (total + per_page - 1) // per_page
    
    return PaginatedResponse(
        items=restaurants,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@app.get("/api/restaurants/{restaurant_id}", response_model=Restaurant)
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    """Get a single restaurant by ID."""
    restaurant = db.query(RestaurantModel).filter(RestaurantModel.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant


@app.get("/api/stats", response_model=Stats)
def get_stats(db: Session = Depends(get_db)):
    """Get statistics about the restaurant collection."""
    total = db.query(RestaurantModel).count()
    visited = db.query(RestaurantModel).filter(RestaurantModel.visited == True).count()
    monitored = db.query(RestaurantModel).filter(RestaurantModel.monitor_enabled == True).count()
    
    neighborhoods = db.query(RestaurantModel.neighborhood).filter(
        RestaurantModel.neighborhood.isnot(None)
    ).distinct().all()
    neighborhoods = sorted([n[0] for n in neighborhoods if n[0]])
    
    cuisine_types = db.query(RestaurantModel.cuisine_type).filter(
        RestaurantModel.cuisine_type.isnot(None)
    ).distinct().all()
    cuisine_types = sorted([c[0] for c in cuisine_types if c[0]])
    
    return Stats(
        total_restaurants=total,
        visited=visited,
        not_visited=total - visited,
        monitored=monitored,
        neighborhoods=neighborhoods,
        cuisine_types=cuisine_types
    )


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/")
def root():
    """Root endpoint."""
    return {"message": "Grace's Gourmet Guide API", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
