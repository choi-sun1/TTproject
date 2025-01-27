from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, View, DetailView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import SignupForm, LoginForm, UserChangeForm  # UserChangeForm import 추가
from django.contrib.auth import get_user_model

User = get_user_model()

class SignupView(CreateView):
    model = User
    form_class = SignupForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()
        login(self.request, user)  # 회원가입 후 자동 로그인
        messages.success(self.request, '회원가입이 완료되었습니다.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, '입력한 정보를 다시 확인해주세요.')
        return super().form_invalid(form)

class LoginView(View):
    template_name = 'accounts/login.html'
    form_class = LoginForm

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                form.add_error(None, '이메일 또는 비밀번호가 잘못되었습니다.')
        
        return render(request, self.template_name, {'form': form})

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
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
    
    context = {
        'profile': profile,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            messages.success(request, '프로필이 성공적으로 수정되었습니다.')
            return redirect('accounts:profile')
    else:
        form = UserChangeForm(instance=request.user)
    
    context = {
        'form': form,
        'user': request.user
    }
    return render(request, 'accounts/profile_edit.html', context)

@login_required
def settings_view(request):
    return render(request, 'accounts/settings.html')