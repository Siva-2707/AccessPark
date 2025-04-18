import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from fastapi import FastAPI, Body
from sqlalchemy.orm import Session
from models import ParkingSpot, LocationRequest
from typing import List
import service
from database import SessionLocal
from fastapi import Depends

app = FastAPI()

def get_db():
    db = SessionLocal()
    print('Inside get_db')
    print("Type of db: ", type(db))
    try:
        yield db
    finally:
        db.close()

@app.get("/parking", response_model=List[ParkingSpot])
def get_parking_spots(db: Session = Depends(get_db)):
    records = service.get_parking_spots(db)
    return [
        ParkingSpot(
            city_lot_id=record.city_lot_id,
            name=record.name,
            no_of_spots=record.no_of_spots,
            location=record.location,
            city=record.city,
            state=record.state,
            country=record.country
        ) for record in records
    ]

@app.get("/parking/city/{city}", response_model=List[ParkingSpot])
def get_parking_spots_by_city(city: str, db: Session = Depends(get_db)):
    records = service.find_parking_spots_based_on_city(city,db)
    return [
        ParkingSpot(
            city_lot_id=record.city_lot_id,
            name=record.name,
            no_of_spots=record.no_of_spots,
            location=record.location,
            city=record.city,
            state=record.state,
            country=record.country
        ) for record in records
    ]

@app.post("/parking/location", response_model=List[ParkingSpot])
def get_parking_spots_by_location(payload: LocationRequest = Body(...), db: Session = Depends(get_db)):
    coord = (payload.lat, payload.lon)
    return service.find_parking_spots_based_on_location(coord, payload.radius,db)