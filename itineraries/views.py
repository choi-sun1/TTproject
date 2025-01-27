from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Itinerary, Place, ItineraryPlace
from .serializers import (
    ItinerarySerializer,
    PlaceSerializer,
    ItineraryDetailSerializer,
    ItineraryPlaceSerializer
)
from django.shortcuts import get_object_or_404
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.contrib.auth.decorators import login_required
from .models import Itinerary, ItineraryDay, ItineraryPlace, ItineraryLike
from .serializers import ItinerarySerializer, ItineraryDaySerializer
from django.db.models import Q
from datetime import datetime, timedelta, date
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .services.weather import WeatherService
from .services.transport import TransportService
from .services.optimizer import RouteOptimizer
from .services.wizard_service import WizardService
from django.views import View
from django.http import JsonResponse
import json
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

# 템플릿 뷰
class ItineraryListView(ListView):
    model = Itinerary
    template_name = 'itineraries/itinerary_list.html'  # 여기서 사용하는 템플릿 확인
    context_object_name = 'itineraries'
    
    def get_queryset(self):
        queryset = Itinerary.objects.filter(is_public=True)
        search = self.request.GET.get('search', '')
        sort = self.request.GET.get('sort', '-created_at')
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        
        # 정렬 적용
        if sort == '-likes':
            queryset = queryset.annotate(
                likes_count=Count('likes')
            ).order_by('-likes_count')
        else:
            queryset = queryset.order_by(sort)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sort'] = self.request.GET.get('sort', '-created_at')
        return context

class ItineraryDetailView(DetailView):
    model = Itinerary
    template_name = 'itineraries/itinerary_detail.html'
    context_object_name = 'itinerary'

class ItineraryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Itinerary
    template_name = 'itineraries/itinerary_form.html'
    fields = ['title', 'description', 'is_public']
    
    def test_func(self):
        """작성자만 수정 가능하도록 검사"""
        itinerary = self.get_object()
        return self.request.user == itinerary.author
    
    def get_success_url(self):
        return reverse_lazy('itineraries:detail', kwargs={'pk': self.object.pk})

class ItineraryDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Itinerary
    template_name = 'itineraries/itinerary_confirm_delete.html'
    success_url = reverse_lazy('itineraries:list')
    
    def test_func(self):
        """작성자만 삭제 가능하도록 검사"""
        itinerary = self.get_object()
        return self.request.user == itinerary.author

@login_required
def itinerary_like(request, pk):
    """여행 일정 좋아요/취소"""
    itinerary = get_object_or_404(Itinerary, pk=pk)
    if request.user in itinerary.likes.all():
        itinerary.likes.remove(request.user)
        liked = False
    else:
        itinerary.likes.add(request.user)
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'likes_count': itinerary.likes.count()
    })

# ItineraryWizardView 및 관련 API 뷰들은 유지
# API 뷰
class ItineraryAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request):
        itineraries = Itinerary.objects.filter(is_public=True)
        serializer = ItinerarySerializer(itineraries, many=True)
        return Response(serializer.data)

    def post(self, request):
        """새로운 여행 일정 생성"""
        serializer = ItinerarySerializer(data=request.data)
        if serializer.is_valid():
            itinerary = serializer.save(author=request.user)
            
            # 일정 기간에 따른 일차 자동 생성
            start_date = itinerary.start_date
            end_date = itinerary.end_date
            days = (end_date - start_date).days + 1
            
            for day_number in range(1, days + 1):
                ItineraryDay.objects.create(
                    itinerary=itinerary,
                    day_number=day_number,
                    date=start_date + timedelta(days=day_number-1)
                )
            
            return Response(
                ItinerarySerializer(itinerary).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ItineraryDetailAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, pk):
        """여행 일정 상세 조회"""
        itinerary = get_object_or_404(Itinerary, pk=pk)
        if not itinerary.is_public and itinerary.author != request.user:
            return Response(
                {'error': '비공개 일정입니다.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        itinerary.views += 1
        itinerary.save()
        serializer = ItinerarySerializer(itinerary)
        return Response(serializer.data)

    def put(self, request, pk):
        """여행 일정 수정"""
        itinerary = get_object_or_404(Itinerary, pk=pk)
        if request.user != itinerary.author:
            return Response(
                {'error': '수정 권한이 없습니다.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ItinerarySerializer(itinerary, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """여행 일정 삭제"""
        itinerary = get_object_or_404(Itinerary, pk=pk)
        if request.user != itinerary.author:
            return Response(
                {'error': '삭제 권한이 없습니다.'},
                status=status.HTTP_403_FORBIDDEN
            )
        itinerary.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ItineraryPlaceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, day_pk):
        """일정 장소 추가"""
        day = get_object_or_404(ItineraryDay, pk=day_pk)
        if request.user != day.itinerary.author:
            return Response(
                {'error': '권한이 없습니다.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # 순서 자동 계산
        order = day.places.count() + 1
        
        place = ItineraryPlace.objects.create(
            day=day,
            order=order,
            **request.data
        )
        
        return Response({
            'id': place.id,
            'name': place.name,
            'order': place.order
        }, status=status.HTTP_201_CREATED)

class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        query = request.data.get('query', '')
        lat = request.data.get('latitude')
        lng = request.data.get('longitude')
        
        places = Place.objects.filter(name__icontains=query)
        if lat and lng:
            # 위치 기반 검색 로직 추가
            pass
            
        serializer = self.get_serializer(places, many=True)
        return Response(serializer.data)

class ItineraryViewSet(viewsets.ModelViewSet):
    queryset = Itinerary.objects.all()
    serializer_class = ItinerarySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ItineraryDetailSerializer
        return self.serializer_class

    @action(detail=True, methods=['post'])
    def add_place(self, request, pk=None):
        itinerary = self.get_object()
        serializer = ItineraryPlaceSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(itinerary=itinerary)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def clone(self, request, pk=None):
        """기존 일정 복제"""
        original = self.get_object()
        cloned = Itinerary.objects.create(
            author=request.user,
            title=f"{original.title} (복사본)",
            description=original.description
        )
        # 일정 상세 정보 복제 로직
        return Response(ItinerarySerializer(cloned).data)

    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """일정 공유"""
        itinerary = self.get_object()
        share_code = generate_share_code()  # 공유 코드 생성
        return Response({'share_code': share_code})

    @action(detail=True, methods=['post'])
    def optimize_route(self, request, pk=None):
        """일정 최적화"""
        itinerary = self.get_object()
        day_number = request.data.get('day_number')
        
        day = itinerary.days.get(day_number=day_number)
        places = day.places.all()
        
        optimizer = RouteOptimizer()
        optimized_route = optimizer.optimize_route(places)
        
        if (optimized_route):
            # 최적화된 순서로 장소 업데이트
            for index, place in enumerate(optimized_route):
                ItineraryPlace.objects.filter(
                    day=day,
                    place=place
                ).update(order=index + 1)
            
            return Response({'message': '일정이 최적화되었습니다.'})
        return Response({'error': '최적화에 실패했습니다.'}, status=400)

    @action(detail=True, methods=['get'])
    def weather_forecast(self, request, pk=None):
        """날씨 정보 조회"""
        itinerary = self.get_object()
        weather_service = WeatherService(settings.WEATHER_API_KEY)
        
        forecasts = []
        for day in itinerary.days.all():
            for place in day.places.all():
                weather = weather_service.get_weather_forecast(
                    place.place.latitude,
                    place.place.longitude,
                    day.date
                )
                forecasts.append({
                    'day': day.day_number,
                    'place': place.place.name,
                    'weather': weather
                })
        
        return Response(forecasts)

    @action(detail=True, methods=['get'])
    def transport_routes(self, request, pk=None):
        """교통 정보 조회"""
        itinerary = self.get_object()
        transport_service = TransportService(settings.GOOGLE_MAPS_API_KEY)
        
        routes = []
        for day in itinerary.days.all():
            places = day.places.all()
            for i in range(len(places) - 1):
                route = transport_service.get_route(
                    f"{places[i].place.latitude},{places[i].place.longitude}",
                    f"{places[i+1].place.latitude},{places[i+1].place.longitude}"
                )
                if route:
                    routes.append({
                        'day': day.day_number,
                        'from': places[i].place.name,
                        'to': places[i+1].place.name,
                        'route': route
                    })
        
        return Response(routes)

@login_required
def create_redirect(request):
    return redirect('itineraries:wizard-start')

class ItineraryWizardView(LoginRequiredMixin, View):
    def get(self, request, step=1):
        if not step:  # 시작 페이지
            return render(request, 'itineraries/wizard/start.html')
        elif step == 1:
            # 기본 정보 입력 폼
            return render(request, 'itineraries/wizard/step1_basic.html')
        elif step == 2:
            # 장소 검색 및 선택
            return render(request, 'itineraries/wizard/step2_places.html')
        elif step == 3:
            # 일정별 장소 배치
            return render(request, 'itineraries/wizard/step3_schedule.html')
        elif step == 4:
            # 상세 설정
            return render(request, 'itineraries/wizard/step4_details.html')

    def post(self, request, step=1):
        if step == 1:
            # 기본 정보 저장
            data = {
                'title': request.POST.get('title'),
                'start_date': request.POST.get('start_date'),
                'end_date': request.POST.get('end_date'),
            }
            request.session['itinerary_data'] = data
            return JsonResponse({'next_step': 2})
            
        elif step == 2:
            # 선택된 장소들 임시 저장
            places = request.POST.getlist('places')
            request.session['selected_places'] = places
            return JsonResponse({'next_step': 3})
            
        elif step == 3:
            # 일정별 장소 배치 저장
            schedule = request.POST.get('schedule')
            request.session['schedule'] = schedule
            return JsonResponse({'next_step': 4})
            
        elif step == 4:
            # 최종 저장
            try:
                itinerary_data = request.session.get('itinerary_data')
                schedule_data = request.session.get('schedule')
                
                itinerary = Itinerary.objects.create(
                    author=request.user,
                    **itinerary_data
                )
                
                # 일정 상세 정보 저장
                for day_data in json.loads(schedule_data):
                    day = ItineraryDay.objects.create(
                        itinerary=itinerary,
                        day_number=day_data['day_number'],
                        date=day_data['date']
                    )
                    
                    for idx, place_data in enumerate(day_data['places'], 1):
                        ItineraryPlace.objects.create(
                            day=day,
                            place_id=place_data['id'],
                            order=idx,
                            start_time=place_data.get('start_time'),
                            end_time=place_data.get('end_time'),
                            note=place_data.get('note')
                        )
                
                # 세션 데이터 삭제
                for key in ['itinerary_data', 'selected_places', 'schedule']:
                    if key in request.session:
                        del request.session[key]
                
                return JsonResponse({
                    'success': True,
                    'redirect_url': reverse('itineraries:detail', kwargs={'pk': itinerary.pk})
                })
            
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=400)

class PlaceSearchAPIView(APIView):
    def get(self, request):
        try:
            query = request.GET.get('query', '')
            print(f"검색 쿼리: {query}")  # 디버깅용
            
            if len(query) < 2:
                return JsonResponse([], safe=False)
            
            # 수정: 괄호 오류 수정
            places = Place.objects.filter(
                Q(name__icontains=query) |
                Q(address__icontains=query) |
                Q(description__icontains=query)  # 괄호 오류 수정
            )
            
            print(f"검색된 장소 수: {places.count()}")  # 디버깅용
            
            # 시리얼라이저 사용
            serializer = PlaceSerializer(places, many=True)
            return JsonResponse(serializer.data, safe=False)
            
        except Exception as e:
            print(f"검색 오류: {str(e)}")  # 디버깅용
            return JsonResponse(
                {'error': str(e)}, 
                status=500
            )

class WizardSaveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            wizard_data = request.session.get('wizard_data', {})
            wizard_data.update(request.data)
            
            # 최종 일정 생성
            itinerary = WizardService.create_itinerary_from_wizard(
                request.user, 
                wizard_data
            )

            # 세션 데이터 삭제
            if 'wizard_data' in request.session:
                del request.session['wizard_data']

            return Response({
                'success': True,
                'itinerary_id': itinerary.id,
                'redirect_url': reverse('itineraries:detail', kwargs={'pk': itinerary.id})
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class WizardPlaceSearchView(APIView):
    """마법사용 장소 검색 뷰"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.GET.get('query', '')
        location = request.GET.get('location', '')
        
        # 장소 검색 로직
        places = Place.objects.filter(name__icontains=query)  # 여기 괄호가 닫히지 않았었습니다
        
        if location:
            lat, lng = map(float, location.split(','))
            # TODO: 위치 기반 필터링 로직 구현
            # places = places.filter(...) 
        
        serializer = PlaceSerializer(places, many=True)
        return Response(serializer.data)

class WizardScheduleView(APIView):
    """마법사 일정 배치 뷰"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            schedule_data = request.data
            # 일정 데이터 검증
            WizardService.validate_wizard_data(schedule_data, step=3)
            # 세션에 저장
            request.session['schedule'] = schedule_data
            return Response({'success': True, 'next_step': 4})
        except Exception as e:
            return Response({'error': str(e)}, status=400)

class WizardOptimizeView(APIView):
    """마법사 일정 최적화 뷰"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            day_number = request.data.get('day_number')
            places = request.data.get('places', [])
            
            if not places or len(places) < 2:
                return Response({
                    'success': False,
                    'error': '최적화할 장소가 충분하지 않습니다.'
                }, status=400)
            
            # 좌표 데이터 검증
            invalid_places = [p for p in places if 'latitude' not in p or 'longitude' not in p]
            if invalid_places:
                return Response({
                    'success': False,
                    'error': '일부 장소의 위치 정보가 누락되었습니다.'
                }, status=400)
            
            optimizer = RouteOptimizer()
            optimized_places = optimizer.optimize_route(places)
            
            print(f"최적화 결과: {optimized_places}")  # 디버깅용
            
            return Response({
                'success': True,
                'optimized_places': optimized_places
            })
        except Exception as e:
            print(f"최적화 오류: {str(e)}")  # 디버깅용
            return Response({
                'success': False,
                'error': str(e)
            }, status=400)

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .services.wizard_service import ItineraryWizardService
from django.views.decorators.http import require_http_methods

@login_required
def wizard_start(request):
    return render(request, 'itineraries/wizard/start.html')

@login_required
@require_http_methods(["GET", "POST"])
def wizard_step1(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # 필수 필드 검증
            required_fields = ['title', 'destination', 'start_date', 'end_date']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({
                        'status': 'error',
                        'message': f'{field} 필드는 필수입니다.'
                    }, status=400)
            
            # 세션에 데이터 저장
            request.session['wizard_data'] = {
                'title': data['title'],
                'destination': data['destination'],
                'start_date': data['start_date'],
                'end_date': data['end_date'],
                'styles': data.get('styles', [])
            }
            
            return JsonResponse({
                'status': 'success',
                'message': '기본 정보가 저장되었습니다.'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': '잘못된 데이터 형식입니다.'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    # GET 요청 처리
    return render(request, 'itineraries/wizard/step1_basic.html')

@login_required
def wizard_step2(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            places = data.get('places', [])
            
            # 세션에 데이터 저장
            wizard_data = request.session.get('wizard_data', {})
            wizard_data['places'] = places
            request.session['wizard_data'] = wizard_data
            
            return JsonResponse({
                'status': 'success',
                'message': '장소가 저장되었습니다.'
            })
        except Exception as e:
            print(f"저장 오류: {str(e)}")  # 디버깅용
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return render(request, 'itineraries/wizard/step2_places.html')

@login_required
def wizard_step3(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            schedule = data.get('schedule', {})
            
            # 세션에 저장
            request.session['wizard_data']['schedule'] = schedule
            
            return JsonResponse({
                'status': 'success',
                'message': '일정이 저장되었습니다.'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
            
    return render(request, 'itineraries/wizard/step3_schedule.html')

@login_required
def wizard_step4(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # wizard_data 가져오기 및 업데이트
            wizard_data = request.session.get('wizard_data', {})
            wizard_data.update({
                'is_public': data.get('is_public', True),
                'budgets': data.get('budgets', {}),
                'checklist': data.get('checklist', [])
            })
            
            # 일정 생성
            wizard_service = ItineraryWizardService()
            itinerary = wizard_service.create_itinerary(request.user, wizard_data)
            
            # 세션 데이터 삭제
            if 'wizard_data' in request.session:
                del request.session['wizard_data']
            
            return JsonResponse({
                'success': True,
                'redirect_url': reverse('itineraries:detail', kwargs={'pk': itinerary.pk})
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    context = {
        'budget_categories': ['교통', '숙박', '식비', '관광', '쇼핑', '기타']
    }
    return render(request, 'itineraries/wizard/step4_details.html', context)
