from typing import List, Dict
import openai
from django.conf import settings

class AIRecommendationService:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY

    def generate_itinerary(self, preferences: Dict) -> Dict:
        """사용자 선호도 기반 여행 일정 생성"""
        prompt = self._create_prompt(preferences)
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        return self._parse_response(response)

    def _create_prompt(self, preferences: Dict) -> str:
        # 프롬프트 생성 로직
        return f"다음 선호도를 바탕으로 여행 일정을 만들어주세요: {preferences}"

    def _parse_response(self, response) -> Dict:
        # GPT 응답 파싱 로직
        return {
            "itinerary": response.choices[0].message.content,
            "recommended_places": []
        }
