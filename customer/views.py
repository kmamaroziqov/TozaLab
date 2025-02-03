from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Service
from .serializers import ServiceSerializer
from rest_framework.permissions import IsAuthenticated
from .models import User
from .serializers import UserSerializer
from .models import Booking
from .serializers import BookingSerializer, BookingCreateSerializer

class ServiceList(APIView):
    def get(self, request):
        services = Service.objects.all()
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ServiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ServiceDetail(APIView):
    def get(self, request, id):
        service = get_object_or_404(Service, id=id)
        serializer = ServiceSerializer(service)
        return Response(serializer.data)

    def put(self, request, id):
        service = get_object_or_404(Service, id=id)
        serializer = ServiceSerializer(service, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        service = get_object_or_404(Service, id=id)
        service.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class UserRegister(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfile(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class BookingList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bookings = Booking.objects.filter(customer=request.user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookingCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(customer=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BookingDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        booking = get_object_or_404(Booking, id=id, customer=request.user)
        serializer = BookingSerializer(booking)
        return Response(serializer.data)

    def put(self, request, id):
        booking = get_object_or_404(Booking, id=id, customer=request.user)
        serializer = BookingSerializer(booking, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        booking = get_object_or_404(Booking, id=id, customer=request.user)
        booking.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)