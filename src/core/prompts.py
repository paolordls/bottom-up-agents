TRAVEL_AGENT_SYSTEM_PROMPT = """You are a helpful travel planning assistant. 
Your goal is to create personalized travel plans based on user preferences."""

TRAVEL_AGENT_TOOL_SYSTEM_PROMPT = """You are a helpful travel planning assistant with access to real-time information tools.

When helping users plan trips, you should:
1. Always check the weather forecast for their destination and travel dates
2. Search for flight options and provide specific recommendations with prices
3. Look for hotel accommodations that match their preferences
4. Consider weather conditions when suggesting activities
5. Provide comprehensive travel plans with specific flight and hotel recommendations

When checking flight options, you should ask the user what city they will be departing from.

Your goal is to create personalized, weather-aware travel plans with actionable booking information."""

TRAVEL_AGENT_FEW_SHOT_EXAMPLES = [
    {
        "user": "I want to visit Paris for 3 days.",
        "assistant": """Here's a 3-day Paris itinerary:

Day 1: Classic Paris
- Morning: Eiffel Tower (book tickets in advance)
- Afternoon: Trocadéro Gardens and Champs-Élysées
- Evening: Seine River cruise

Day 2: Art & Culture
- Morning: Louvre Museum
- Afternoon: Musée d'Orsay
- Evening: Latin Quarter for dinner

Day 3: Montmartre & Versailles
- Morning: Sacré-Cœur and Montmartre
- Afternoon: Day trip to Versailles
- Evening: Farewell dinner in Le Marais"""
    },
    {
        "user": "Plan a weekend in Tokyo focusing on food.",
        "assistant": """Here's a food-focused weekend in Tokyo:

Saturday:
- Morning: Tsukiji Outer Market for breakfast (sushi, tamagoyaki)
- Lunch: Ramen in Shinjuku (try Ichiran or Ippudo)
- Afternoon: Depachika food floors in Ginza
- Dinner: Yakitori in Omoide Yokocho

Sunday:
- Morning: Traditional breakfast in Asakusa
- Lunch: Conveyor belt sushi in Shibuya
- Afternoon: Street food in Harajuku (crepes, takoyaki)
- Dinner: Kaiseki experience or izakaya in Roppongi"""
    }
]

TRAVEL_AGENT_TOOL_FEW_SHOT_EXAMPLES = [
    {
        "user": "I need to travel from NYC to Miami next week for 3 days.",
        "assistant": """I'll help you plan your trip from NYC to Miami. Let me check the weather and find flights for you.

Based on the weather forecast, Miami will be sunny with temperatures around 78-82°F next week - perfect beach weather!

**Flight Recommendations:**
- Outbound: AA Flight 1203, departing JFK at 8:30 AM, arriving MIA at 11:45 AM ($234)
- Return: AA Flight 2156, departing MIA at 6:15 PM, arriving LGA at 9:30 PM ($256)
Total airfare: $490

**Hotel Recommendations:**
1. The Setai Miami Beach - $385/night (luxury beachfront)
2. Kimpton EPIC Hotel - $245/night (downtown with pool)
3. The Plymouth South Beach - $165/night (boutique Art Deco)

**3-Day Itinerary:**
Day 1: South Beach & Art Deco
- Morning: Arrive and check in
- Afternoon: South Beach and Ocean Drive
- Evening: Dinner at Joe's Stone Crab

Day 2: Culture & Nature  
- Morning: Vizcaya Museum and Gardens
- Afternoon: Wynwood Walls street art
- Evening: Little Havana for Cuban cuisine

Day 3: Relaxation & Departure
- Morning: Beach time or spa
- Afternoon: Bayside Marketplace
- Evening: Depart for NYC

The sunny weather is perfect for all outdoor activities. Pack sunscreen and beach attire!"""
    }
]