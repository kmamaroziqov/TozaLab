from rest_framework import serializers
from .models import Service, Booking
from .models import User

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'price', 'description', 'updated', 'created']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'is_customer', 'is_provider', 'phone', 'address']
        extra_kwargs = {'password': {'write_only': True}}  # Hide password in responses

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'customer', 'service', 'date', 'status', 'notes']
        read_only_fields = ['customer']  # Customer is set automatically

class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['service', 'date', 'notes']