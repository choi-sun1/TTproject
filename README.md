# 추가 라이브러리

pip install markdown 

pip install Pillow

pip install markdown2

## 게시판 글작성 기능 개선
> 마크다운에디터 추가 (마크다운으로 게시글 작성 가능)
> 
> 게시글 이미지 추가 최대 10개 까지 업로드가능 (용량제한 5MB)
>
> 기능 개선 필요(아직 버그있음 : 업로드시 1개 이미지만 업로드됨, 수정하면 더 넣어지는 데 개선해야함.)

### 테스트 실행방법
>  venv 생성
>  `python -m venv venv`
>
>  venv 활성화
>  `source venv/Scripts/activate`# Windows
>
>  라이브러리 설치
>  `pip install django==4.2.8`
>
>  `pip install -r requirements.txt`
> 
>  MYSQL 에디터베이스 생성
>  CMD 입력 : `mysql -u root -p`
>  
>  비밀번호 입력 후 
>  `CREATE DATABASE team11 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`
> 
>
>  마이그레이션 파일 생성
>  `python manage.py makemigrations`
>
>  데이터베이스 마이그레이션 적용
>  `python manage.py migrate`
>
>  서버 실행
>  `python manage.py runserver`
>
>  발급된 주소 접속
>  `http://127.0.0.1:8000/` (기본 주소)
>
>>  게시판 오류 발생시 (board 마그레이션 실행)
>>  `python manage.py makemigrations board`
>>  `python manage.py migrate board`
>>  `python manage.py migrate`
>>
>>  지속적 오류 발생시 (MYSQL 초기화 후 다시 시작 후 마그레이션 진행행)
>>  `mysql -u root -p`
>>  `DROP DATABASE team11;`
>>  `CREATE DATABASE team11 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`
>>
# HTML 구현
![image](https://github.com/user-attachments/assets/85f52d24-3d0d-46a9-85cc-d7f7eca86d0e)

![image](https://github.com/user-attachments/assets/03f0ae19-741f-4763-b88b-d7594b9caab8)

![image](https://github.com/user-attachments/assets/b224fee6-47e4-460e-8ff4-b1d14f82e379)

![image](https://github.com/user-attachments/assets/d7a23bf6-a70e-4d0c-b3b3-034eab24b808)

![image](https://github.com/user-attachments/assets/fdd2a9e0-151d-42e8-a45c-3d83106fccba)
