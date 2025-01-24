from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
from itineraries.models import Itinerary, ItineraryDay, ItineraryPlace, Place
from stays.models import Stay
import googlemaps
import random
from datetime import datetime, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = '제주도 여행 일정 테스트 데이터 생성'

    def handle(self, *args, **kwargs):
        # Google Maps 클라이언트 초기화
        gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

        # 제주도 주요 관광지 정의
        jeju_attractions = [
            {
                'name': '성산일출봉',
                'location': '제주특별자치도 서귀포시 성산읍 성산리',
                'coords': {'lat': 33.4587, 'lng': 126.9425},
                'category': 'ATTRACTION',
                'description': '유네스코 세계자연유산으로 등재된 제주의 대표적인 관광지'
            },
            {
                'name': '만장굴',
                'location': '제주특별자치도 제주시 구좌읍 만장굴길 182',
                'coords': {'lat': 33.5284, 'lng': 126.7714},
                'category': 'ATTRACTION',
                'description': '세계적으로 손꼽히는 용암동굴'
            },
            {
                'name': '우도',
                'location': '제주특별자치도 제주시 우도면',
                'coords': {'lat': 33.5219, 'lng': 126.9514},
                'category': 'ATTRACTION',
                'description': '소가 누워있는 형상을 닮은 제주의 가장 큰 부속섬'
            },
            {
                'name': '함덕해수욕장',
                'location': '제주특별자치도 제주시 조천읍 함덕리',
                'coords': {'lat': 33.5434, 'lng': 126.6691},
                'category': 'BEACH',
                'description': '에메랄드빛 바다가 아름다운 해변'
            },
            {
                'name': '협재해수욕장',
                'location': '제주특별자치도 제주시 한림읍 협재리',
                'coords': {'lat': 33.3940, 'lng': 126.2397},
                'category': 'BEACH',
                'description': '비취색 물빛이 아름다운 제주 대표 해변'
            },
            {
                'name': '한라산 국립공원',
                'location': '제주특별자치도 제주시 해발 1,950m',
                'coords': {'lat': 33.3616, 'lng': 126.5292},
                'category': 'NATURE',
                'description': '제주도의 상징이자 대한민국에서 가장 높은 산'
            },
        ]

        # 추가 장소 검색 및 데이터 보강
        for location in jeju_attractions:
            places_result = gmaps.places_nearby(
                location=location['coords'],
                radius=5000,
                language='ko'
            )

            if places_result.get('results'):
                for place_data in places_result['results'][:3]:  # 각 지역당 3개의 추가 장소
                    jeju_attractions.append({
                        'name': place_data['name'],
                        'location': place_data.get('vicinity', '제주도'),
                        'coords': place_data['geometry']['location'],
                        'category': 'ATTRACTION',
                        'description': f'제주도의 매력적인 관광지 {place_data["name"]}'
                    })

        # Place 객체 생성
        places = []
        for attraction in jeju_attractions:
            place = Place.objects.create(
                name=attraction['name'],
                description=attraction['description'],
                location=attraction['location'],
                latitude=attraction['coords']['lat'],
                longitude=attraction['coords']['lng'],
                category=attraction['category']
            )
            places.append(place)

        # 테스트 사용자 생성 또는 가져오기
        test_user, _ = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )

        # 여행 일정 생성 (10개의 다른 일정)
        for i in range(10):
            # 무작위 시작 날짜 (현재부터 3개월 이내)
            start_date = datetime.now().date() + timedelta(days=random.randint(1, 90))
            duration = random.randint(2, 5)  # 2-5일 일정
            end_date = start_date + timedelta(days=duration - 1)

            # 일정 생성
            itinerary = Itinerary.objects.create(
                author=test_user,
                title=f'제주도 {duration}일 여행 계획 {i+1}',
                description=f'{start_date.strftime("%Y년 %m월")} 제주도 여행',
                start_date=start_date,
                end_date=end_date,
                is_public=True
            )

            # 일자별 일정 생성
            for day_num in range(duration):
                current_date = start_date + timedelta(days=day_num)
                day = ItineraryDay.objects.create(
                    itinerary=itinerary,
                    day_number=day_num + 1,
                    date=current_date
                )

                # 각 날짜별 3-5개의 장소 무작위 선택
                day_places = random.sample(places, random.randint(3, 5))
                
                # 시간대 설정 (09:00부터 시작)
                current_time = datetime.strptime('09:00', '%H:%M')
                
                for idx, place in enumerate(day_places, 1):
                    # 각 장소별 1-3시간 소요
                    duration_hours = random.randint(1, 3)
                    end_time = current_time + timedelta(hours=duration_hours)
                    
                    ItineraryPlace.objects.create(
                        day=day,
                        place=place,
                        order=idx,
                        start_time=current_time.strftime('%H:%M'),
                        end_time=end_time.strftime('%H:%M'),
                        note=f'Day {day_num + 1}의 {idx}번째 방문지'
                    )
                    
                    # 다음 장소는 1시간 후부터 시작
                    current_time = end_time + timedelta(hours=1)

            self.stdout.write(
                self.style.SUCCESS(f'생성된 여행 일정: {itinerary.title}')
            )

        self.stdout.write(
            self.style.SUCCESS(f'총 {len(places)}개의 장소와 10개의 여행 일정이 생성되었습니다.')
        )
