from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, View, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import SignupForm
from django.contrib.auth import get_user_model

User = get_user_model()

class SignupView(CreateView):
    model = User
    form_class = SignupForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:login')

class LoginView(View):
    template_name = 'accounts/login.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        return render(request, self.template_name)
    
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(email=email, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, '이메일 또는 비밀번호가 잘못되었습니다.')
            return render(request, self.template_name)

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('home')

class UserProfileView(DetailView):
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'
    slug_field = 'nickname'
    slug_url_kwarg = 'nickname'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context.update({
            'articles_count': user.articles.count(),
            'itineraries_count': user.itineraries.count(),
            'is_owner': self.request.user == user
        })
        return context

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')

@login_required
def profile_edit(request):
    return render(request, 'accounts/profile_edit.html')