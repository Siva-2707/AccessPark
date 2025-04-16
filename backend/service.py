import math
from sqlalchemy.orm import Session
from models import AccessibilityParking, ParkingSpot


# Haversine formula to calculate the distance between two points on Earth (in km)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c  # Returns distance in kilometers

def find_coordinates_within_radius(input_coord, merged_df, radius):
    results = []
    print("Type of merged_df: ", type(merged_df))
    for rows in merged_df:
        coord = rows.location
        coord = coord.split(",")
        coord[0] = float(coord[0])
        coord[1] = float(coord[1])
        distance = haversine(input_coord[0], input_coord[1], coord[1], coord[0])
        
        if distance <= radius:
            print("Distance: ", distance)
            results.append({"data":rows,"distance":distance})  # Add coordinate and distance to the results

    # Sort results by distance (nearest first)
    results.sort(key=lambda x: x["distance"])
    print("Results: ", results[1])
    return results

def get_parking_spots(db: Session):
    records = db.query(AccessibilityParking).all()

def find_parking_spots_based_on_city(city: str, db: Session):
    print("Type of db: ", type(db))
    if city:
        records = db.query(AccessibilityParking).filter(AccessibilityParking.city == city).all()
    else:
        records = db.query(AccessibilityParking).all()
    return records

def find_parking_spots_based_on_location(coord: tuple, radius: float, db: Session):
    records = db.query(AccessibilityParking).all()
    results = find_coordinates_within_radius(coord, records, radius)
    return[
        ParkingSpot(
        city_lot_id=record["data"].city_lot_id,
        name=record["data"].name,
        no_of_spots=record["data"].no_of_spots,
        location=record["data"].location,
        city=record["data"].city,
        state=record["data"].state,
        country=record["data"].country,
        distance_from_user=record["distance"]
    ) for record in results
    ]

