from .models import Phone
from rest_framework import viewsets, permissions
from .serializers import PhoneSerializer

class PhoneViewSet(viewsets.ModelViewSet):
    ''' Phone Viewset. '''
    queryset = Phone.objects.all()
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly
    ]
    serializer_class = PhoneSerializer