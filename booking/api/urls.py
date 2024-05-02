from django.urls import path
from booking.api.views import (
    api_illness_detail_view,
    api_update_illness_view,
    api_delete_illness_view,
    api_create_illness_view,
    api_create_appointment_view,
    api_update_appointment_view,
    api_appointment_detail_view,
    api_related_doctors_list_view,
    api_add_to_doctors_meet_view,
    api_root,
    # api_illness_list_view,
)


urlpatterns = [
    path('', api_root),
    path('illness/<int:pk>/', api_illness_detail_view, name='illness-detail'),
    path('illness/<int:pk>/update/', api_update_illness_view, name='illness-update'),
    path('illness/<int:pk>/delete', api_delete_illness_view, name='illness-delete'),
    path('illness/create', api_create_illness_view, name='illness-create'),
    path('<str:specialty>/<int:pt_age>/results/', api_related_doctors_list_view, name='results'),
    # path('illness/list/', api_illness_list_view.as_view(), name='illness-list'),
    path('appointment/create/<str:username>/', api_create_appointment_view, name='appointment-create'),
    path('appointment/<int:pk>/', api_appointment_detail_view, name='appointment-detail'),
    path('appointment/<int:pk>/update/', api_update_appointment_view, name='appointment-update'),
    path('meet/<str:username>/add/', api_add_to_doctors_meet_view, name='add-to-meet')
]