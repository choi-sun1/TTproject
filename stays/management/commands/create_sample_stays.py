from django.core.management.base import BaseCommand
from django.conf import settings
import googlemaps
import random
from stays.models import Stay
from django.core.files import File
import requests
from tempfile import NamedTemporaryFile
import os

class Command(BaseCommand):
    help = '샘플 숙소 데이터 생성'

    def handle(self, *args, **kwargs):
        # Google Maps 클라이언트 초기화
        gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

        # 주요 도시 목록
        cities = [
            {'name': '서울', 'location': '서울특별시', 'coords': {'lat': 37.5665, 'lng': 126.9780}},
            {'name': '부산', 'location': '부산광역시', 'coords': {'lat': 35.1796, 'lng': 129.0756}},
            {'name': '제주', 'location': '제주특별자치도', 'coords': {'lat': 33.4996, 'lng': 126.5312}},
            {'name': '강릉', 'location': '강릉시', 'coords': {'lat': 37.7519, 'lng': 128.8760}},
        ]

        # 숙소 유형
        accommodation_types = ['호텔', '리조트', '풀빌라', '펜션', '게스트하우스']

        # 편의시설 목록
        amenities = {
            'wifi': '무료 와이파이',
            'parking': '주차장',
            'pool': '수영장',
            'breakfast': '조식 포함',
            'fitness': '피트니스 센터',
            'spa': '스파',
            'restaurant': '레스토랑',
            'bar': '바/라운지',
            'ac': '에어컨',
            'tv': 'TV',
        }

        for city in cities:
            # 각 도시마다 5개의 숙소 생성
            for _ in range(5):
                # 구글맵스로 실제 호텔 검색
                places_result = gmaps.places_nearby(
                    location=city['coords'],
                    radius=5000,
                    type='lodging'
                )

                if places_result.get('results'):
                    place = random.choice(places_result['results'])
                    
                    # 상세 정보 가져오기
                    place_details = gmaps.place(place['place_id'])['result']
                    
                    # 가격 범위 설정
                    price_ranges = {
                        '호텔': (80000),
                        '리조트': (80000),
                        '풀빌라': (80000),
                        '펜션': (80000),
                        '게스트하우스': (80000),
                    }
                    
                    accommodation_type = random.choice(accommodation_types)
                    price_range = price_ranges[accommodation_type]
                    
                    # 숙소 기본 정보
                    stay_data = {
                        'name': place.get('name', f'{city["name"]} {accommodation_type}'),
                        'description': f'''
                        {city["name"]}에 위치한 {accommodation_type}입니다.
                        도심과 가까워 편리한 위치에 있으며, 깨끗하고 안락한 객실을 제공합니다.
                        {random.randint(3, 10)}층 규모의 건물에 총 {random.randint(20, 100)}개의 객실이 있습니다.
                        ''',
                        'location': place.get('vicinity', city['location']),
                        'price': random.randint(price_range[0], price_range[1]),
                        'capacity': random.randint(2, 6),
                        'latitude': place['geometry']['location']['lat'],
                        'longitude': place['geometry']['location']['lng'],
                        'rating': round(random.uniform(3.5, 5.0), 1),
                    }

                    # 랜덤 편의시설 선택
                    selected_amenities = {k: v for k, v in amenities.items() 
                                       if random.choice([True, False])}
                    stay_data['amenities'] = selected_amenities

                    # Stay 객체 생성
                    stay = Stay.objects.create(**stay_data)

                    # Google Place 사진 가져오기 시도
                    if 'photos' in place:
                        photo_reference = place['photos'][0]['photo_reference']
                        photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={photo_reference}&key={settings.GOOGLE_MAPS_API_KEY}"
                        
                        try:
                            response = requests.get(photo_url)
                            if response.status_code == 200:
                                img_temp = NamedTemporaryFile(delete=True)
                                img_temp.write(response.content)
                                img_temp.flush()
                                
                                filename = f"stay_{stay.id}_main.jpg"
                                stay.image.save(filename, File(img_temp), save=True)
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f'이미지 저장 실패: {e}'))

                    self.stdout.write(self.style.SUCCESS(f'생성된 숙소: {stay.name}'))
