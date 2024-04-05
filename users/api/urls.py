from django.urls import path
from users.api.views import (
    registration_view,
    ObtainAuthTokenView,
    ChangePasswordApiView,
)


urlpatterns = [
    path('register/', registration_view, name='register'),
    path('login/', ObtainAuthTokenView.as_view(), name='login'),
    path('change-password/', ChangePasswordApiView.as_view(), name='change-password'),
]