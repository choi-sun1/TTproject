from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Itinerary, Place, ItineraryDay, ItineraryPlace
from datetime import date, timedelta

User = get_user_model()

class ItineraryTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123!',
            nickname='testuser'
        )
        self.client.force_authenticate(user=self.user)
        
        self.itinerary = Itinerary.objects.create(
            author=self.user,
            title='Test Trip',
            description='Test Description',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=2),
            is_public=True
        )

    def test_create_itinerary(self):
        url = reverse('itineraries:itinerary-create')
        data = {
            'title': 'New Trip',
            'description': 'New Trip Description',
            'start_date': '2024-01-01',
            'end_date': '2024-01-03',
            'is_public': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Itinerary.objects.count(), 2)

    def test_get_itinerary_list(self):
        url = reverse('itineraries:itinerary-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_itinerary_detail(self):
        url = reverse('itineraries:itinerary-detail', kwargs={'pk': self.itinerary.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Trip')

    def test_update_itinerary(self):
        url = reverse('itineraries:itinerary-update', kwargs={'pk': self.itinerary.pk})
        data = {
            'title': 'Updated Trip',
            'description': 'Updated Description'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Itinerary.objects.get(pk=self.itinerary.pk).title, 'Updated Trip')

    def test_like_itinerary(self):
        url = reverse('itineraries:itinerary-like', kwargs={'pk': self.itinerary.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.itinerary.likes.filter(id=self.user.id).exists())

class PlaceTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123!',
            nickname='testuser'
        )
        self.client.force_authenticate(user=self.user)
        
        self.place = Place.objects.create(
            name='Test Place',
            description='Test Description',
            address='Test Address',
            latitude=37.5665,
            longitude=126.9780,
            place_type='attraction'
        )

    def test_create_place(self):
        url = reverse('itineraries:place-create')
        data = {
            'name': 'New Place',
            'description': 'New Description',
            'address': 'New Address',
            'latitude': 37.5665,
            'longitude': 126.9780,
            'place_type': 'restaurant'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
