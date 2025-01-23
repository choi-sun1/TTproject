from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Stay, Booking
from .utils import fetch_hotels_from_google
import os
from datetime import date
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .models import Stay, Booking, Review
from .serializers import StaySerializer, BookingSerializer, ReviewSerializer
from .services.google_maps import GoogleMapsService
from rest_framework.views import APIView
from django.db.models import Q
from django.conf import settings

class StayListView(ListView):
    model = Stay
    template_name = 'stays/list.html'
    context_object_name = 'stays'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['google_maps_api_key'] = os.getenv('GOOGLE_MAPS_API_KEY')
        
        # 숙박시설이 없을 경우 Google Places API에서 데이터 가져오기
        if not Stay.objects.exists():
            fetch_hotels_from_google()
            context['stays'] = Stay.objects.all()
        
        return context

class StayDetailView(DetailView):
    model = Stay
    template_name = 'stays/detail.html'
    context_object_name = 'stay'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['google_maps_api_key'] = os.getenv('GOOGLE_MAPS_API_KEY')
        return context

@login_required
def book_stay(request, pk):
    stay = get_object_or_404(Stay, pk=pk)
    if request.method == 'POST':
        try:
            booking = Booking.objects.create(
                stay=stay,
                user=request.user,
                check_in=request.POST['check_in'],
                check_out=request.POST['check_out'],
                guests=request.POST['guests'],
                total_price=stay.price_per_night * int(request.POST['nights'])
            )
            messages.success(request, '예약이 완료되었습니다.')
            return redirect('stays:booking_confirmation', pk=booking.pk)
        except Exception as e:
            messages.error(request, f'예약 중 오류가 발생했습니다: {str(e)}')
    
    return render(request, 'stays/booking.html', {'stay': stay})

@login_required
def booking_confirmation(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    context = {
        'booking': booking,
        'can_cancel': booking.check_in > date.today()  # 취소 가능 여부 추가
    }
    return render(request, 'stays/booking_confirmation.html', context)

@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    stay_name = booking.stay.name  # 숙소 이름 저장
    booking.delete()
    messages.success(request, f'{stay_name} 예약이 취소되었습니다.')
    
    # 이전 페이지로 리다이렉트
    referer = request.META.get('HTTP_REFERER')
    if (referer and 'my-bookings' in referer):
        return redirect('stays:my_bookings')
    return redirect('accounts:profile', username=request.user.username)

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'bookings': bookings,
        'today': date.today()
    }
    return render(request, 'stays/my_bookings.html', context)

class StayViewSet(viewsets.ModelViewSet):
    queryset = Stay.objects.all()
    serializer_class = StaySerializer
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.maps_service = GoogleMapsService(api_key=settings.GOOGLE_MAPS_API_KEY)

    def list(self, request):
        # Handle the case when Google Maps service is not available
        if not self.maps_service.client:
            return Response(
                {"error": "Location services temporarily unavailable"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        # ...existing code...

    @action(detail=True, methods=['post'])
    def book(self, request, pk=None):
        stay = self.get_object()
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, stay=stay)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def nearby(self, request, pk=None):
        stay = self.get_object()
        maps_service = GoogleMapsService()
        nearby_places = maps_service.search_nearby(
            location={'lat': stay.latitude, 'lng': stay.longitude}
        )
        return Response(nearby_places)

def stay_list(request):
    """숙소 목록 페이지"""
    stays = Stay.objects.all()
    return render(request, 'stays/list.html', {'stays': stays})

def stay_detail(request, pk):
    """숙소 상세 페이지"""
    stay = get_object_or_404(Stay, pk=pk)
    return render(request, 'stays/detail.html', {'stay': stay})

def stay_map(request):
    """숙소 지도 페이지"""
    return render(request, 'stays/map_view.html')

class StaySearchAPIView(APIView):
    """숙소 검색 API"""
    def post(self, request):
        location = request.data.get('location')
        check_in = request.data.get('checkIn')
        check_out = request.data.get('checkOut')
        guests = request.data.get('guests')

        # 기본 쿼리셋
        stays = Stay.objects.all()

        # 위치 기반 필터링
        if location:
            stays = stays.filter(
                Q(address__icontains=location) |
                Q(name__icontains=location)
            )

        # 예약 가능 여부 확인
        if check_in and check_out:
            unavailable_stays = Booking.objects.filter(
                Q(check_in__lte=check_out) & Q(check_out__gte=check_in),
                status='confirmed'
            ).values_list('stay_id', flat=True)
            stays = stays.exclude(id__in=unavailable_stays)

        # 수용 인원 필터링
        if guests:
            stays = stays.filter(capacity__gte=guests)

        serializer = StaySerializer(stays, many=True)
        return Response(serializer.data)

class BookingListCreateAPIView(APIView):
    """예약 생성 및 조회 API"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """사용자의 예약 목록 조회"""
        bookings = Booking.objects.filter(user=request.user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    def post(self, request):
        """새로운 예약 생성"""
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            # 예약 가능 여부 확인
            stay = serializer.validated_data['stay']
            check_in = serializer.validated_data['check_in']
            check_out = serializer.validated_data['check_out']
            
            if not stay.is_available(check_in, check_out):
                return Response(
                    {'error': '해당 기간에는 예약할 수 없습니다.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            booking = serializer.save(user=request.user)
            return Response(
                BookingSerializer(booking).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReviewListCreateAPIView(APIView):
    """리뷰 생성 및 조회 API"""
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, stay_id):
        """숙소의 리뷰 목록 조회"""
        reviews = Review.objects.filter(stay_id=stay_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request, stay_id):
        """새로운 리뷰 작성"""
        # 실제 투숙객인지 확인
        if not Booking.objects.filter(
            user=request.user,
            stay_id=stay_id,
            status='completed'
        ).exists():
            return Response(
                {'error': '숙박 완료 후에만 리뷰를 작성할 수 있습니다.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            review = serializer.save(
                user=request.user,
                stay_id=stay_id
            )
            return Response(
                ReviewSerializer(review).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stay_booking(request, pk):
    stay = get_object_or_404(Stay, pk=pk)
    
    try:
        booking = Booking.objects.create(
            user=request.user,
            stay=stay,
            check_in=request.data.get('check_in'),
            check_out=request.data.get('check_out'),
            guests=request.data.get('guests', 1)
        )
        return Response({
            'status': 'success',
            'message': 'Booking created successfully',
            'booking_id': booking.id
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

class StayListCreateAPIView(generics.ListCreateAPIView):
    queryset = Stay.objects.all()
    serializer_class = StaySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        queryset = Stay.objects.all()
        location = self.request.query_params.get('location', None)
        
        if location:
            queryset = queryset.filter(
                Q(address__icontains=location) |
                Q(name__icontains=location)
            )
        return queryset
