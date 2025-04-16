from sqlalchemy import Column, Integer, String
from dataclasses import dataclass
from database import Base

class AccessibilityParking(Base):

    __tablename__ = "accessibility_parking"

    record_hash = Column(String, primary_key=True)
    city_lot_id = Column(Integer)
    name = Column(String(255))
    no_of_spots =  Column(Integer)
    location = Column(String(255))
    city = Column(String(255))
    state = Column(String(255))
    country = Column(String(255))

@dataclass
class ParkingSpot:
    city_lot_id: int
    name: str
    no_of_spots: int
    location: str
    city: str
    state: str
    country: str
    distance_from_user: float = 0.0

@dataclass
class LocationRequest:
    lat: float
    lon: float
    radius: float = 5.0 







    