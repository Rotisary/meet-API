from django.urls import path
from booking.api.views import (
    api_complaint_detail_view,
    api_update_complaint_view,
    api_delete_complaint_view,
    api_create_complaint_view,
    api_create_appointment_view,
    api_update_appointment_view,
    api_appointment_detail_view,
    api_related_doctors_list_view,
    api_add_to_doctors_meet_view,
    api_root,
    api_complaint_list_view,
)


urlpatterns = [
    path('', api_root),
    path('complaint/<int:pk>/', api_complaint_detail_view, name='complaint-detail'),
    path('complaint/<int:pk>/update/', api_update_complaint_view, name='complaint-update'),
    path('complaint/<int:pk>/delete', api_delete_complaint_view, name='complaint-delete'),
    path('complaint/create', api_create_complaint_view, name='complaint-create'),
    path('<int:pk>/match/results/', api_related_doctors_list_view, name='results'),
    path('complaint/list/', api_complaint_list_view.as_view(), name='complaint-list'),
    path('appointment/create/<str:username>/', api_create_appointment_view, name='appointment-create'),
    path('appointment/<int:pk>/', api_appointment_detail_view, name='appointment-detail'),
    path('appointment/<int:pk>/update/', api_update_appointment_view, name='appointment-update'),
    path('meet/<str:username>/<int:pk>/add/', api_add_to_doctors_meet_view, name='add-to-meet')
]