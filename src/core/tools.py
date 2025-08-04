from typing import Dict, List, Callable, Any
import json
from datetime import datetime
import requests
import random


class Tool:
    def __init__(self, name: str, description: str, function: Callable, parameters: Dict[str, Any]):
        self.name = name
        self.description = description
        self.function = function
        self.parameters = parameters
    
    def to_openai_function(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }
    
    def execute(self, **kwargs) -> str:
        # 50% chance of failure for demonstration
        if random.random() < 0.5:
            failure_messages = [
                f"❌ {self.name} service temporarily unavailable. Please try again.",
                f"❌ {self.name} connection timeout. Service may be experiencing high load.",
                f"❌ {self.name} returned an error. Please retry the request.",
                f"❌ {self.name} service is down for maintenance. Try again shortly."
            ]
            return random.choice(failure_messages)
        
        try:
            result = self.function(**kwargs)
            return json.dumps(result) if not isinstance(result, str) else result
        except Exception as e:
            return f"Error executing {self.name}: {str(e)}"


# Example travel planning tools
def search_flights(origin: str, destination: str, date: str) -> Dict[str, Any]:
    # Randomized mock implementation
    airlines = ["SkyWings Airlines", "Global Air", "Swift Travel", "Azure Airways", "Horizon Flight", "Cloud9 Airlines"]
    
    # Generate 1-3 random flights
    num_flights = random.randint(1, 3)
    flights = []
    
    for i in range(num_flights):
        departure_hour = random.randint(6, 22)
        flight_duration = random.randint(2, 14)  # 2-14 hours
        arrival_hour = (departure_hour + flight_duration) % 24
        price = random.randint(200, 1200)
        
        flights.append({
            "airline": random.choice(airlines),
            "departure": f"{origin} {departure_hour:02d}:{random.randint(0, 59):02d}",
            "arrival": f"{destination} {arrival_hour:02d}:{random.randint(0, 59):02d}",
            "price": f"${price}",
            "date": date,
            "flight_number": f"{random.choice(['AA', 'UA', 'DL', 'SW'])}{random.randint(100, 9999)}",
            "duration": f"{flight_duration}h {random.randint(0, 59)}m"
        })
    
    return {"flights": flights}


def search_hotels(city: str, checkin_date: str, checkout_date: str) -> Dict[str, Any]:
    # Randomized mock implementation
    hotel_names = [
        "Grand Palace Hotel", "City Center Inn", "Skyline Resort", "Harbor View Hotel", 
        "Metropolitan Suites", "Royal Gardens Hotel", "Downtown Plaza", "Sunset Lodge",
        "Urban Retreat", "Cosmopolitan Hotel", "Riverside Inn", "Crown Hotel"
    ]
    
    locations = [f"Downtown {city}", f"{city} City Center", f"Old Town {city}", 
                f"{city} Business District", f"Historic {city}", f"Airport Area {city}"]
    
    amenities_list = [
        ["Free WiFi", "Pool", "Gym"], ["Spa", "Restaurant", "Room Service"],
        ["Business Center", "Parking", "Pet Friendly"], ["Beach Access", "Bar", "Concierge"],
        ["Breakfast Included", "Airport Shuttle", "Fitness Center"]
    ]
    
    # Generate 1-4 random hotels
    num_hotels = random.randint(1, 4)
    hotels = []
    
    for i in range(num_hotels):
        price = random.randint(80, 500)
        rating = round(random.uniform(3.0, 5.0), 1)
        
        hotels.append({
            "name": random.choice(hotel_names),
            "location": random.choice(locations),
            "price_per_night": f"${price}",
            "rating": rating,
            "amenities": random.choice(amenities_list),
            "availability": "Available" if random.random() > 0.2 else "Limited availability"
        })
    
    return {"hotels": hotels}


def get_weather(city: str, date: str) -> Dict[str, Any]:
    # Randomized mock implementation
    conditions = [
        "Sunny", "Partly cloudy", "Cloudy", "Light rain", "Heavy rain", 
        "Thunderstorms", "Snow", "Foggy", "Windy", "Clear skies"
    ]
    
    # Temperature varies by season - more moderate like typical travel destinations
    temp_celsius = random.randint(5, 30)  # 5°C to 30°C (41°F to 86°F)
    temp_fahrenheit = int(temp_celsius * 9/5 + 32)
    
    humidity = random.randint(30, 90)
    precipitation = random.randint(0, 80)
    wind_speed = random.randint(5, 25)
    
    condition = random.choice(conditions)
    
    # Add weather-appropriate details
    extras = {}
    if "rain" in condition.lower():
        extras["umbrella_needed"] = True
        precipitation = max(precipitation, 40)  # Higher chance of rain
    elif condition == "Snow":
        temp_celsius = random.randint(-2, 5)  # Snow only at low temps
        temp_fahrenheit = int(temp_celsius * 9/5 + 32)
        extras["winter_clothing_recommended"] = True
    elif condition == "Sunny":
        extras["sunscreen_recommended"] = True
        precipitation = min(precipitation, 20)  # Lower chance of rain when sunny
    
    return {
        "city": city,
        "date": date,
        "temperature": f"{temp_celsius}°C ({temp_fahrenheit}°F)",
        "condition": condition,
        "precipitation_chance": f"{precipitation}%",
        "humidity": f"{humidity}%",
        "wind_speed": f"{wind_speed} km/h",
        **extras
    }


# Tool definitions
TRAVEL_TOOLS = [
    Tool(
        name="search_flights",
        description="Search for available flights between cities",
        function=search_flights,
        parameters={
            "type": "object",
            "properties": {
                "origin": {"type": "string", "description": "Departure city"},
                "destination": {"type": "string", "description": "Arrival city"},
                "date": {"type": "string", "description": "Travel date (YYYY-MM-DD)"}
            },
            "required": ["origin", "destination", "date"]
        }
    ),
    Tool(
        name="search_hotels",
        description="Search for hotels in a specific city",
        function=search_hotels,
        parameters={
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"},
                "checkin_date": {"type": "string", "description": "Check-in date (YYYY-MM-DD)"},
                "checkout_date": {"type": "string", "description": "Check-out date (YYYY-MM-DD)"}
            },
            "required": ["city", "checkin_date", "checkout_date"]
        }
    ),
    Tool(
        name="get_weather",
        description="Get weather forecast for a city on a specific date",
        function=get_weather,
        parameters={
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"},
                "date": {"type": "string", "description": "Date (YYYY-MM-DD)"}
            },
            "required": ["city", "date"]
        }
    )
]