from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

shema_view = get_schema_view(
    openapi.Info(
        title='Foodgram API',
        default_version='v1',
        description='Документация для проекта Foodgram',
        contact=openapi.Contact(email='admin@foodgram.com'),
        lisense=openapi.License(name='BSD License'),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    url(
        r'^swagger(?P<format>\.json|\.yaml)$',
        shema_view.without_ui(cache_timeout=0),
        name='schema-json',
    ),
    url(
        r'^swagger/$',
        shema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui',
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
