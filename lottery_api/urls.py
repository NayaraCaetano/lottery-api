from django.conf.urls import url, include
from django.contrib import admin

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="Lottery API",
      default_version='v1',
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)



urlpatterns = [
    url(r'auth/', include('authentication.urls')),

    # Others
    url(r'^admin/', admin.site.urls),

    # Docs
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]