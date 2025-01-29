from django.core.management.base import BaseCommand
from itineraries.models import Place
from django.conf import settings
import googlemaps
import time
import json
from django.db import IntegrityError

class Command(BaseCommand):
    help = '제주도 관광지와 숙소 데이터 생성'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='기존 제주도 데이터 삭제',
        )

    def handle(self, *args, **kwargs):
        try:
            gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
            
            # 제주도 주요 지역들
            jeju_locations = [
                {'name': '제주시', 'lat': 33.4996, 'lng': 126.5312},
                {'name': '서귀포시', 'lat': 33.2539, 'lng': 126.5600},
                {'name': '애월읍', 'lat': 33.4629, 'lng': 126.3119},
                {'name': '성산일출봉', 'lat': 33.4582, 'lng': 126.9425},
                {'name': '중문관광단지', 'lat': 33.2444, 'lng': 126.4125}
            ]

            # 검색 키워드
            keywords = {
                'attraction': [
                    '제주 관광명소', '제주 해변', '제주 오름', '제주 폭포',
                    '제주 박물관', '제주 동굴', '제주 절', '제주 테마파크',
                    '제주 카페', '제주 올레길'
                ],
                'accommodation': [
                    '제주 호텔', '제주 리조트', '제주 펜션',
                    '제주 풀빌라', '제주 게스트하우스', '제주 콘도'
                ]
            }

            # 기존 데이터 삭제
            if kwargs['clear']:
                deleted_count = Place.objects.filter(address__contains='제주').delete()[0]
                self.stdout.write(f'Deleted {deleted_count} existing places')

            created_places = {
                'attraction': 0,
                'accommodation': 0
            }

            for location in jeju_locations:
                self.stdout.write(f"\nSearching in {location['name']}...")
                
                for place_type, search_keywords in keywords.items():
                    for keyword in search_keywords:
                        try:
                            # 장소 검색
                            results = gmaps.places(
                                keyword,
                                location=(location['lat'], location['lng']),
                                radius=10000,  # 10km 반경
                                language='ko',
                                type='point_of_interest'
                            )

                            for place in results['results']:
                                try:
                                    # 중복 체크
                                    if Place.objects.filter(google_place_id=place['place_id']).exists():
                                        continue

                                    # 상세 정보 가져오기
                                    details = gmaps.place(place['place_id'], language='ko')['result']
                                    
                                    # 장소 데이터 생성
                                    Place.objects.create(
                                        name=place['name'],
                                        place_type=place_type,
                                        address=details.get('formatted_address', ''),
                                        latitude=place['geometry']['location']['lat'],
                                        longitude=place['geometry']['location']['lng'],
                                        rating=place.get('rating', 0.0),
                                        google_place_id=place['place_id'],
                                        description=details.get('editorial_summary', {}).get('overview', ''),
                                        phone_number=details.get('formatted_phone_number', ''),
                                        website=details.get('website', ''),
                                        extra_info={
                                            'types': place['types'],
                                            'price_level': details.get('price_level', 0),
                                            'reviews_count': place.get('user_ratings_total', 0),
                                            'photos': [photo.get('photo_reference') for photo in place.get('photos', [])[:3]],
                                            'opening_hours': details.get('opening_hours', {}).get('weekday_text', []),
                                            'vicinity': place.get('vicinity', '')
                                        }
                                    )
                                    
                                    created_places[place_type] += 1
                                    self.stdout.write(f"Created {place['name']} ({place_type})")

                                except IntegrityError:
                                    continue
                                except Exception as e:
                                    self.stderr.write(f"Error creating place {place['name']}: {str(e)}")

                            # API 제한 고려
                            time.sleep(2)

                        except Exception as e:
                            self.stderr.write(f"Error processing keyword {keyword}: {str(e)}")
                            continue

            self.stdout.write(self.style.SUCCESS(
                f"\nSuccessfully created {created_places['attraction']} attractions and "
                f"{created_places['accommodation']} accommodations"
            ))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Failed to generate data: {str(e)}'))
