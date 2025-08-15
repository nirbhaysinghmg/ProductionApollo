#!/usr/bin/env python3
"""
Test script for geocoding service
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.geocoding import geocoding_service

def test_geocoding():
    """Test the geocoding service with known coordinates"""
    
    # Test coordinates for different cities
    test_coordinates = [
        (26.7912664, 80.9715834, "Lucknow"),  # Lucknow, UP
        (19.0760, 72.8777, "Mumbai"),         # Mumbai, Maharashtra
        (28.7041, 77.1025, "Delhi"),          # Delhi
        (12.9716, 77.5946, "Bangalore"),      # Bangalore, Karnataka
        (22.5726, 88.3639, "Kolkata"),        # Kolkata, West Bengal
        (13.0827, 80.2707, "Chennai"),        # Chennai, Tamil Nadu
    ]
    
    print("Testing geocoding service...")
    print("=" * 50)
    
    for lat, lng, expected_city in test_coordinates:
        print(f"\nTesting coordinates: {lat}, {lng}")
        print(f"Expected city: {expected_city}")
        
        try:
            # Get city name
            city_name = geocoding_service.get_city_from_coordinates(lat, lng)
            print(f"Detected city: {city_name}")
            
            # Get full location info
            location_info = geocoding_service.get_location_info(lat, lng)
            print(f"Full location info: {location_info}")
            
            if city_name:
                print("✅ City detected successfully")
            else:
                print("❌ No city detected")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 30)

if __name__ == "__main__":
    test_geocoding() 