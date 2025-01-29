from typing import List, Dict
from .services.gpt import GPTService

def get_travel_recommendations() -> List[Dict]:
    """여행지 추천 기능"""
    gpt_service = GPTService()
    recommendations = gpt_service.get_travel_recommendations({
        'type': 'tourist',
        'preferences': ['nature', 'culture', 'food']
    })
    return parse_recommendations(recommendations)

def get_food_recommendations() -> List[Dict]:
    """맛집 추천 기능"""
    gpt_service = GPTService()
    recommendations = gpt_service.get_food_recommendations('서울')
    return parse_recommendations(recommendations)

def parse_recommendations(response: str) -> List[Dict]:
    """GPT 응답을 파싱하여 구조화된 데이터로 변환"""
    try:
        # 실제 구현에서는 GPT 응답을 파싱하는 로직 추가
        return [
            {
                'name': '추천 장소 1',
                'description': '설명 1',
                'rating': 4.5
            },
            {
                'name': '추천 장소 2',
                'description': '설명 2',
                'rating': 4.3
            }
        ]
    except Exception as e:
        return []
