## SQL라이트로 교체
 - 교체이유 : 원활한 데이터 공유
- SQL서버 설정 따로 필요없음
- 패키지 설치로 쉽게 설치
- 테스트용 데이터 입력 쉬움

## 가상환경 활성화
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

## 패키지 설치
pip install -r requirements.txt

## .env 파일 생성
```
# API Keys (실제 키는 별도로 안전하게 보관)
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
OPENAI_API_KEY=your-openai-api-key

# Django settings
SECRET_KEY=django-insecure-your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Email settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Database settings (SQLite)
DATABASE_URL=sqlite:///db.sqlite3
```

## 테스트용 데이터 생성

python manage.py generate_jeju_data

제주도 위주로 구성


# 데이터 베이스 초기화
## 마그레이션 생성
python manage.py makemigrations

## 특정 앱의 마그레이션 생성
python manage.py makemigrations itineraries

python manage.py makemigrations accounts

python manage.py makemigrations chatbot

## 마그레이션 적용
python manage.py migrate

## 슈퍼계정 생성 (필요시)
python manage.py createsuperuser

## 서버 실행
python manage.py runserver

## 정적 파일수집 ("static" 정적파일 수집 서버 배포시 사용)
python manage.py collectstatic


## 현재 구현 기능
메인페이지 : http://127.0.0.1:8000/

회원가입 페이지 : http://127.0.0.1:8000/accounts/signup/

로그인 페이지 : http://127.0.0.1:8000/accounts/login/

프로필 페이지 : http://127.0.0.1:8000/accounts/profile/

여행일정 게시판 페이지 : http://127.0.0.1:8000/itineraries/

여핼일정 만들기 페이지 : http://127.0.0.1:8000/itineraries/wizard/

챗봇 페이지 : http://127.0.0.1:8000/chatbot/chat/

어드민 페이지 : http://127.0.0.1:8000/admin/

API 문서: http://localhost:8000/swagger/

ReDoc 문서: http://localhost:8000/redoc/




# 시스템 코드 커버리지 테스트
## 정적 파일 수집
python manage.py collectstatic

## 마이그레이션 최종 확인
python manage.py showmigrations

## 의존성 패키지 목록 업데이트
pip freeze > requirements.txt

## 테스트 코드 실행
python manage.py test --verbosity=2

## 커버리지 확인
coverage run manage.py test
coverage report
coverage html


# TTproject

## 📖 목차
1. [프로젝트 소개](#프로젝트-소개)
2. [팀소개](#팀소개)
3. [주요기능](#주요기능)
4. [개발기간](#개발기간)
5. [기술스택](#기술스택)
6. [Architecture](#Architecture)
7.  [ERD](#ERD)
8.  [프로젝트 파일 구조](#프로젝트-파일-구조)
9.  [Trouble Shooting](#trouble-shooting)
    
## 👨‍🏫 프로젝트 소개
#### SmartTrip - 똑똑한 여행 AI
##### 프로젝트 계기 - 나중에 작성
기억하고 싶은 순간을 사진으로 남기고, 여행지에서의 간단한 리뷰를 통해 여행 일정을 다른 사람들과 공유할 수 있는 플랫폼을 개발하는 것을 목표로 합니다.
사용자는 챗봇을 통해 여행지, 맛집, 숙소 등을 추천받고, 추천 일정과 여행지에 대한 리뷰를 공유함으로써 여행 경험을 향상시킵니다.
또한, 공유된 여행 일정은 알고리즘 추천을 통해 사용자의 만족도를 높이는 방향으로 최적화됩니다.

## 팀소개
- **팀명 : T.T (Traveler Tip)**

| 👑 리더 | 👑 부 리더 | 📝 서기 | ✨ 팀원 |
| --- | --- | --- | --- |
| 정용선 | 최해찬 | 차아인 | 이유림 |




## 💜 주요기능
### 🧑‍💻 회원기능
- 로그인
- 로그아웃
- 회원가입
- 회원 정보 조회 및 수정

### 🚙 챗봇 기능
- 여행 일정 계획
- 글쓰기

### 📝 게시글 기능
- 게시글 댓글
- 게시글 추천
- 숙박 예약

## ⏲️ 개발기간
- 2024.12.30(목) ~ 2025.00.00()

## 📚️ 기술스택

### Frontend & Tools

<div>
    <img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue">
    <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white">
    <img src="https://img.shields.io/badge/JavaScript-323330?style=for-the-badge&logo=javascript&logoColor=F7DF1E">
    <img src="https://img.shields.io/badge/Slack-4A154B?style=for-the-badge&logo=slack&logoColor=white">
    <img src="https://img.shields.io/badge/Jira-0052CC?style=for-the-badge&logo=Jira&logoColor=white">
    <img src="https://img.shields.io/badge/Notion-000000?style=for-the-badge&logo=notion&logoColor=white">
    <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green">
    <img src="https://img.shields.io/badge/GIT-E44C30?style=for-the-badge&logo=git&logoColor=white"/>
    <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white">
    <img src="https://img.shields.io/badge/Figma-F24E1E?style=for-the-badge&logo=figma&logoColor=white">
    <img src="https://img.shields.io/badge/Colab-F9AB00?style=for-the-badge&logo=googlecolab&color=525252">
    <img src="https://img.shields.io/badge/Visual_Studio_Code-0078D4?style=for-the-badge&logo=visual%20studio%20code&logoColor=white">
    <img src="https://img.shields.io/badge/ZEP-6758ff?style=for-the-badge&logo=visual%20studio%20code&logoColor=white">
</div>


### ✔️ Backend & Tools

<div>
    <img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue">
    <img src="https://camo.githubusercontent.com/4c4a57a11a83f99eafb6eaaaaf65ea43e0fc446fccbf8533aac7e9be1067aaf7/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f446a616e676f2d3039324532303f7374796c653d666f722d7468652d6261646765266c6f676f3d446a616e676f266c6f676f436f6c6f723d7768697465">
    <img src="https://img.shields.io/badge/Postman-FF6C37?style=for-the-badge&logo=Postman&logoColor=white">
    <img src="https://img.shields.io/badge/scikit_learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white">
    <img src="https://img.shields.io/badge/-HuggingFace-FDEE21?style=for-the-badge&logo=HuggingFace&logoColor=black">
    <img src="https://img.shields.io/badge/ChatGPT-74aa9c?style=for-the-badge&logo=openai&logoColor=white">
    <img src="https://img.shields.io/badge/Slack-4A154B?style=for-the-badge&logo=slack&logoColor=white"/>
    <img src="https://img.shields.io/badge/Jira-0052CC?style=for-the-badge&logo=Jira&logoColor=white">
    <img src="https://img.shields.io/badge/Notion-000000?style=for-the-badge&logo=notion&logoColor=white">
    <img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white">
    <img src="https://img.shields.io/badge/GIT-E44C30?style=for-the-badge&logo=git&logoColor=white">
    <img src="https://img.shields.io/badge/Colab-F9AB00?style=for-the-badge&logo=googlecolab&color=525252"/>
    <img src="https://img.shields.io/badge/Visual_Studio_Code-0078D4?style=for-the-badge&logo=visual%20studio%20code&logoColor=white">
    <img src="https://img.shields.io/badge/ZEP-6758ff?style=for-the-badge&logo=visual%20studio%20code&logoColor=white">
    <img src="https://img.shields.io/badge/MySQL-005C84?style=for-the-badge&logo=mysql&logoColor=white">
    
</div>

### ✔️ Deploy

<div>
    <img src="https://img.shields.io/badge/AWS_EC2-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white">
</div>

## 🌐 Architecture





## ERD


## 🗂️ 프로젝트 파일 구조




## 🚨 Trouble Shooting