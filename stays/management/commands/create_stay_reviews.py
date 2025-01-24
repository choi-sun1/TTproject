from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from stays.models import Stay, Review
import random
from datetime import datetime, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = '숙소 리뷰 테스트 데이터 생성'

    def handle(self, *args, **kwargs):
        # 테스트 사용자 생성 또는 가져오기
        test_users = []
        for i in range(5):
            user, _ = User.objects.get_or_create(
                email=f'testuser{i+1}@example.com',
                defaults={
                    'first_name': f'Test{i+1}',
                    'last_name': 'User',
                    'nickname': f'여행자{i+1}'  # nickname 필드 추가
                }
            )
            test_users.append(user)

        # 리뷰 내용 템플릿
        positive_comments = [
            "깨끗하고 아늑한 숙소였습니다. 특히 {feature}이(가) 좋았어요!",
            "위치가 너무 좋았고 {feature}도 맘에 들었습니다.",
            "친절한 서비스와 {feature}이(가) 인상적이었습니다.",
            "전망이 너무 예뻤고 {feature}도 좋았어요.",
            "조용하고 편안했으며 {feature}이(가) 특히 좋았습니다.",
            "가성비가 매우 좋았고 {feature}이(가) 만족스러웠어요.",
            "청결도가 훌륭했고 {feature}도 좋았습니다.",
            "직원분들이 친절했고 {feature}도 좋았어요."
        ]

        features = [
            "조식", "수영장", "침구", "룸컨디션", "욕실",
            "주변 경관", "접근성", "주차 시설", "와이파이",
            "친절한 직원", "청결도", "전망", "위치",
            "조용한 환경", "인테리어", "어메니티", "냉난방시설"
        ]

        stays = Stay.objects.all()
        if not stays.exists():
            self.stdout.write(
                self.style.ERROR('리뷰를 생성할 숙소가 없습니다. 먼저 숙소를 생성해주세요.')
            )
            return

        created_count = 0
        # 각 숙소마다 5-10개의 리뷰 생성
        for stay in stays:
            num_reviews = random.randint(5, 10)
            
            for _ in range(num_reviews):
                # 랜덤 날짜 생성 (최근 6개월 이내)
                days_ago = random.randint(1, 180)
                review_date = datetime.now() - timedelta(days=days_ago)
                
                # 리뷰 생성
                review = Review.objects.create(
                    stay=stay,
                    author=random.choice(test_users),
                    rating=random.randint(4, 5),  # 4-5점 사이의 평점
                    content=random.choice(positive_comments).format(
                        feature=random.choice(features)
                    ),
                    created_at=review_date
                )
                
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'리뷰 생성 완료: {stay.name} - {review.rating}점 (작성자: {review.author.nickname})'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'총 {created_count}개의 숙소 리뷰가 생성되었습니다.'
            )
        )
