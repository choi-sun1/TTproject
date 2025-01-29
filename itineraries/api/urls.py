
from django.urls import path
from . import views

urlpatterns = [
    path('', views.ItineraryAPIView.as_view(), name='itinerary-list-create'),
    path('<int:pk>/', views.ItineraryDetailAPIView.as_view(), name='itinerary-detail'),
]