from flask import Flask, request, jsonify
from geopy.distance import geodesic

app = Flask(__name__)

# Mock data store
PARKING_SPOTS = [
    {"id": 1, "name": "Spot A", "location": (37.7749, -122.4194), "city": "San Francisco"},
    {"id": 2, "name": "Spot B", "location": (37.7849, -122.4094), "city": "San Francisco"},
    {"id": 3, "name": "Spot C", "location": (34.0522, -118.2437), "city": "Los Angeles"},
    {"id": 4, "name": "Spot D", "location": (34.0622, -118.2537), "city": "Los Angeles"},
]

@app.route('/api/accessibility_parking/nearby', methods=['GET'])
def get_parking_nearby():
    """Get parking spots based on current location and optional radius."""
    try:
        lat = float(request.args.get('lat'))
        lon = float(request.args.get('lon'))
        radius = float(request.args.get('radius', 5))  # Default radius is 5 km
        current_location = (lat, lon)

        nearby_spots = [
            spot for spot in PARKING_SPOTS
            if geodesic(current_location, spot['location']).km <= radius
        ]
        return jsonify(nearby_spots), 200
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid or missing parameters"}), 400

@app.route('/api/accessibility_parking/by_city', methods=['GET'])
def get_parking_by_city():
    """List all parking spots based on city."""
    city = request.args.get('city')
    if not city:
        return jsonify({"error": "City parameter is required"}), 400

    city_spots = [spot for spot in PARKING_SPOTS if spot['city'].lower() == city.lower()]
    return jsonify(city_spots), 200

if __name__ == '__main__':
    app.run(debug=True)