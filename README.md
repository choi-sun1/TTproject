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


# 데이터 베이스 초기화
## 마그레이션 생성
python manage.py makemigrations

## 특정 앱의 마그레이션 생성
python manage.py makemigrations itineraries

python manage.py makemigrations accounts

python manage.py makemigrations articles

python manage.py makemigrations stays

python manage.py makemigrations chatbot


## 마그레이션 적용
python manage.py migrate

## 슈퍼계정 생성 (필요시)
python manage.py createsuperuser

## 서버 실행
python manage.py runserver

## 현재 구현 기능
메인페이지 : http://127.0.0.1:8000/

회원가입 페이지 : http://127.0.0.1:8000/accounts/signup/

로그인 페이지 : http://127.0.0.1:8000/accounts/login/

프로필 페이지 : http://127.0.0.1:8000/accounts/profile/

게시판 페이지 : 

챗봇 페이지 : 

여핼일정 만들기 페이지 :



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
