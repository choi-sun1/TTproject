from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'nickname']
        
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'nickname', 'profile_image', 'birth_date', 'gender', 'bio']
        read_only_fields = ['username', 'email']

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['nickname', 'profile_image', 'birth_date', 'gender', 'bio']