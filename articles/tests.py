from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Article, Comment
from .serializers import ArticleSerializer

User = get_user_model()

class ArticleTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123!',
            nickname='testuser'
        )
        self.client.force_authenticate(user=self.user)
        
        self.article = Article.objects.create(
            author=self.user,
            title='Test Article',
            content='Test Content'
        )

    def test_create_article(self):
        url = reverse('articles_api:article-create')  # namespace 수정
        data = {
            'title': 'New Article',
            'content': 'New Content'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Article.objects.count(), 2)

    def test_get_article_list(self):
        url = reverse('articles_api:article-list')  # namespace 수정
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_article_detail(self):
        url = reverse('articles_api:article-detail', kwargs={'pk': self.article.pk})  # namespace 수정
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Article')

    def test_article_update(self):
        url = reverse('articles_api:article-update', kwargs={'pk': self.article.pk})  # namespace 수정
        data = {
            'title': 'Updated Title',
            'content': 'Updated Content'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Article.objects.get(pk=self.article.pk).title, 'Updated Title')

    def test_article_delete(self):
        url = reverse('articles_api:article-delete', kwargs={'pk': self.article.pk})  # namespace 수정
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Article.objects.count(), 0)

    def test_create_article_without_auth(self):
        """인증되지 않은 사용자의 게시글 작성 시도"""
        self.client.force_authenticate(user=None)
        url = reverse('articles:article-create')
        data = {
            'title': 'Unauthorized Article',
            'content': 'This should fail'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_article_like_functionality(self):
        """게시글 좋아요 기능 테스트"""
        url = reverse('articles_api:article-like', kwargs={'pk': self.article.pk})  # namespace 수정
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.article.likes.filter(id=self.user.id).exists())

        # 좋아요 취소
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.article.likes.filter(id=self.user.id).exists())

class ArticleCommentTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123!',
            nickname='testuser'
        )
        self.article = Article.objects.create(
            author=self.user,
            title='Test Article',
            content='Test Content'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_comment(self):
        """댓글 작성 테스트"""
        url = reverse('articles_api:comment-create', kwargs={'article_id': self.article.pk})  # namespace 수정
        data = {'content': 'Test Comment'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.article.comments.count(), 1)

    def test_delete_comment(self):
        """댓글 삭제 테스트"""
        # 먼저 댓글 생성
        comment = Comment.objects.create(
            article=self.article,
            author=self.user,
            content='Test Comment'
        )
        url = reverse('articles_api:comment-delete', kwargs={
            'article_id': self.article.pk,
            'comment_id': comment.pk
        })  # namespace 수정
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.article.comments.count(), 0)

class ArticleViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123!',
            nickname='testuser'
        )
        self.client.force_authenticate(user=self.user)
        
    def test_article_filter(self):
        """게시글 필터링 테스트"""
        url = reverse('articles:article-list')
        response = self.client.get(url, {'author': self.user.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_article_search(self):
        """게시글 검색 테스트"""
        url = reverse('articles:article-list')
        response = self.client.get(url, {'search': 'test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_article_ordering(self):
        """게시글 정렬 테스트"""
        url = reverse('articles:article-list')
        response = self.client.get(url, {'ordering': '-created_at'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class ArticleTemplateViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123!',
            nickname='testuser'
        )
        
    def test_article_list_template(self):
        """게시글 목록 템플릿 테스트"""
        self.client.login(email='test@example.com', password='testpass123!')
        response = self.client.get(reverse('articles:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'articles/list.html')
