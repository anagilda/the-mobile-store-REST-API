from rest_framework import routers
from .api import PhoneViewSet

router = routers.DefaultRouter()
router.register('api/phones', PhoneViewSet, 'phones')

urlpatterns = router.urls