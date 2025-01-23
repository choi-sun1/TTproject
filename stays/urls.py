from django.urls import path
from . import views

app_name = 'stays'

urlpatterns = [
    path('', views.stay_list, name='list'),
    path('<int:pk>/', views.stay_detail, name='detail'),
    path('<int:pk>/book/', views.stay_booking, name='booking'),
    path('map/', views.stay_map, name='map'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('booking/<int:pk>/cancel/', views.cancel_booking, name='cancel_booking'),
    
    # API endpoints
    path('api/stays/', views.StayListCreateAPIView.as_view(), name='api_list_create'),
    path('api/stays/<int:pk>/reviews/', views.ReviewListCreateAPIView.as_view(), name='review_list_create'),
    path('api/bookings/', views.BookingListCreateAPIView.as_view(), name='booking_list_create'),
]
