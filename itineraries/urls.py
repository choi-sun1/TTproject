from django.urls import path
from . import views

app_name = 'itineraries'

urlpatterns = [
    path('', views.ItineraryListView.as_view(), name='list'),
    path('create/', views.ItineraryCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ItineraryDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.ItineraryUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.ItineraryDeleteView.as_view(), name='delete'),
]
