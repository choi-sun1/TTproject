from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

# 회원가입 시리얼라이저 정의
class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'password2', 'username','profile_image','nickname','birth','gender','introduce')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({
                'password': '비밀번호가 일치하지 않습니다.'
            })

        return data
    
    def create(self, validated_data):
        validated_data.pop('password2') # password2 제거
        user = User.objects.create_user(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
    
# 유저 프로필 시리얼라이저 정의
class UserProfileSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email','username','profile_image','nickname','birth','gender','introduce']  # 반환할 필드

    def get_profile_image(self, obj):
        request = self.context.get('request')  # Serializer context에서 request 가져오기
        if obj.profile_image:
            if request:
                return request.build_absolute_uri(obj.profile_image.url)
            return obj.profile_image.url
        return None
    
# 유저 정보 수정 시리얼라이저 정의
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['profile_image','nickname','gender','introduce',]  
