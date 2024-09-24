from django.contrib import admin
from django.urls import path, include
from rest_framework.schemas import get_schema_view
from users.api.utils import CustomSchemaGenerator
from users.views import docs_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', docs_view, name='docs'),
    # REST FRAMEWORK URLS
    path('api/booking/', include('booking.api.urls')),
    path('api/users/', include('users.api.urls')),

    # project schema path
    path('openapi', 
         get_schema_view(
                         title="MEET", 
                         description="Web-API that allows patient to consult doctors with expertise in the treatment of their illness online", 
                         version="1.0.0",
                        #  generator_class = CustomSchemaGenerator,
                         public=True
                        ),
         name='openapi-schema'          
        )
]
