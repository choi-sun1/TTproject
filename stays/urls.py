from django.urls import path
from . import views

app_name = 'stays'

urlpatterns = [
    path('', views.StayListView.as_view(), name='list'),
    path('<int:pk>/', views.StayDetailView.as_view(), name='detail'),
    path('<int:pk>/book/', views.book_stay, name='book'),
    path('booking/<int:pk>/', views.booking_confirmation, name='booking_confirmation'),
    path('booking/<int:pk>/cancel/', views.cancel_booking, name='cancel_booking'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
]
