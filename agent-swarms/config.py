from collections import defaultdict
from datetime import datetime, timedelta

# Flight reservations storage
RESERVATIONS = defaultdict(lambda: {"flight_info": {}, "hotel_info": {}})

# Flight data
TOMORROW = (datetime.now() + timedelta(days=1)).isoformat()
FLIGHTS = [
    {
        "departure_airport": "BOS",
        "arrival_airport": "JFK",
        "airline": "Jet Blue",
        "date": TOMORROW,
        "id": "1",
    }
] 

HOTELS = [
    {
        "location": "New York",
        "name": "McKittrick Hotel",
        "neighborhood": "Chelsea",
        "id": "1",
    }
]