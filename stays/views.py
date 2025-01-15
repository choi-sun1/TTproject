from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Stay, Booking
from .utils import fetch_hotels_from_google
import os
from datetime import date

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
    if referer and 'my-bookings' in referer:
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
