from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # REST FRAMEWORK URLS
    path('api/booking/', include('booking.api.urls')),
    path('api/users/', include('users.api.urls')),
]
