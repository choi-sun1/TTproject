from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from openai import OpenAI
from .models import Conversation
from .forms import ChatForm
from django.http import StreamingHttpResponse
import time
import re

CLIENT = OpenAI(api_key=settings.OPENAI_API_KEY)

# def remove_markdown(text):
#     text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
#     text = re.sub(r'\*(.*?)\*', r'\1', text)
#     text = re.sub(r'`(.*?)`', r'\1', text)
#     text = re.sub(r'#+\s', '', text)
#     text = re.sub(r'(\n- |\n\*)', '\n', text)
#     text = text.replace('•', '')
#     text = re.sub(r'(\d+\.\s)', '', text)
#     text = re.sub(r'\n\s*\n', '\n', text)
#     return text.strip()

@login_required
def chat_view(request):
    if request.method == 'GET':
        show_history = request.GET.get('show_history', 'false') == 'true'
        conversations = Conversation.objects.filter(user=request.user).order_by('timestamp') if show_history else []
        return render(request, 'chatbot/chat.html', {'conversations': conversations, 'form': ChatForm(), 'show_history': show_history})

    prompt = '''
    응답을 반드시 **일반 텍스트 형식**으로 작성해야 합니다.

    1. 문장을 **줄글로 이어쓰지 말고, 문단 단위로 구분하세요.**  
    2. 각 문단 사이에 **한 줄(`\n`)의 빈 줄을 추가하세요.**
    3. 문장은 완전한 형태로 작성하고, 문단을 **짧고 간결하게 유지하세요.**
    4. 텍스트만 사용하고, 마크다운을 **절대 포함하지 마세요.**

    예제:
    ---
    사용자: 서울 2박 3일 여행 일정을 추천해줘.
    AI:
    강릉에서의 1박 2일 여행은 정말 멋진 선택이에요!

첫째 날 일정을 추천해볼게요:

오전: 도착 및 카페 탐방
- 아침에 강릉에 도착한 후, 유명한 커피 명소인 ‘강릉커피거리’를 방문해보세요.
- 다양한 카페에서 커피를 즐기며 바다가 보이는 멋진 경치를 감상할 수 있습니다.

점심: 지역 맛집
- ‘초당순두부’나 ‘강릉회센터’ 같은 지역 맛집에서 점심을 먹어보세요.
- 신선한 해산물이나 순두부 요리를 추천합니다.

오후: 경포대 및 해변 산책
- 점심 후 경포대로 이동해보세요.
- 경포대에서 바다를 바라보며 산책하고, 주변 사진도 찍어보세요.
- 경포해변에서 바다에 발을 담그며 여유로운 시간을 가져도 좋습니다.

저녁: 바베큐 혹은 해산물 요리
- 숙소에서 바베큐를 즐길 수도 있고, ‘속초 수산시장’에 가서 신선한 해산물을 즐기는 것도 좋습니다.

밤: 해변 산책 또는 휴식
- 저녁 식사 후에는 해변을 따라 산책하며 일몰을 감상해보세요.
- 숙소에서 자유롭게 휴식을 취하는 것도 좋은 선택이에요.

둘째 날 일정을 제안해드릴게요:

오전: 안목해변 카페 탐방
- 아침 식사 후 안목해변으로 이동해 근처의 카페에서 아침 커피와 간단한 아침을 즐기세요.
- 해안선 따라 걷는 것도 좋은 아침 산책이 됩니다.

오후: 명소 방문 및 돌아가기
- ‘선교장’이나 ‘오죽헌’을 방문해 전통적인 한국의 모습을 느껴보세요.
- 강릉의 역사와 문화를 체험할 수 있는 좋은 기회가 될 것입니다.

이후 여행을 마치고 돌아가는 일정으로 계획하면 좋겠네요. 필요에 따라 일정 수정도 가능하니 언제든지 말씀해 주세요!
    ---

    위 예제와 같은 방식으로 답변하세요.
    '''

    if request.method == 'POST':
        user = request.user
        form = ChatForm(request.POST)
        if form.is_valid():
            user_message = form.cleaned_data["user_message"]

            def generate_response():
                stream = CLIENT.chat.completions.create(
                    model="gpt-4o",
                    stream=True,
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": user_message}
                    ]
                )

                bot_reply = ""

                for chunk in stream:
                    if hasattr(chunk, "choices") and chunk.choices:
                        delta = chunk.choices[0].delta
                        if hasattr(delta, "content") and delta.content:
                            text = delta.content
                            bot_reply += text
                            yield text.replace('\n', '<br>')
                            time.sleep(0.05)

        #        clean_reply = remove_markdown(bot_reply)

                Conversation.objects.create(
                    user=user,
                    user_message=user_message,
                    bot_reply=bot_reply # 현재 대화 내용과 DB 에 저장되는 이전 대화 내용을 같게 하기 위해 clean_reply 사용 X
                )

            return StreamingHttpResponse(generate_response(), content_type='text/html')

    return render(request, 'chatbot/chat.html', {'form': ChatForm()})


@login_required
def new_chat(request):
    request.session['new_chat'] = True
    return redirect('chatbot:chat')  # chat_view로 리디렉션