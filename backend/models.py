"""
Database models for the restaurant notification system.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

class Restaurant(Base):
    """Restaurant model."""
    __tablename__ = "restaurants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    visited = Column(Boolean, default=False)
    notes = Column(Text, default="")
    neighborhood = Column(String(100), nullable=True, index=True)
    cuisine_type = Column(String(100), nullable=True, index=True)
    booking_urls = Column(JSON, default=dict)
    monitor_enabled = Column(Boolean, default=False)
    priority = Column(String(20), default="normal")  # normal, high, urgent
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to watch list
    watch_config = relationship("WatchConfig", back_populates="restaurant", uselist=False, cascade="all, delete-orphan")
    availability_checks = relationship("AvailabilityCheck", back_populates="restaurant", cascade="all, delete-orphan")


class WatchConfig(Base):
    """Configuration for monitoring a restaurant's availability."""
    __tablename__ = "watch_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), unique=True)
    party_size = Column(Integer, default=2)
    date_range_start = Column(String(10), nullable=True)  # YYYY-MM-DD
    date_range_end = Column(String(10), nullable=True)    # YYYY-MM-DD
    preferred_times = Column(JSON, default=list)  # ["18:00", "19:00", "20:00"]
    notify_email = Column(String(255), nullable=True)
    notify_sms = Column(String(20), nullable=True)
    active = Column(Boolean, default=True)
    last_checked = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    restaurant = relationship("Restaurant", back_populates="watch_config")


class AvailabilityCheck(Base):
    """Log of availability checks and found slots."""
    __tablename__ = "availability_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    checked_at = Column(DateTime, default=datetime.utcnow)
    available_slots = Column(JSON, default=list)  # [{"date": "2026-02-15", "time": "19:30", "party_size": 2}]
    notified = Column(Boolean, default=False)
    booking_url = Column(Text, nullable=True)
    
    restaurant = relationship("Restaurant", back_populates="availability_checks")


class NotificationLog(Base):
    """Log of sent notifications."""
    __tablename__ = "notification_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"))
    notification_type = Column(String(20))  # email, sms
    recipient = Column(String(255))
    message = Column(Text)
    sent_at = Column(DateTime, default=datetime.utcnow)
    success = Column(Boolean, default=True)


# Database setup
DATABASE_URL = "sqlite:///./data/restaurants.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
