try:
    import googlemaps
except ImportError:
    googlemaps = None
from django.conf import settings
from typing import Dict, List

class GoogleMapsService:
    def __init__(self, api_key=None):
        self.client = None
        if googlemaps and api_key:
            self.client = googlemaps.Client(key=api_key)
    
    def get_place_details(self, place_id: str) -> Dict:
        """특정 장소의 상세 정보 조회"""
        if not self.client:
            return {"error": "Google Maps service not available"}
        try:
            return self.client.place(place_id)
        except Exception as e:
            return {"error": str(e)}
    
    def search_nearby(self, location: Dict[str, float], radius: int = 1000) -> List[Dict]:
        """주변 숙박시설 검색"""
        if not self.client:
            return {"error": "Google Maps service not available"}
        try:
            return self.client.places_nearby(
                location=location,
                radius=radius,
                type='lodging'
            )
        except Exception as e:
            return {"error": str(e)}

    def get_directions(self, origin: Dict[str, float], destination: Dict[str, float]) -> Dict:
        """경로 정보 조회"""
        if not self.client:
            return {"error": "Google Maps service not available"}
        try:
            return self.client.directions(
                origin=origin,
                destination=destination,
                mode="transit",
                language="ko"
            )
        except Exception as e:
            return {"error": str(e)}
