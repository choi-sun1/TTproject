from django.shortcuts import render
from .models import ChatHistory, Location, Review
from .forms import ChatForm
from openai import OpenAI
import requests
from django.conf import settings

# OpenAI API 키
CLIENT = OpenAI(api_key=settings.OPENAI_API_KEY)
GOOGLE_MAPS_API_KEY = settings.GOOGLE_PLACES_API_KEY

def chat_view(request):
    completion = None
    prompt = '''
    너는 여행 계획을 돕는 챗봇이야.
    국내 여행만을 대상으로 도와줄 수 있어.'''
    if request.method == "POST":
        form = ChatForm(request.POST)
        if form.is_valid():
            user_message = form.cleaned_data["user_message"]

            # OpenAI API와 통신
            completion = CLIENT.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system",
                    "content": prompt},
                    {"role": "user",
                    "content": user_message
                    }
                ]
            )
            bot_response = completion.choices[0].message.content

            # Google Maps API를 사용하여 장소 찾기
            if "place" in user_message.lower():  # 예제 조건
                google_maps_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={user_message}&key={GOOGLE_MAPS_API_KEY}"
                place_data = requests.get(google_maps_url).json()
                if place_data.get("results"):
                    place = place_data["results"][0]
                    location = Location.objects.create(
                        name=place["name"],
                        address=place["formatted_address"],
                        latitude=place["geometry"]["location"]["lat"],
                        longitude=place["geometry"]["location"]["lng"],
                    )
                    bot_response += f"\n추천 장소: {location.name}, {location.address}"

            # 대화 기록 저장
            ChatHistory.objects.create(user_message=user_message, bot_response=bot_response)

    else:
        form = ChatForm()

    chat_history = ChatHistory.objects.all().order_by("-timestamp")[:10]  # 최근 대화 10개 표시
    return render(request, "chatbot/chatbot.html", {"form": form, "response": completion, "chat_history": chat_history})
