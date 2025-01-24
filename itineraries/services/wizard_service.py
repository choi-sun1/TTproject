from datetime import timedelta, datetime
from ..models import (
    Itinerary, 
    ItineraryDay, 
    ItineraryPlace, 
    Place, 
    ItineraryExpense, 
    TravelChecklist
)

class ItineraryWizardService:
    def create_itinerary(self, user, wizard_data):
        # 기본 일정 생성
        itinerary = Itinerary.objects.create(
            user=user,
            destination=wizard_data['destination'],
            start_date=datetime.strptime(wizard_data['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(wizard_data['end_date'], '%Y-%m-%d').date()
        )

        # 선택된 장소들 추가
        for place_data in wizard_data['places']:
            Place.objects.create(
                itinerary=itinerary,
                name=place_data['name'],
                address=place_data['address'],
                latitude=place_data['lat'],
                longitude=place_data['lng']
            )

        return itinerary

class WizardService:
    @staticmethod
    def create_itinerary_from_wizard(user, wizard_data):
        """마법사 데이터로부터 일정 생성"""
        itinerary = Itinerary.objects.create(
            author=user,
            title=wizard_data['title'],
            start_date=wizard_data['start_date'],
            end_date=wizard_data['end_date'],
            is_public=wizard_data.get('is_public', True)
        )

        # 일별 일정 생성
        days = (itinerary.end_date - itinerary.start_date).days + 1
        for day_num in range(days):
            current_date = itinerary.start_date + timedelta(days=day_num)
            day = ItineraryDay.objects.create(
                itinerary=itinerary,
                day_number=day_num + 1,
                date=current_date
            )

            # 해당 일자의 장소들 추가
            day_places = wizard_data['schedule'].get(str(day_num + 1), [])
            for idx, place_data in enumerate(day_places, 1):
                ItineraryPlace.objects.create(
                    day=day,
                    place_id=place_data['place_id'],
                    order=idx,
                    start_time=place_data.get('start_time'),
                    end_time=place_data.get('end_time'),
                    category=place_data.get('category', 'ATTRACTION'),
                    note=place_data.get('note', '')
                )

        # 예산 정보 추가
        if 'budgets' in wizard_data:
            for category, amount in wizard_data['budgets'].items():
                ItineraryExpense.objects.create(
                    itinerary=itinerary,
                    category=category,
                    amount=amount
                )

        # 체크리스트 항목 추가
        if 'checklist' in wizard_data:
            for item in wizard_data['checklist']:
                TravelChecklist.objects.create(
                    itinerary=itinerary,
                    item=item
                )

        return itinerary

    @staticmethod
    def validate_wizard_data(data, step):
        """마법사 단계별 데이터 유효성 검사"""
        if step == 1:
            if not all(key in data for key in ['title', 'start_date', 'end_date']):
                raise ValueError("기본 정보가 누락되었습니다.")
        elif step == 2:
            if not data.get('places'):
                raise ValueError("최소 한 개 이상의 장소를 선택해야 합니다.")
        elif step == 3:
            if not data.get('schedule'):
                raise ValueError("일정 배치 정보가 누락되었습니다.")
        
        return True
