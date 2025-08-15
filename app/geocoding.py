import requests
import json
from typing import Optional, Dict, Any
import time

class GeocodingService:
    """Service to convert coordinates to city names using free geocoding APIs"""
    
    def __init__(self):
        self.cache = {}
        self.cache_file = "geocoding_cache.json"
        self.load_cache()
    
    def load_cache(self):
        """Load cached geocoding results from file"""
        try:
            with open(self.cache_file, 'r') as f:
                self.cache = json.load(f)
        except FileNotFoundError:
            self.cache = {}
    
    def save_cache(self):
        """Save cached geocoding results to file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f)
        except Exception as e:
            print(f"Error saving geocoding cache: {e}")
    
    def get_city_from_coordinates(self, latitude: float, longitude: float) -> Optional[str]:
        """
        Convert coordinates to city name using free geocoding APIs
        Returns city name or None if not found
        """
        # Create cache key
        cache_key = f"{latitude:.6f},{longitude:.6f}"
        
        # Check cache first
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Try Nominatim API (free, no API key required)
        city_name = self._try_nominatim(latitude, longitude)
        
        # Cache the result (even if None to avoid repeated failed requests)
        self.cache[cache_key] = city_name
        self.save_cache()
        
        return city_name
    
    def _try_nominatim(self, latitude: float, longitude: float) -> Optional[str]:
        """Try OpenStreetMap Nominatim API (free, no API key required)"""
        try:
            url = f"https://nominatim.openstreetmap.org/reverse"
            params = {
                "lat": latitude,
                "lon": longitude,
                "format": "json",
                "addressdetails": 1,
                "accept-language": "en"
            }
            
            print(f"Making request to Nominatim: {url} with params: {params}")
            headers = {
                'User-Agent': 'ApolloTyresChatbot/1.0 (https://apollotyres.com; contact@apollotyres.com)'
            }
            response = requests.get(url, params=params, headers=headers, timeout=5)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response data: {data}")
                address = data.get("address", {})
                print(f"Address data: {address}")
                
                # Try to get city name from various fields
                city = (
                    address.get("city") or
                    address.get("town") or
                    address.get("village") or
                    address.get("municipality") or
                    address.get("county") or
                    address.get("state")
                )
                
                print(f"Extracted city: {city}")
                if city:
                    return city
            
        except Exception as e:
            print(f"Error with Nominatim API: {e}")
        
        return None
    

    
    def get_location_info(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Get comprehensive location information including city name
        Returns a dictionary with location details
        """
        city_name = self.get_city_from_coordinates(latitude, longitude)
        
        # Determine region based on coordinates
        region = self._get_region_from_coordinates(latitude, longitude)
        
        return {
            "city": city_name,
            "region": region,
            "latitude": latitude,
            "longitude": longitude,
            "coordinates": f"{latitude:.4f}, {longitude:.4f}"
        }
    
    def _get_region_from_coordinates(self, latitude: float, longitude: float) -> str:
        """Get region name based on coordinates"""
        if 8.0 <= latitude <= 37.0 and 68.0 <= longitude <= 97.0:
            # India regions
            if 20.0 <= latitude <= 30.0 and 70.0 <= longitude <= 80.0:
                return "Western India"
            elif 10.0 <= latitude <= 20.0 and 70.0 <= longitude <= 80.0:
                return "Southern India"
            elif 20.0 <= latitude <= 30.0 and 80.0 <= longitude <= 90.0:
                return "Central India"
            elif 20.0 <= latitude <= 30.0 and 90.0 <= longitude <= 100.0:
                return "Eastern India"
            elif 30.0 <= latitude <= 37.0 and 70.0 <= longitude <= 80.0:
                return "Northern India"
            else:
                return "India"
        else:
            return "International"

# Global instance
geocoding_service = GeocodingService() 