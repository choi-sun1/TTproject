from rest_framework import serializers
from .models import Stay, Booking, Review, StayImage

class StayImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StayImage
        fields = ['id', 'image', 'is_main']

class StaySerializer(serializers.ModelSerializer):
    images = StayImageSerializer(many=True, read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    reviews_count = serializers.IntegerField(source='reviews.count', read_only=True)

    class Meta:
        model = Stay
        fields = [
            'id', 'name', 'description', 'address', 'latitude', 'longitude',
            'price_per_night', 'capacity', 'stay_type', 'has_wifi', 'has_parking',
            'has_breakfast', 'images', 'average_rating', 'reviews_count'
        ]

class BookingSerializer(serializers.ModelSerializer):
    stay_name = serializers.CharField(source='stay.name', read_only=True)
    total_nights = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'stay', 'stay_name', 'check_in', 'check_out',
            'guests', 'total_price', 'status', 'total_nights',
            'created_at'
        ]
        read_only_fields = ['total_price', 'status']

    def get_total_nights(self, obj):
        return (obj.check_out - obj.check_in).days

    def validate(self, data):
        if data['check_in'] >= data['check_out']:
            raise serializers.ValidationError(
                "체크아웃 날짜는 체크인 날짜보다 뒤여야 합니다."
            )
        return data

class ReviewSerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)
    user_profile = serializers.ImageField(source='user.profile_image', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id', 'user_nickname', 'user_profile', 'rating',
            'comment', 'created_at'
        ]
        read_only_fields = ['created_at']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("평점은 1에서 5 사이여야 합니다.")
        return value
