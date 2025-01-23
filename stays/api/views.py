from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from django.db.models import Q
from ..models import Stay, Booking, Review
from ..serializers import StaySerializer, BookingSerializer, ReviewSerializer

class StaySearchAPIView(APIView):
    """숙소 검색 API"""
    def post(self, request):
        location = request.data.get('location')
        check_in = request.data.get('check_in')
        check_out = request.data.get('check_out')
        guests = request.data.get('guests')
        
        # 기본 쿼리셋
        stays = Stay.objects.all()
        
        # 필터링 적용
        if location:
            stays = stays.filter(Q(address__icontains=location) | Q(name__icontains=location))
        if check_in and check_out:
            stays = stays.exclude(
                bookings__check_in__lte=check_out,
                bookings__check_out__gte=check_in,
                bookings__status='confirmed'
            )
        if guests:
            stays = stays.filter(capacity__gte=guests)
            
        serializer = StaySerializer(stays, many=True)
        return Response(serializer.data)

class BookingCreateAPIView(APIView):
    """예약 생성 API"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            booking = serializer.save(user=request.user)
            return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReviewListCreateAPIView(APIView):
    """리뷰 생성 및 조회 API"""
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get(self, request, stay_id):
        reviews = Review.objects.filter(stay_id=stay_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)
    
    def post(self, request, stay_id):
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
