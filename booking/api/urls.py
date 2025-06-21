from django.urls import path
from booking.api.views import (
    api_complaint_detail_view,
    api_update_match_doctor_view,
    api_match_doctor_view,
    api_create_appointment_view,
    api_update_appointment_view,
    api_appointment_detail_view,
    api_book_meet_view,
    api_meet_detail_view,
    api_confirm_meet_view,
    api_end_meet_view,
    api_root,
    api_meet_list_view,
    api_complaint_list_view,
    SymptomsList
)


urlpatterns = [
    path('root/', api_root),
    path('complaint/match/', api_match_doctor_view, name='results'),
    path('complaint/list/', api_complaint_list_view.as_view(), name='complaint-list'),
    path('complaint/<int:pk>/', api_complaint_detail_view, name='complaint-detail'),
    path('complaint/<int:pk>/update/', api_update_match_doctor_view, name='complaint-update'),
    path('meet/list/', api_meet_list_view.as_view(), name='meet-list'),
    path('meet/<str:username>/book/', api_book_meet_view, name='book-meet'),
    path('meet/<str:ID>/', api_meet_detail_view, name='meet-detail'),
    path('meet/<str:ID>/confirm/', api_confirm_meet_view, name='confirm-meet'),
    path('meet/<str:ID>/end/', api_end_meet_view, name='end-meet'),
    path('appointment/<str:username>/create/', api_create_appointment_view, name='appointment-create'),
    path('appointment/<int:pk>/', api_appointment_detail_view, name='appointment-detail'),
    path('appointment/<int:pk>/update/', api_update_appointment_view, name='appointment-update'),
    path('symptoms/list/', SymptomsList.as_view(), name='symptoms-list')
]