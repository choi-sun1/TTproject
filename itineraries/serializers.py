from rest_framework import serializers
from .models import Itinerary, ItineraryDay, ItineraryPlace, ItineraryComment, Place

class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = [
            'id', 'name', 'description', 'address', 
            'latitude', 'longitude', 'place_type',
            'google_place_id', 'rating', 'price_level'
        ]

class ItineraryPlaceSerializer(serializers.ModelSerializer):
    place = PlaceSerializer(read_only=True)
    place_id = serializers.PrimaryKeyRelatedField(
        queryset=Place.objects.all(),
        source='place',
        write_only=True
    )

    class Meta:
        model = ItineraryPlace
        fields = ['id', 'place', 'place_id', 'day', 'order', 'note']

class ItineraryDaySerializer(serializers.ModelSerializer):
    places = ItineraryPlaceSerializer(many=True, read_only=True)

    class Meta:
        model = ItineraryDay
        fields = ['id', 'day_number', 'date', 'places']

class ItineraryCommentSerializer(serializers.ModelSerializer):
    author_nickname = serializers.CharField(source='author.nickname', read_only=True)
    author_profile = serializers.ImageField(source='author.profile_image', read_only=True)

    class Meta:
        model = ItineraryComment
        fields = [
            'id', 'author_nickname', 'author_profile',
            'content', 'created_at'
        ]
        read_only_fields = ['created_at']

class ItineraryDetailSerializer(serializers.ModelSerializer):
    places = ItineraryPlaceSerializer(
        source='itineraryplace_set',
        many=True,
        read_only=True
    )
    total_days = serializers.SerializerMethodField()

    class Meta:
        model = Itinerary
        fields = [
            'id', 'title', 'description', 'start_date',
            'end_date', 'is_public', 'places', 'total_days',
            'created_at', 'updated_at'
        ]

    def get_total_days(self, obj):
        if obj.start_date and obj.end_date:
            return (obj.end_date - obj.start_date).days + 1
        return 0

# 중복된 ItinerarySerializer 제거하고 하나로 통합
class ItinerarySerializer(serializers.ModelSerializer):
    days = ItineraryDaySerializer(many=True, read_only=True)
    comments = ItineraryCommentSerializer(many=True, read_only=True)
    author_nickname = serializers.CharField(source='author.nickname', read_only=True)
    author_profile = serializers.ImageField(source='author.profile_image', read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    is_liked = serializers.SerializerMethodField()
    total_days = serializers.SerializerMethodField()

    class Meta:
        model = Itinerary
        fields = [
            'id', 'title', 'description', 'author_nickname', 'author_profile',
            'start_date', 'end_date', 'is_public', 'views',
            'likes_count', 'is_liked', 'total_days', 'days', 'comments',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['views', 'likes_count', 'total_days']

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

    def get_total_days(self, obj):
        if obj.start_date and obj.end_date:
            return (obj.end_date - obj.start_date).days + 1
        return 0
