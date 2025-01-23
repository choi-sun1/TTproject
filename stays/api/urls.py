
from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.StaySearchAPIView.as_view(), name='stay-search'),
    path('booking/create/', views.BookingCreateAPIView.as_view(), name='booking-create'),
    path('<int:stay_id>/reviews/', views.ReviewListCreateAPIView.as_view(), name='stay-reviews'),
]