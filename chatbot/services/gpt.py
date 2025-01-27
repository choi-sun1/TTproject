import openai
from django.conf import settings
from django.core.cache import cache
from typing import Dict, List, Optional, Any
import json

class GPTService:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.embeddings_cache = {}

    def _get_context(self, query: str) -> str:
        # RAG: 관련 컨텍스트 검색
        cached_data = cache.get(f"context_{query}")
        if cached_data:
            return cached_data
        
        # 실제 구현에서는 벡터 DB나 다른 저장소에서 관련 데이터 검색
        context = "여행 관련 컨텍스트"
        cache.set(f"context_{query}", context, timeout=3600)
        return context

    def get_response(self, message: str) -> str:
        try:
            context = self._get_context(message)
            messages = [
                {"role": "system", "content": "당신은 여행 전문가입니다. 다음 컨텍스트를 참고하여 답변해주세요:\n" + context},
                {"role": "user", "content": message}
            ]
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                **settings.GPT_SETTINGS
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"죄송합니다. 오류가 발생했습니다: {str(e)}"

    def get_travel_recommendations(self, preferences):
        prompt = f"다음 선호도를 바탕으로 여행지를 추천해주세요: {preferences}"
        return self.get_response(prompt)

    def get_food_recommendations(self, location):
        prompt = f"{location}의 맛집을 추천해주세요."
        return self.get_response(prompt)

def generate_chat_response(messages: List[Dict[str, str]]) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"죄송합니다. 오류가 발생했습니다: {str(e)}"

def generate_travel_recommendation(
    destination: str,
    duration: int,
    preferences: Dict[str, Any],
    budget: str = "중간"
) -> Dict[str, Any]:
    """여행 추천 생성"""
    prompt = f"""
    다음 조건에 맞는 여행 일정을 추천해주세요:
    - 목적지: {destination}
    - 기간: {duration}일
    - 예산: {budget}
    - 선호도: {json.dumps(preferences, ensure_ascii=False)}
    
    다음 형식으로 응답해주세요:
    {{
        "일정": [
            {{
                "일차": 1,
                "장소": ["장소1", "장소2", "..."],
                "설명": "해당 일차 일정에 대한 설명"
            }}
        ],
        "예상비용": "예상되는 총 비용",
        "추천이유": "이 일정을 추천하는 이유"
    }}
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )
        
        # JSON 형식으로 파싱
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        return {
            "error": f"추천 생성 중 오류가 발생했습니다: {str(e)}",
            "일정": [],
            "예상비용": "알 수 없음",
            "추천이유": "추천을 생성할 수 없습니다."
        }

def generate_food_recommendation(
    location: str,
    cuisine_type: str = None,
    dietary_restrictions: List[str] = None
) -> List[Dict[str, Any]]:
    """음식점 추천 생성"""
    restrictions = ', '.join(dietary_restrictions) if dietary_restrictions else '없음'
    prompt = f"""
    다음 조건에 맞는 맛집을 추천해주세요:
    - 위치: {location}
    - 음식 종류: {cuisine_type if cuisine_type else '전체'}
    - 식이 제한: {restrictions}
    
    다음 형식으로 응답해주세요:
    [
        {{
            "이름": "식당 이름",
            "음식종류": "음식 카테고리",
            "대표메뉴": ["메뉴1", "메뉴2"],
            "가격대": "가격 범위",
            "추천이유": "추천 이유"
        }}
    ]
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        
        # JSON 형식으로 파싱
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        return [{
            "error": f"추천 생성 중 오류가 발생했습니다: {str(e)}",
            "이름": "알 수 없음",
            "음식종류": "알 수 없음",
            "대표메뉴": [],
            "가격대": "알 수 없음",
            "추천이유": "추천을 생성할 수 없습니다."
        }]
