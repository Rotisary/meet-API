from django.urls import path
from users.api.views import (
    registration_view,
    api_user_detail_view,
    api_profile_view,
    api_update_profile_view,
    api_update_user_detail_view,
    api_request_otp_view,
    api_verify_otp_view,
    api_delete_user_view,
    api_create_review_view,
    api_review_detail_view,
    api_delete_review_view,
    api_review_list_view,
    CreateAPIAccount,
    ObtainAuthTokenView,
    ChangePasswordApiView,
)


urlpatterns = [
    path('register/', registration_view, name='register'),
    path('login/', ObtainAuthTokenView.as_view(), name='login'),
    path('details/<str:username>/', api_user_detail_view, name='user-detail'),
    path('profile/<slug:slug>/', api_profile_view, name='profile-detail'),
    path('profile/<slug:slug>/update/', api_update_profile_view, name='doctor-profile-update'),
    path('details/<str:username>/update/', api_update_user_detail_view, name='patient-profile-update'),
    path('<str:username>/delete', api_delete_user_view, name='delete-user'),
    path('request-otp/', api_request_otp_view, name='request-otp'),
    path('verify-otp/<str:email>/', api_verify_otp_view, name='verify-otp'),
    path('change-password/', ChangePasswordApiView.as_view(), name='change-password'),
    path('review/<str:username>/create/', api_create_review_view, name='create-review'),
    path('review/<int:pk>/', api_review_detail_view, name='doctorreview-detail'),
    path('review/<int:pk>/delete', api_delete_review_view, name='delete-review'),
    path('reviews/<str:username>/list/', api_review_list_view, name='review-list'),
    path('register/apiuser/', CreateAPIAccount, name='create-api-account')
]