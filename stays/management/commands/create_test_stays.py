from django.core.management.base import BaseCommand
from stays.models import Stay
from django.core.files import File
from pathlib import Path

class Command(BaseCommand):
    help = '테스트용 숙소 데이터 생성'

    def handle(self, *args, **kwargs):
        test_stays = [
            {
                'name': '서울 시티 호텔',
                'description': '서울 중심부에 위치한 현대적인 호텔',
                'location': '서울시 중구',
                'price': 150000,
                'capacity': 2,
                'amenities': {
                    'wifi': True,
                    'parking': True,
                    'breakfast': True
                }
            },
            # 필요한 만큼 더 추가
        ]

        for stay_data in test_stays:
            Stay.objects.create(**stay_data)
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created stay "{stay_data["name"]}"')
            )
