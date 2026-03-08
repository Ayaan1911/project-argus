import json
import os
from pathlib import Path

def load_benchmarks():
    """Load price benchmark data from JSON file"""
    data_path = Path(__file__).parent.parent / "data" / "price_benchmarks.json"
    with open(data_path, 'r') as f:
        return json.load(f)

def normalize_string(s: str) -> str:
    """Normalize string for case-insensitive fuzzy matching"""
    return s.lower().strip()

def analyze_price(price: int, city: str, locality: str, property_type: str) -> dict:
    """
    Analyze rental price against market benchmarks
    
    Args:
        price: Listed rental price in INR
        city: City name
        locality: Locality/area name
        property_type: Property type (1BHK, 2BHK, 3BHK, PG)
    
    Returns:
        dict with score, verdict, market_median, percentage_below_market, reasoning
    """
    try:
        benchmarks = load_benchmarks()
    except Exception as e:
        return {
            "score": 30,
            "verdict": "Unable to verify",
            "market_median": None,
            "percentage_below_market": None,
            "reasoning": "Price benchmark data unavailable"
        }
    
    # Normalize inputs
    city_norm = normalize_string(city)
    locality_norm = normalize_string(locality)
    property_type_norm = normalize_string(property_type)
    
    # Find matching city
    if city_norm not in benchmarks:
        return {
            "score": 30,
            "verdict": "Unable to verify",
            "market_median": None,
            "percentage_below_market": None,
            "reasoning": f"City '{city}' not found in database. Unable to verify pricing."
        }
    
    city_data = benchmarks[city_norm]
    
    # Find matching locality
    if locality_norm not in city_data:
        return {
            "score": 30,
            "verdict": "Unable to verify",
            "market_median": None,
            "percentage_below_market": None,
            "reasoning": f"Locality '{locality}' not found in database for {city}. Unable to verify pricing."
        }
    
    locality_data = city_data[locality_norm]
    
    # Get median price for property type
    if property_type_norm not in locality_data:
        return {
            "score": 30,
            "verdict": "Unable to verify",
            "market_median": None,
            "percentage_below_market": None,
            "reasoning": f"Property type '{property_type}' not found in database."
        }
    
    market_median = locality_data[property_type_norm]
    std_dev_percent = locality_data.get("std_dev_percent", 0.20)
    std_dev = market_median * std_dev_percent
    
    # Calculate Z-score
    z_score = (price - market_median) / std_dev
    
    # Calculate percentage below market
    percentage_below_market = ((market_median - price) / market_median) * 100
    
    # Determine risk score and verdict based on Z-score
    if z_score < -1.5:
        # Price is significantly below market (high risk)
        score = min(100, int(85 + abs(z_score) * 5))
        verdict = "High Risk - Price Too Low"
        reasoning = f"Listed price of ₹{price:,} is {abs(percentage_below_market):.1f}% below market median of ₹{market_median:,}. This is suspiciously low and may indicate a scam."
    elif z_score < -0.5:
        # Price is moderately below market (suspicious)
        score = int(50 + abs(z_score) * 20)
        verdict = "Suspicious - Below Market Rate"
        reasoning = f"Listed price of ₹{price:,} is {abs(percentage_below_market):.1f}% below market median of ₹{market_median:,}. This is lower than typical rates and warrants caution."
    elif z_score <= 0.5:
        # Price is around market rate (likely genuine)
        score = int(20 + abs(z_score) * 10)
        verdict = "Likely Genuine"
        if price < market_median:
            reasoning = f"Listed price of ₹{price:,} is {abs(percentage_below_market):.1f}% below market median of ₹{market_median:,}. This is within normal range."
        else:
            reasoning = f"Listed price of ₹{price:,} is {percentage_below_market:.1f}% above market median of ₹{market_median:,}. This is within normal range."
    else:
        # Price is above market (low risk from pricing perspective)
        score = 10
        verdict = "Likely Genuine"
        reasoning = f"Listed price of ₹{price:,} is {abs(percentage_below_market):.1f}% above market median of ₹{market_median:,}. Higher prices are generally less risky."
    
    return {
        "score": score,
        "verdict": verdict,
        "market_median": market_median,
        "percentage_below_market": round(percentage_below_market, 2),
        "reasoning": reasoning
    }
