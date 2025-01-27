from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    사용자 정보를 직렬화하는 시리얼라이저
    
    Attributes:
        email: 사용자 이메일
        nickname: 사용자 닉네임
        profile_image: 프로필 이미지
        birth_date: 생년월일
        gender: 성별
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'nickname')

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('bio', 'profile_image', 'location')

class UserDetailSerializer(UserSerializer):
    profile = ProfileSerializer(read_only=True)
    
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('profile',)

class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'nickname', 'password', 'password2', 'birth_date', 'gender')
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):
        if data['password'] != data.pop('password2'):
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")
        validate_password(data['password'])
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            nickname=validated_data['nickname'],
            password=validated_data['password'],
            birth_date=validated_data.get('birth_date'),
            gender=validated_data.get('gender')
        )
        return user

class SignupSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('email', 'password', 'password2', 'nickname')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({
                "password": "비밀번호가 일치하지 않습니다."
            })
        return data

    def create(self, validated_data):
        validated_data.pop('password2')  # password2 필드 제거
        return User.objects.create_user(**validated_data)

class UserProfileSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()
    # liked_articles 필드 임시 비활성화
    articles_count = serializers.SerializerMethodField()
    itineraries_count = serializers.SerializerMethodField()
    itineraries = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'nickname', 'profile_image', 
            'birth_date', 'gender', 'bio',
            'articles_count', 'itineraries_count', 'itineraries'
        )
        read_only_fields = ('email',)

    def get_profile_image(self, obj):
        request = self.context.get('request')
        if obj.profile_image:
            if request:
                return request.build_absolute_uri(obj.profile_image.url)
            return obj.profile_image.url
        return None

    def get_articles_count(self, obj):
        return 0  # 임시로 0 반환
        # return obj.articles.count()

    def get_itineraries_count(self, obj):
        return 0  # 임시로 0 반환
        # return obj.itineraries.count()

    def get_itineraries(self, obj):
        # 나중에 Itinerary 모델이 준비되면 실제 데이터로 교체
        return []

# 유저 정보 수정 시리얼라이저 정의
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['profile_image', 'nickname', 'gender', 'bio']