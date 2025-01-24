from django.core.management.base import BaseCommand
from django.conf import settings
import googlemaps
import random
from stays.models import Stay
from django.core.files import File
import requests
from tempfile import NamedTemporaryFile
import time

class Command(BaseCommand):
    help = '제주도 지역 샘플 숙소 데이터 생성'

    def handle(self, *args, **kwargs):
        gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

        # 제주도 주요 지역 정의
        jeju_locations = [
            {'name': '제주시', 'coords': {'lat': 33.4996, 'lng': 126.5312}},
            {'name': '서귀포시', 'coords': {'lat': 33.2496, 'lng': 126.5219}},
            {'name': '애월읍', 'coords': {'lat': 33.4629, 'lng': 126.3114}},
            {'name': '중문관광단지', 'coords': {'lat': 33.2444, 'lng': 126.4125}},
            {'name': '성산일출봉', 'coords': {'lat': 33.4587, 'lng': 126.9425}},
            {'name': '함덕해수욕장', 'coords': {'lat': 33.5434, 'lng': 126.6691}},
            {'name': '협재해수욕장', 'coords': {'lat': 33.3940, 'lng': 126.2397}},
        ]

        # 숙소 유형별 가격을 단일 가격으로 고정
        accommodation_types = [
            ('리조트', 150000),
            ('호텔', 130000),
            ('풀빌라', 180000),
            ('펜션', 100000),
            ('게스트하우스', 40000),
        ]

        amenities_pool = {
            'wifi': '무료 와이파이',
            'parking': '무료 주차',
            'pool': '수영장',
            'breakfast': '조식 포함',
            'fitness': '피트니스 센터',
            'spa': '스파',
            'restaurant': '레스토랑',
            'bar': '바/라운지',
            'beach_access': '해변 접근성',
            'bbq': 'BBQ 시설',
            'ocean_view': '오션뷰',
            'terrace': '테라스/발코니',
            'cafe': '카페',
            'rental_car': '렌터카 서비스',
            'tour_desk': '투어 데스크',
        }

        created_count = 0
        attempts = 0
        max_attempts = 100

        while created_count < 50 and attempts < max_attempts:
            location = random.choice(jeju_locations)
            
            try:
                places_result = gmaps.places_nearby(
                    location=location['coords'],
                    radius=5000,
                    type='lodging',
                    language='ko'
                )

                if not places_result.get('results'):
                    continue

                for place in places_result['results']:
                    if created_count >= 50:
                        break

                    # 상세 정보 가져오기
                    place_details = gmaps.place(place['place_id'])['result']
                    
                    acc_type, fixed_price = random.choice(accommodation_types)
                    
                    # 기본 정보 설정
                    stay_data = {
                        'name': place.get('name', f'제주 {location["name"]} {acc_type}'),
                        'description': f'''
                        {location["name"]}에 위치한 아름다운 {acc_type}입니다.
                        제주의 향취를 느낄 수 있는 최적의 위치에 자리잡고 있으며,
                        {random.choice(['바다 전망이 아름답고', '한라산 전망이 시원하고', '주변 관광지와 가깝고'])}
                        편안한 휴식을 제공합니다.
                        '''.strip(),
                        'location': place.get('vicinity', f'제주도 {location["name"]}'),
                        'price': fixed_price,  # 고정된 가격 사용
                        'capacity': random.randint(2, 8),
                        'latitude': place['geometry']['location']['lat'],
                        'longitude': place['geometry']['location']['lng'],
                        'rating': round(random.uniform(4.0, 5.0), 1),
                    }

                    # 편의시설 선택 (타입별 특성 반영)
                    selected_amenities = {}
                    if acc_type in ['리조트', '호텔']:
                        # 고급 숙소는 더 많은 편의시설 보유
                        selected_amenities = {k: v for k, v in amenities_pool.items() 
                                           if random.random() > 0.3}
                    else:
                        # 그 외 숙소는 기본적인 편의시설만
                        selected_amenities = {k: v for k, v in amenities_pool.items() 
                                           if random.random() > 0.6}
                    
                    stay_data['amenities'] = selected_amenities

                    # Stay 객체 생성
                    stay = Stay.objects.create(**stay_data)

                    # 이미지 처리
                    if 'photos' in place:
                        photo_reference = place['photos'][0]['photo_reference']
                        photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={photo_reference}&key={settings.GOOGLE_MAPS_API_KEY}"
                        
                        try:
                            response = requests.get(photo_url)
                            if response.status_code == 200:
                                img_temp = NamedTemporaryFile(delete=True)
                                img_temp.write(response.content)
                                img_temp.flush()
                                
                                filename = f"jeju_stay_{stay.id}.jpg"
                                stay.image.save(filename, File(img_temp), save=True)
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f'이미지 저장 실패: {e}'))

                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'[{created_count}/50] 생성된 숙소: {stay.name} ({location["name"]})'
                        )
                    )

                # API 호출 제한 고려
                time.sleep(0.5)

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'오류 발생: {str(e)}'))
                attempts += 1
                time.sleep(1)

        self.stdout.write(
            self.style.SUCCESS(
                f'총 {created_count}개의 제주도 숙소 데이터 생성 완료'
            )
        )
