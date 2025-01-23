from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth import get_user_model
from .models import User

User = get_user_model()

class UserCreationForm(BaseUserCreationForm):
    class Meta(BaseUserCreationForm.Meta):
        model = User
        fields = ('email', 'nickname', 'birth_date', 'gender')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            del self.fields['username']

class UserChangeForm(BaseUserChangeForm):
    password = None  # 비밀번호 필드 제거
    
    class Meta:
        model = User
        fields = ('nickname', 'profile_image', 'gender', 'bio')
        widgets = {
            'nickname': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class SignupForm(UserCreationForm):
    email = forms.EmailField(
        max_length=255,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    nickname = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('email', 'nickname', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('이미 사용중인 이메일입니다.')
        return email

    def clean_nickname(self):
        nickname = self.cleaned_data.get('nickname')
        if User.objects.filter(nickname=nickname).exists():
            raise forms.ValidationError('이미 사용중인 닉네임입니다.')
        return nickname

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        max_length=255,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
