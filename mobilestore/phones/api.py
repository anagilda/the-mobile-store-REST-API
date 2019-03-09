from .models import Phone
from rest_framework import viewsets, permissions
from .serializers import PhoneListSerializer, PhoneDetailSerializer
from .pagination import PhonesPagination

class PhoneViewSet(viewsets.ReadOnlyModelViewSet):
    ''' Phone Viewset. '''
    queryset = Phone.objects.all()
    permission_classes = [ permissions.IsAuthenticatedOrReadOnly ]
    pagination_class = PhonesPagination
    serializers = {
        'list': PhoneListSerializer,
        'retrieve': PhoneDetailSerializer
    }
    
    def get_serializer_class(self):
        # Overwriting method for viewset to have several serializers
        return self.serializers.get(self.action)