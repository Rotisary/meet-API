from django.urls import path
from booking.api.views import (
    api_illness_detail_view,
    api_update_illness_view,
    api_delete_illness_view,
    api_create_illness_view,
    api_root,
    api_illness_list_view,
)


urlpatterns = [
    path('', api_root),
    path('illness/<int:pk>/', api_illness_detail_view, name='illness-detail'),
    path('illness/<int:pk>/update/', api_update_illness_view, name='illness-update'),
    path('illness/<int:pk>/delete', api_delete_illness_view, name='illness-delete'),
    path('illness/create', api_create_illness_view, name='illness-create'),
    path('illness/list/', api_illness_list_view.as_view(), name='illness-list'),
]