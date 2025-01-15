from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.password_validation import password_validators_help_texts
from .models import User

class UserRegisterForm(UserCreationForm):
    username = forms.CharField(
        label='ID',
        help_text='영문, 숫자 및 @/./+/-/_ 만 사용 가능합니다.'
    )
    email = forms.EmailField(
        label='이메일',
        help_text='유효한 이메일 주소를 입력해주세요.'
    )
    nickname = forms.CharField(
        label='닉네임',
        required=False,
        help_text='선택사항입니다.'
    )
    birth_date = forms.DateField(
        label='생년월일',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    gender = forms.ChoiceField(
        label='성별',
        choices=User.GENDER_CHOICES,
        required=False
    )
    bio = forms.CharField(
        label='자기소개',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text='간단한 자기소개를 작성해주세요.'
    )
    profile_image = forms.ImageField(
        label='프로필 이미지',
        required=False,
        help_text='프로필 이미지를 선택해주세요.'
    )
    password1 = forms.CharField(
        label='비밀번호',
        widget=forms.PasswordInput,
        help_text='8자 이상의 영문, 숫자, 특수문자를 조합해주세요.'
    )
    password2 = forms.CharField(
        label='비밀번호 확인',
        widget=forms.PasswordInput,
        help_text='동일한 비밀번호를 다시 입력해주세요.'
    )

    class Meta:
        model = User
        fields = (
            'username', 
            'email', 
            'nickname', 
            'password1', 
            'password2',
            'birth_date',
            'gender',
            'bio',
            'profile_image'
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.nickname = self.cleaned_data['nickname']
        user.birth_date = self.cleaned_data['birth_date']
        user.gender = self.cleaned_data['gender']
        user.bio = self.cleaned_data['bio']
        if commit:
            user.save()
            if self.cleaned_data.get('profile_image'):
                user.profile_image = self.cleaned_data['profile_image']
                user.save()
        return user

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label='아이디')
    password = forms.CharField(label='비밀번호', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password']