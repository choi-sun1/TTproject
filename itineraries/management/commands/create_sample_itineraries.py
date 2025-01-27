from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from itineraries.models import Itinerary, ItineraryDay, Place, ItineraryPlace
from datetime import timedelta, date

class Command(BaseCommand):
    help = '샘플 여행 일정을 생성합니다.'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        admin_user = User.objects.filter(is_superuser=True).first()

        if not admin_user:
            self.stdout.write(self.style.ERROR('관리자 계정이 필요합니다.'))
            return

        # 샘플 장소 데이터
        sample_places = {
            'seoul': [
                {
                    'name': '경복궁',
                    'category': 'attraction',
                    'description': '조선시대의 대표적인 궁궐',
                    'address': '서울특별시 종로구 사직로 161',
                    'latitude': '37.579617',
                    'longitude': '126.977041',
                },
                {
                    'name': '남산서울타워',
                    'category': 'attraction',
                    'description': '서울의 상징적인 타워',
                    'address': '서울특별시 용산구 남산공원길 105',
                    'latitude': '37.551168',
                    'longitude': '126.988228',
                },
                {
                    'name': '명동',
                    'category': 'shopping',
                    'description': '쇼핑과 음식의 중심지',
                    'address': '서울특별시 중구 명동길',
                    'latitude': '37.563826',
                    'longitude': '126.983819',
                }
            ],
            'busan': [
                {
                    'name': '해운대 해수욕장',
                    'category': 'attraction',
                    'description': '부산의 대표적인 해변',
                    'address': '부산광역시 해운대구 해운대해변로 264',
                    'latitude': '35.158795',
                    'longitude': '129.160728',
                },
                {
                    'name': '감천문화마을',
                    'category': 'attraction',
                    'description': '부산의 마추피추',
                    'address': '부산광역시 사하구 감내2로 203',
                    'latitude': '35.097859',
                    'longitude': '129.010838',
                }
            ],
            'jeju': [
                {
                    'name': '성산일출봉',
                    'category': 'attraction',
                    'description': '유네스코 세계자연유산',
                    'address': '제주특별자치도 서귀포시 성산읍 성산리',
                    'latitude': '33.458228',
                    'longitude': '126.942316',
                },
                {
                    'name': '만장굴',
                    'category': 'attraction',
                    'description': '세계적인 용암동굴',
                    'address': '제주특별자치도 제주시 구좌읍 만장굴길 182',
                    'latitude': '33.528077',
                    'longitude': '126.771408',
                }
            ]
        }

        # 샘플 일정 데이터
        sample_itineraries = [
            {
                'title': '서울 3일 여행',
                'description': '서울의 주요 관광지를 둘러보는 코스',
                'region': 'seoul',
                'duration': 3,
                'places': sample_places['seoul']
            },
            {
                'title': '부산 2일 여행',
                'description': '부산의 핵심 명소 탐방',
                'region': 'busan',
                'duration': 2,
                'places': sample_places['busan']
            },
            {
                'title': '제주도 4일 여행',
                'description': '제주도의 아름다운 자연 탐방',
                'region': 'jeju',
                'duration': 4,
                'places': sample_places['jeju']
            }
        ]

        for itinerary_data in sample_itineraries:
            try:
                # 일정 생성
                start_date = date.today()
                end_date = start_date + timedelta(days=itinerary_data['duration']-1)
                
                itinerary = Itinerary.objects.create(
                    author=admin_user,
                    title=itinerary_data['title'],
                    description=itinerary_data['description'],
                    start_date=start_date,
                    end_date=end_date,
                    is_sample=True,
                    is_public=True
                )

                # 일차별 데이터 생성
                for day_num in range(1, itinerary_data['duration'] + 1):
                    day = ItineraryDay.objects.create(
                        itinerary=itinerary,
                        day_number=day_num,
                        date=start_date + timedelta(days=day_num-1)
                    )

                    # 해당 일차의 장소들 생성
                    for idx, place_data in enumerate(itinerary_data['places'], 1):
                        # 장소 생성 또는 가져오기
                        place, _ = Place.objects.get_or_create(
                            name=place_data['name'],
                            defaults={
                                'category': place_data['category'],
                                'description': place_data['description'],
                                'address': place_data['address'],
                                'latitude': place_data['latitude'],
                                'longitude': place_data['longitude'],
                            }
                        )

                        # 일정에 장소 추가
                        ItineraryPlace.objects.create(
                            day=day,
                            place=place,
                            order=idx
                        )

                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created sample itinerary: {itinerary.title}')
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to create itinerary: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS('Sample itineraries created successfully!')
        )
