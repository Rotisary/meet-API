from django.urls import path
from users.api.views import (
    registration_view,
    api_user_detail_view,
    api_profile_view,
    api_update_profile_view,
    api_update_user_detail_view,
    api_create_review_view,
    api_review_detail_view,
    api_review_list_view,
    ObtainAuthTokenView,
    ChangePasswordApiView,
)


urlpatterns = [
    path('register/', registration_view, name='register'),
    path('login/', ObtainAuthTokenView.as_view(), name='login'),
    path('<str:username>/detail/', api_user_detail_view, name='user-detail'),
    path('change-password/', ChangePasswordApiView.as_view(), name='change-password'),
    path('profile/<str:username>/', api_profile_view, name='profile-detail'),
    path('profile/dr/<str:username>/update/', api_update_profile_view, name='doctor-profile-update'),
    path('details/<str:username>/update/', api_update_user_detail_view, name='patient-profile-update'),
    path('review/<str:username>/create/', api_create_review_view, name='create-review'),
    path('review/<int:pk>/', api_review_detail_view, name='doctorreview-detail'),
    path('reviews/<str:username>/list/', api_review_list_view, name='review-list')
]