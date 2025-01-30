from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .serializers import UserSerializer

User = get_user_model()

class AccountTests(APITestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123!',
            'password2': 'testpass123!',
            'nickname': 'testuser'
        }
        self.user = User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password'],
            nickname=self.user_data['nickname']
        )

    def test_registration(self):
        url = reverse('accounts:register')
        data = {
            'email': 'newuser@example.com',
            'password': 'newpass123!',
            'password2': 'newpass123!',
            'nickname': 'newuser'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_login(self):
        url = reverse('accounts:token_obtain_pair')
        data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)

    def test_profile_update(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('accounts:profile_update')
        data = {
            'nickname': 'updated_nickname',
            'bio': 'New bio'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nickname'], 'updated_nickname')

    def test_invalid_registration(self):
        """유효하지 않은 회원가입 테스트"""
        url = reverse('accounts:register')
        # 비밀번호 불일치
        data = {
            'email': 'test2@example.com',
            'password': 'testpass123!',
            'password2': 'wrongpass123!',
            'nickname': 'testuser2'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_email(self):
        """중복 이메일 회원가입 테스트"""
        url = reverse('accounts:register')
        data = {
            'email': self.user_data['email'],  # 기존 유저와 동일한 이메일
            'password': 'newpass123!',
            'password2': 'newpass123!',
            'nickname': 'newuser'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_refresh(self):
        """토큰 갱신 테스트"""
        # 먼저 로그인하여 토큰 획득
        login_url = reverse('accounts:token_obtain_pair')
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(login_url, login_data, format='json')
        refresh_token = response.data['refresh']

        # 토큰 갱신 테스트
        refresh_url = reverse('accounts:token_refresh')
        refresh_data = {'refresh': refresh_token}
        response = self.client.post(refresh_url, refresh_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)

class UserProfileTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123!',
            nickname='testuser'
        )
        self.client.force_authenticate(user=self.user)

    def test_get_profile(self):
        """프로필 조회 테스트"""
        url = reverse('accounts:profile_api')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)

    def test_update_profile_without_auth(self):
        """인증되지 않은 사용자의 프로필 수정 시도"""
        self.client.force_authenticate(user=None)
        url = reverse('accounts:profile_update')
        data = {'nickname': 'updated_nickname'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
