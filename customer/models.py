from django.db import models
from django.contrib.auth.models import AbstractUser

class Service(models.Model):
    name = models.CharField(max_length=100)  # Text field (e.g., "Plumbing")
    price = models.DecimalField(max_digits=10, decimal_places=2)  # e.g., 50.00
    description = models.TextField(null = True, blank = True)   # Long text (e.g., "24/7 plumbing services")
    updated = models.DateTimeField(auto_now = True)
    created = models.DateTimeField(auto_now_add = True)
    
    def __str__(self):
        return self.name

class User(AbstractUser):
    is_customer = models.BooleanField(default=False)
    is_provider = models.BooleanField(default=False)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

class Booking(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    notes = models.TextField(blank=True)