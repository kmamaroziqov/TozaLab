from django.db import models

class Service(models.Model):
    name = models.CharField(max_length=100)  # Text field (e.g., "Plumbing")
    price = models.DecimalField(max_digits=10, decimal_places=2)  # e.g., 50.00
    description = models.TextField()  # Long text (e.g., "24/7 plumbing services")