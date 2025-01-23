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
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.contrib.auth.decorators import login_required
from .models import Itinerary, ItineraryDay, ItineraryPlace, ItineraryLike
from .serializers import ItinerarySerializer, ItineraryDaySerializer
from django.db.models import Q
from datetime import datetime, timedelta
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

# 템플릿 뷰
class ItineraryListView(ListView):
    model = Itinerary
    template_name = 'itineraries/itinerary_list.html'
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

class ItineraryCreateView(LoginRequiredMixin, CreateView):
    model = Itinerary
    template_name = 'itineraries/itinerary_form.html'
    fields = ['title', 'description', 'start_date', 'end_date', 'is_public']
    success_url = reverse_lazy('itineraries:list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class ItineraryUpdateView(LoginRequiredMixin, UpdateView):
    model = Itinerary
    template_name = 'itineraries/itinerary_form.html'
    fields = ['title', 'description', 'start_date', 'end_date', 'is_public']

class ItineraryDeleteView(LoginRequiredMixin, DeleteView):
    model = Itinerary
    template_name = 'itineraries/itinerary_confirm_delete.html'
    success_url = '/itineraries/'

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
    
    return Response({
        'liked': liked,
        'likes_count': itinerary.likes.count()
    })

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
