from django.urls import path
from . import views

app_name = 'itineraries'

urlpatterns = [
    # 기본 CRUD URL
    path('', views.ItineraryListView.as_view(), name='list'),
    path('create/', views.create_redirect, name='create'),  # create -> wizard로 리다이렉트
    path('<int:pk>/', views.ItineraryDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.ItineraryUpdateView.as_view(), name='edit'),  # 추가
    path('<int:pk>/delete/', views.ItineraryDeleteView.as_view(), name='delete'),  # 추가
    path('<int:pk>/like/', views.itinerary_like, name='like'),
    
    # 일정 생성 마법사 URL
    path('wizard/', views.wizard_start, name='wizard'),
    path('wizard/step1/', views.wizard_step1, name='wizard_step1'),
    path('wizard/step2/', views.wizard_step2, name='wizard_step2'),
    path('wizard/step3/', views.wizard_step3, name='wizard_step3'),
    path('wizard/step4/', views.wizard_step4, name='wizard_step4'),
    
    # API 엔드포인트
    path('api/places/search/', views.PlaceSearchAPIView.as_view(), name='place-search-api'),
    path('api/wizard/places/', views.WizardPlaceSearchView.as_view(), name='wizard-place-search'),
    path('api/wizard/schedule/', views.WizardScheduleView.as_view(), name='wizard-schedule'),
    path('api/wizard/optimize/', views.WizardOptimizeView.as_view(), name='wizard-optimize'),
    path('api/wizard/save/', views.WizardSaveView.as_view(), name='wizard-save'),
]
