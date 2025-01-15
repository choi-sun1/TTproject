import requests
from django.conf import settings
from .models import Stay
from decimal import Decimal
import random

def fetch_hotels_from_google():
    # 한국 주요 도시 좌표
    cities = [
        {"name": "서울", "lat": 37.5665, "lng": 126.9780},
        {"name": "부산", "lat": 35.1796, "lng": 129.0756},
        {"name": "제주", "lat": 33.4996, "lng": 126.5312},
        {"name": "강릉", "lat": 37.7519, "lng": 128.8760},
        {"name": "전주", "lat": 35.8242, "lng": 127.1480}
    ]

    api_key = settings.GOOGLE_MAPS_API_KEY
    results = []

    for city in cities:
        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            'location': f"{city['lat']},{city['lng']}",
            'radius': '5000',  # 5km 반경
            'type': 'lodging',  # 숙박시설
            'language': 'ko',   # 한국어 결과
            'key': api_key
        }

        response = requests.get(url, params=params)
        data = response.json()

        if data.get('results'):
            for place in data['results']:
                # 가격은 임의로 설정 (실제로는 다른 API나 크롤링이 필요할 수 있음)
                price = random.randint(80000, 300000)
                
                stay = Stay.objects.create(
                    name=place['name'],
                    address=place.get('vicinity', '주소 정보 없음'),
                    latitude=place['geometry']['location']['lat'],
                    longitude=place['geometry']['location']['lng'],
                    description=f"{city['name']}에 위치한 {place['name']}입니다. 편안한 숙박을 제공합니다.",
                    price_per_night=Decimal(price)
                )
                results.append(stay)

    return results
