from django.urls import path, include
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

urlpatterns = [
    url(r'^admin/', admin.site.urls, name='admin'),
    url(r'^$', views.homepage, name='home'),
    url(r'^api/', include(('phones.urls', 'api')), name='api'),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)