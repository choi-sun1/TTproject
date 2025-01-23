from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from ..models import Itinerary, ItineraryDay, ItineraryPlace
from ..serializers import ItinerarySerializer, ItineraryDaySerializer
from datetime import datetime, timedelta

class ItineraryAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        """여행 일정 목록 조회"""
        itineraries = Itinerary.objects.filter(is_public=True)
        search = request.query_params.get('search', '')
        if search:
            itineraries = itineraries.filter(title__icontains=search)
        serializer = ItinerarySerializer(itineraries, many=True)
        return Response(serializer.data)

    def post(self, request):
        """새 여행 일정 생성"""
        serializer = ItinerarySerializer(data=request.data)
        if serializer.is_valid():
            itinerary = serializer.save(author=request.user)
            
            # 일정 기간에 따른 일차 자동 생성
            start_date = datetime.strptime(request.data['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(request.data['end_date'], '%Y-%m-%d').date()
            days = (end_date - start_date).days + 1
            
            for day_number in range(1, days + 1):
                current_date = start_date + timedelta(days=day_number-1)
                ItineraryDay.objects.create(
                    itinerary=itinerary,
                    day_number=day_number,
                    date=current_date
                )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ItineraryDetailAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, pk):
        """여행 일정 상세 조회"""
        itinerary = get_object_or_404(Itinerary, pk=pk)
        serializer = ItinerarySerializer(itinerary)
        return Response(serializer.data)

    def put(self, request, pk):
        """여행 일정 수정"""
        itinerary = get_object_or_404(Itinerary, pk=pk)
        if request.user != itinerary.author:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = ItinerarySerializer(itinerary, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """여행 일정 삭제"""
        itinerary = get_object_or_404(Itinerary, pk=pk)
        if request.user != itinerary.author:
            return Response(status=status.HTTP_403_FORBIDDEN)
        itinerary.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
