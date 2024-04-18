from django.urls import path
from users.api.views import (
    registration_view,
    api_user_detail_view,
    api_profile_view,
    api_update_profile_view,
    api_update_user_detail_view,
    ListUserApiView,
    ObtainAuthTokenView,
    ChangePasswordApiView,
)


urlpatterns = [
    path('register/', registration_view, name='register'),
    path('login/', ObtainAuthTokenView.as_view(), name='login'),
    path('list/', ListUserApiView.as_view(), name='user-list'),
    path('<str:username>/detail/', api_user_detail_view, name='user-detail'),
    path('change-password/', ChangePasswordApiView.as_view(), name='change-password'),
    path('profile/<str:username>/', api_profile_view, name='profile-detail'),
    path('profile/dr/<str:username>/update/', api_update_profile_view, name='docotr-profile-update'),
    path('profile/pt/<str:username>/update/', api_update_user_detail_view, name='patient-profile-update')
]