from django.core.management.base import BaseCommand
from itineraries.models import Place
from django.conf import settings
import googlemaps
import random

class Command(BaseCommand):
    help = '제주도 관광지 테스트 데이터 생성'

    def handle(self, *args, **kwargs):
        gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

        # 제주도 주요 관광지 데이터
        places_data = [
            {
                'name': '성산일출봉',
                'category': 'ATTRACTION',
                'location': '제주특별자치도 서귀포시 성산읍 일출로 284-12',
                'coords': {'lat': 33.4587, 'lng': 126.9425},
                'description': '유네스코 세계자연유산으로 등재된 제주의 랜드마크. 일출 명소로 유명한 화산체.'
            },
            {
                'name': '만장굴',
                'category': 'ATTRACTION',
                'location': '제주특별자치도 제주시 구좌읍 만장굴길 182',
                'coords': {'lat': 33.5284, 'lng': 126.7714},
                'description': '총 길이가 약 7.4km에 달하는 세계적인 규모의 용암동굴.'
            },
            {
                'name': '한라산 국립공원',
                'category': 'NATURE',
                'location': '제주특별자치도 제주시 1100로 2070-61',
                'coords': {'lat': 33.3616, 'lng': 126.5292},
                'description': '한국에서 가장 높은 산으로, 사계절 아름다운 경관을 자랑하는 제주의 상징.'
            },
            {
                'name': '천지연폭포',
                'category': 'NATURE',
                'location': '제주특별자치도 서귀포시 천지동 667-7',
                'coords': {'lat': 33.2444, 'lng': 126.5544},
                'description': '서귀포 시내에 위치한 높이 22m의 아름다운 폭포.'
            },
            {
                'name': '우도',
                'category': 'ATTRACTION',
                'location': '제주특별자치도 제주시 우도면',
                'coords': {'lat': 33.5219, 'lng': 126.9514},
                'description': '소가 누워있는 모양을 닮은 섬으로, 아름다운 해변과 경관을 자랑하는 관광지.'
            },
            {
                'name': '협재해수욕장',
                'category': 'BEACH',
                'location': '제주특별자치도 제주시 한림읍 협재리 2497-1',
                'coords': {'lat': 33.3940, 'lng': 126.2397},
                'description': '맑은 에메랄드빛 바다와 고운 모래가 매력적인 해수욕장.'
            },
            {
                'name': '함덕해수욕장',
                'category': 'BEACH',
                'location': '제주특별자치도 제주시 조천읍 조함해안로 519-10',
                'coords': {'lat': 33.5434, 'lng': 126.6691},
                'description': '제주 동부 해안의 대표적인 해수욕장으로 백사장과 수심이 얕은 것이 특징.'
            },
            {
                'name': '중문색달해수욕장',
                'category': 'BEACH',
                'location': '제주특별자치도 서귀포시 중문관광로72번길 29-1',
                'coords': {'lat': 33.2444, 'lng': 126.4125},
                'description': '제주 최대 규모의 종합 해양 리조트가 있는 아름다운 해변.'
            },
            {
                'name': '제주민속촌',
                'category': 'ATTRACTION',
                'location': '제주특별자치도 서귀포시 표선면 민속해안로 631-34',
                'coords': {'lat': 33.3213, 'lng': 126.8419},
                'description': '제주의 전통 문화와 생활상을 체험할 수 있는 민속촌.'
            },
            {
                'name': '섭지코지',
                'category': 'NATURE',
                'location': '제주특별자치도 서귀포시 성산읍 섭지코지로',
                'coords': {'lat': 33.4239, 'lng': 126.9285},
                'description': '드라마 촬영지로 유명한 해안가 관광지, 아름다운 해안절경.'
            },
            {
                'name': '용머리해안',
                'category': 'NATURE',
                'location': '제주특별자치도 서귀포시 안덕면 사계리',
                'coords': {'lat': 33.2344, 'lng': 126.3142},
                'description': '용의 머리를 닮은 독특한 지형의 해안가.'
            },
            {
                'name': '오설록티뮤지엄',
                'category': 'ATTRACTION',
                'location': '제주특별자치도 서귀포시 안덕면 신화역사로 15',
                'coords': {'lat': 33.3066, 'lng': 126.2899},
                'description': '푸른 차밭과 함께 제주 차 문화를 체험할 수 있는 곳.'
            },
            {
                'name': '카멜리아힐',
                'category': 'NATURE',
                'location': '제주특별자치도 서귀포시 안덕면 병악로 166',
                'coords': {'lat': 33.2887, 'lng': 126.3708},
                'description': '동양에서 가장 큰 동백꽃 정원.'
            },
            {
                'name': '비자림',
                'category': 'NATURE',
                'location': '제주특별자치도 제주시 구좌읍 비자숲길 55',
                'coords': {'lat': 33.4894, 'lng': 126.8059},
                'description': '천연기념물로 지정된 아름다운 비자나무 숲.'
            },
            {
                'name': '사려니숲길',
                'category': 'NATURE',
                'location': '제주특별자치도 제주시 조천읍 교래리',
                'coords': {'lat': 33.4071, 'lng': 126.6373},
                'description': '울창한 숲이 있는 아름다운 산책로.'
            },
            {
                'name': '월정리해변',
                'category': 'BEACH',
                'location': '제주특별자치도 제주시 구좌읍 월정리',
                'coords': {'lat': 33.5552, 'lng': 126.7959},
                'description': '에메랄드빛 바다와 하얀 모래가 인상적인 해변.'
            },
            {
                'name': '금오름',
                'category': 'NATURE',
                'location': '제주특별자치도 제주시 한림읍 금악리',
                'coords': {'lat': 33.3589, 'lng': 126.3059},
                'description': '제주의 아름다운 오름 중 하나로 일몰이 특히 아름다움.'
            },
            {
                'name': '제주4.3평화공원',
                'category': 'ATTRACTION',
                'location': '제주특별자치도 제주시 명림로 430',
                'coords': {'lat': 33.4500, 'lng': 126.5722},
                'description': '제주4.3사건의 역사를 기억하고 평화를 기원하는 공간.'
            },
            {
                'name': '걸매생태공원',
                'category': 'NATURE',
                'location': '제주특별자치도 서귀포시 중문관광로 227-24',
                'coords': {'lat': 33.2547, 'lng': 126.4251},
                'description': '아름다운 습지생태공원으로 다양한 식물과 새들을 관찰할 수 있는 곳.'
            },
            {
                'name': '산방산',
                'category': 'NATURE',
                'location': '제주특별자치도 서귀포시 안덕면 사계리',
                'coords': {'lat': 33.2369, 'lng': 126.3127},
                'description': '제주도의 대표적인 산으로 웅장한 모습을 자랑하는 종상화산.'
            }
        ]

        # 추가 장소 데이터
        additional_locations = [
            {'name': '제주시내', 'coords': {'lat': 33.4996, 'lng': 126.5312}},
            {'name': '서귀포시내', 'coords': {'lat': 33.2496, 'lng': 126.5219}},
            {'name': '구좌읍', 'coords': {'lat': 33.5205, 'lng': 126.8555}},
            {'name': '애월읍', 'coords': {'lat': 33.4629, 'lng': 126.3114}}
        ]

        # 각 지역에서 주변 장소 검색
        for location in additional_locations:
            places_result = gmaps.places_nearby(
                location=location['coords'],
                radius=3000,
                type='tourist_attraction',
                language='ko'
            )

            if places_result.get('results'):
                for place in places_result['results'][:5]:  # 각 지역당 5개
                    place_details = gmaps.place(place['place_id'])['result']
                    
                    category = 'ATTRACTION'
                    if any(keyword in place.get('types', []) for keyword in ['park', 'natural_feature']):
                        category = 'NATURE'
                    elif 'beach' in place.get('types', []):
                        category = 'BEACH'

                    places_data.append({
                        'name': place['name'],
                        'category': category,
                        'location': place.get('vicinity', '제주도'),
                        'coords': place['geometry']['location'],
                        'description': f"제주도의 매력적인 관광지 {place['name']}입니다. {place.get('rating', '0')}점의 평점을 받은 인기 명소입니다."
                    })

        # Place 객체 생성
        created_count = 0
        for place_data in places_data:
            # 중복 체크
            if not Place.objects.filter(name=place_data['name']).exists():
                Place.objects.create(
                    name=place_data['name'],
                    place_type=place_data['category'],  # category -> place_type
                    address=place_data['location'],     # location -> address
                    latitude=place_data['coords']['lat'],
                    longitude=place_data['coords']['lng'],
                    description=place_data['description']
                )
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'생성된 장소: {place_data["name"]} ({place_data["category"]})'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'총 {created_count}개의 제주도 관광지 데이터가 생성되었습니다.'
            )
        )
