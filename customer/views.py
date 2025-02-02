from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Service

@api_view(['GET'])
def get_services(request):
    services = Service.objects.all()  # Fetch all services from the database
    data = [
        {"name": service.name, "price": str(service.price)}
        for service in services
    ]
    return Response(data)