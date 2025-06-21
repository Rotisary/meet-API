from rest_framework import status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.decorators import (
    api_view, 
    permission_classes, 
    parser_classes, 
    renderer_classes, 
    )
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from booking.models import Complaint, Meet, Appointment, Symptom
from users.models import Profile, User
from booking.api.serializers import (
    ComplaintSerializer, 
    MeetSerializer,
    AppointmentSerializer, 
    SymptomSerializer
)
from users.api.serializers import ProfileSerializer
from users.api.core.custom_permissions import UserIsPatient, UserIsDoctor
from booking.api.core.custom_permissions import (
    ComplaintPerm, 
    MeetDetailPerm,
    AppointmentDetailPerm, 
    DoctorsComplaintPerm,
    ComplaintUpdatePerm
)
from booking.api.utils.ext_api_helpers import filter_doctors
from booking.api.utils.helpers import split_symptoms, add_complaint_symptoms
import requests
from booking.api.core.tasks import send_meet_end_email

@api_view(['GET', ])
def api_root(request):
    return Response({
        'user': reverse('user-list', request=request),
        'complaint': reverse('complaint-list', request=request)
    })


class SymptomsList(ListAPIView):
    authentication_classes = ([TokenAuthentication, ])
    permission_classes = ([IsAuthenticated, ])
    renderer_classes = ([JSONRenderer, BrowsableAPIRenderer])
    serializer_class = SymptomSerializer
    queryset = Symptom.objects.all()


@api_view(['POST', ])
@permission_classes([IsAuthenticated, UserIsPatient])
@parser_classes([JSONParser, MultiPartParser])
def api_match_doctor_view(request):      
    if request.method == 'POST':
        serializer = ComplaintSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        new_complaint = Complaint(**serializer.validated_data, patient=request.user)                     
        data = filter_doctors(new_complaint, Profile, ProfileSerializer, request) 
        new_complaint.save()
        return Response(data, status=status.HTTP_201_CREATED)

        
@api_view(['PATCH', ])
@permission_classes([IsAuthenticated,])
@parser_classes([JSONParser, MultiPartParser])
def api_update_match_doctor_view(request, pk):
    if request.method == 'PATCH':
        try:
            complaint = Complaint.objects.get(id=pk)

            if complaint.patient != request.user:
                raise PermissionDenied
            else: 
                permission_class = ComplaintUpdatePerm()
                if not permission_class.has_object_permission(request, None, complaint):
                    raise PermissionDenied
                else:         
                    serializer = ComplaintSerializer(
                        complaint, 
                        data=request.data, 
                        partial=True, 
                        context={'request': request}
                    )                            
                    serializer.is_valid(raise_exception=True)
                    result, obj = serializer.save()
                    data = {
                        'message': "Here's your updated list of suggestions",
                        'suggestions': result
                    }
                    return Response(data=data, status=status.HTTP_200_OK)
        except Complaint.DoesNotExist:
            raise NotFound(detail='this complaint does not exist')
    

@api_view(['GET', ])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer, BrowsableAPIRenderer])
def api_complaint_detail_view(request, pk):
    try:
        complaint = Complaint.objects.get(id=pk)
    
        permission_class = ComplaintPerm()
        if not permission_class.has_object_permission(request, None, complaint):
            raise PermissionDenied
        else:
            if request.method == 'GET':
                serializer = ComplaintSerializer(complaint, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
    except Complaint.DoesNotExist:
        raise NotFound(detail='this complaint does not exist')


class api_complaint_list_view(ListAPIView):
    serializer_class = ComplaintSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, UserIsDoctor, ComplaintPerm)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)
    filter_backends = ([SearchFilter, OrderingFilter])
    ordering = ['-created_at']

    def get_queryset(self):
        username = self.request.query_params.get('username')
        if not username:
            raise ValidationError('error. Please add the username of the patient')
        else:
            queryset = Complaint.objects.filter(patient__username=username)
        return queryset


@api_view(['POST', ])
@permission_classes([IsAuthenticated, UserIsPatient])
def api_book_meet_view(request, username):
    try:
        doctor = Profile.objects.get(user__username=username)
        patient = request.user
        complaint_id = request.query_params.get('complaint')
        try:
            complaint = Complaint.objects.get(id=complaint_id)
            data = {}
            status_code = None
            if doctor.active_meets_count() == 3:
                data['message'] = "This doctor is already booked for three meets, please find another doctor"
                status_code = status.HTTP_403_FORBIDDEN
            else:
                meet, created = Meet.objects.get_or_create(
                    doctor=doctor,
                    patient=patient,
                    complaint=complaint
                )
                if not created:
                    if meet.is_confirmed == False:
                        meet.delete()
                        complaint.treated_by = None
                        complaint.save()
                    else:
                        data['message'] = "You cannot cancel this meet, it has already been confirmed by the doctor"
                        status_code = status.HTTP_400_BAD_REQUEST
                else:
                    complaint.treated_by = doctor
                    complaint.save()
                    data['message'] = "you have succesfully booked a meet with this doctor"
                    status_code = status.HTTP_201_CREATED
            return Response(data=data, status=status_code)
        except Complaint.DoesNotExist:
            raise NotFound(detail='sorry, seems this complaint has already been deleted')
    except Profile.DoesNotExist:
        raise NotFound(detail='this doctor does not exist')
    

@api_view(['GET'])
@permission_classes([IsAuthenticated, ])
@renderer_classes([JSONRenderer, BrowsableAPIRenderer])
def api_meet_detail_view(request, ID):
    try:
        meet = Meet.objects.get(ID=ID)

        permission_class = MeetDetailPerm()
        if not permission_class.has_object_permission(request, None, meet):
            raise PermissionDenied(detail='you cannot access this meet')
        else:
            serializer = MeetSerializer(meet, context={'request': request})
            return Response(data=serializer.data, status=status.HTTP_200_OK)
    except Meet.DoesNotExist:
        raise NotFound(detail='this meet does not exist')
    

@api_view(['GET', ])
@permission_classes([IsAuthenticated, UserIsDoctor])
def api_confirm_meet_view(request, ID):
    try:
        meet = Meet.objects.get(ID=ID)
        if meet.doctor != request.user.profile:
            raise PermissionDenied
        else:
            if meet.is_confirmed == False:
                meet.is_confirmed = True
                meet.save()
                return Response(data='You have confirmed this meet', status=status.HTTP_200_OK)
            else:
                raise PermissionDenied(detail='this meet has already been confirmed')
    except Meet.DoesNotExist:
        raise NotFound(detail='this meet does not exist')
    

@api_view(['GET', ])
@permission_classes([IsAuthenticated, UserIsPatient])
def api_end_meet_view(request, ID):
    try:
        meet = Meet.objects.get(ID=ID)
        if meet.patient != request.user:
            raise PermissionDenied
        else:
            if meet.is_confirmed == True:
                meet.has_ended = True
                meet.save()
                send_meet_end_email.delay_on_commit(meet.ID, meet.patient.email, meet.doctor.user.email)
                return Response(data='You have ended this meet', status=status.HTTP_200_OK)
            else:
                raise PermissionDenied(detail='you cannot end this meet, it has not been confirmed by the doctor yet')
    except meet.DoesNotExist:
        raise NotFound(detail='this meet does not exist')
    

class api_meet_list_view(ListAPIView):
    serializer_class = MeetSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, )
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)
    filter_backends = ([SearchFilter, OrderingFilter])
    search_fields = [
        'complaint__symptoms__ID', 
        'doctor__user__first_name',
        'doctor__user__last_name', 
        'patient__first_name', 
        'patient__last_name'
    ]
    ordering = ['-created_at']


    def get_queryset(self):
        user = self.request.user
        active = self.request.query_params.get('active')

        if not active:
            raise ValidationError("The 'active' query parameter is required.")
        else:
            if user.category == 'DR':
                if active == 'true':
                    queryset = Meet.filtered_objects.get_active_meets().filter(doctor__user=user)
                elif active == 'false':
                    queryset = Meet.filtered_objects.get_ended_meets().filter(doctor__user=user)
                else:
                    raise ValidationError("The 'active' query parameter can only be true or false.")
            elif user.category == 'PT':
                if active == 'true':
                    queryset = Meet.filtered_objects.get_active_meets().filter(patient=user)
                elif active == 'false':
                    queryset = Meet.filtered_objects.get_ended_meets().filter(patient=user)
                else:
                    raise ValidationError("The 'active' query parameter can only be true or false.")
            return queryset


@api_view(['POST', ])
@permission_classes([IsAuthenticated, UserIsDoctor])
@parser_classes([JSONParser, MultiPartParser])
def api_create_appointment_view(request, username):  
    try:    
        appointment_patient = User.objects.get(username=username)
    
        if request.method == 'POST':
            serializer = AppointmentSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save(owner=request.user.profile, patient=appointment_patient)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
    except User.DoesNotExist:
        raise NotFound(detail='this patient does not exist')
    

@api_view(['PUT', ])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser, MultiPartParser])
def api_update_appointment_view(request, pk):
    try:
        appointment = Appointment.objects.get(id=pk)
    
        user = request.user
        if appointment.owner != user.profile:
             raise PermissionDenied
        else:
            if request.method == 'PUT':
                serializer = AppointmentSerializer(appointment, data=request.data, partial=True)
                data = {}
                serializer.is_valid(raise_exception=True)
                serializer.save()
                data['success'] = 'update successful'
                return Response(data=data)
    except Appointment.DoesNotExist:
        raise NotFound(detail='this appointment does not exist')
    

@api_view(['GET', ])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer, BrowsableAPIRenderer])
def api_appointment_detail_view(request, pk):
    try:
        appointment = Appointment.objects.get(id=pk)
    
        permission_class = AppointmentDetailPerm()
        if not permission_class.has_object_permission(request, None, appointment):
             raise PermissionDenied
        else:
            if request.method == 'GET':
                serializer = AppointmentSerializer(appointment, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
    except Appointment.DoesNotExist:
        raise NotFound(detail='this appointment does not exist')
