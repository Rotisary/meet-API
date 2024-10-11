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
from rest_framework.exceptions import NotFound, PermissionDenied

from booking.models import Complaint, Appointment, Symptom
from users.models import Profile, User
from booking.api.serializers import ComplaintSerializer, AppointmentSerializer, SymptomSerializer
from users.api.serializers import ProfileSerializer
from booking.api.custom_permissions import (
    UserIsDoctor, 
    UserIsPatient, 
    ComplaintDetailPerm, 
    AppointmentDetailPerm, 
    DoctorsComplaintPerm
)
from booking.api.requests_functions import get_token, get_api_data
import requests


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
def api_create_complaint_view(request):  
     
    if request.method == 'POST':
        serializer = ComplaintSerializer(data=request.data, context={'request': request})
        symptoms = request.query_params.get('symptoms')
        if not symptoms:
            return Response(data={'error': 'please add symptoms to query_parameter'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            splited_symptoms = symptoms.split('_')
            symptoms_list = []
            for item in splited_symptoms:
                symptoms_list.append(int(item))

            if serializer.is_valid(raise_exception=True):
                new_complaint = serializer.save(patient=request.user)
                try:
                    complaint = Complaint.objects.get(id=new_complaint.id)
                    for symptom in symptoms_list:
                        try:
                            model_symptom = Symptom.objects.get(ID=symptom)
                            complaint.symptoms.add(model_symptom)
                        except Symptom.DoesNotExist:
                            raise NotFound(detail="sorry, couldn't process your symptom. Please use different keywords")
                    complaint.save()
                except Complaint.DoesNotExist:
                    raise NotFound(detail='the complaint was not found')
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        
@api_view(['PUT', ])
@permission_classes([IsAuthenticated,])
@parser_classes([JSONParser, MultiPartParser])
def api_update_complaint_view(request, pk):
    try:
        complaint = Complaint.objects.get(id=pk)
    
        user = request.user
        if complaint.patient != user:
            raise PermissionDenied
        
        if request.method == 'PUT':
            serializer = ComplaintSerializer(complaint, data=request.data, partial=True)
            symptoms = request.query_params.get('symptoms')
            data = {}
            if not symptoms:
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    data['success'] = 'update successful'
                    return Response(data=data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                splited_symptoms = symptoms.split('_')
                symptoms_list = []
                for item in splited_symptoms:
                    symptoms_list.append(int(item))
    
                for symptom in symptoms_list:
                    try:
                        model_symptom = Symptom.objects.get(ID=symptom)
                        complaint.symptoms.add(model_symptom)
                    except Symptom.DoesNotExist:
                        raise NotFound(detail="sorry, couldn't process your symptom. Please use different keywords")
                    
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    complaint.save()
                    data['success'] = 'update successful'
                    return Response(data=data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Complaint.DoesNotExist:
         raise NotFound(detail='this complaint does not exist')
    

@api_view(['DELETE', ])
@permission_classes([IsAuthenticated])
def api_delete_complaint_view(request, pk):
    try:
        complaint = Complaint.objects.get(id=pk)
    
        user = request.user
        if complaint.patient != user:
            raise PermissionDenied
        
        if request.method == 'DELETE':
            operation = complaint.delete()
            data = {}
            if operation:
                data['success'] = 'delete successful'
            else:
                data['failure'] = 'delete failed'
            return Response(data=data)
    except Complaint.DoesNotExist:
        raise NotFound(detail='this complaint does not exist')
    

@api_view(['GET', ])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer, BrowsableAPIRenderer])
def api_complaint_detail_view(request, pk):
    try:
        complaint = Complaint.objects.get(id=pk)
    
        permission_class = ComplaintDetailPerm()
        if not permission_class.has_object_permission(request, None, complaint):
            raise PermissionDenied
        else:
            if request.method == 'GET':
                serializer = ComplaintSerializer(complaint, context={'request': request})
                return Response(serializer.data)
    except Complaint.DoesNotExist:
        raise NotFound(detail='this complaint does not exist')


class api_complaint_list_view(ListAPIView):
    serializer_class = ComplaintSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, UserIsDoctor, DoctorsComplaintPerm)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)
    filter_backends = ([SearchFilter, OrderingFilter])
    search_fields = ['symptoms__Name','age_group', 'patient__first_name', 'patient__last_name']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.query_params.get('username')
        queryset = Complaint.objects.filter(treated_by__user__username=user)
        return queryset


@api_view(['GET', ])
@permission_classes([IsAuthenticated, UserIsPatient])
def api_related_doctors_list_view(request, pk):
    if request.method == 'GET':
        secret_key = 'Fp78JnAf62SmTg35D'
        requested_uri = "https://authservice.priaid.ch/login"
        # get apimedic authentication token
        token = get_token(secret_key, requested_uri)

        try:
            # get arguments for api data function
            complaint = Complaint.objects.get(id=pk)
            symptom_id_list = []
            symptoms = complaint.symptoms.all()
            for symptom in symptoms:
                id = symptom.ID
                symptom_id_list.append(id)

            sex = complaint.sex
            year_of_birth = complaint.year_of_birth
            age_group = complaint.age_group

            # call get api data function
            specialisations_list, issues = get_api_data(
                token, 
                symptom_id_list, 
                sex, 
                year_of_birth
            )

            # filter doctors and them to data list
            doctors = Profile.objects.all()
            doctors_that_match = []

            for doctor in doctors:
                for specialisation_data in specialisations_list:
                    if doctor.specialization == specialisation_data and doctor.patient_type == age_group:
                        doctors_that_match.append(doctor)         

            data = {
                'possible illness': issues
            }
            if not doctors_that_match:
                data['message'] = "sorry, we don't any have doctor that can treat your probable illness. Please try again later"
            else:
                # sort data list
                doctors_that_match_sorted = sorted(doctors_that_match, key=lambda doctor: -doctor.rating)
                serializer = ProfileSerializer(set(doctors_that_match_sorted), many=True, context={'request': request})

                # remove unwanted fields from data
                for object in serializer.data:
                    object.pop('meets')
                    object.pop('appointments_booked')
                    object.pop('id')
                    object.pop('slug')
                    object.pop('reviews')

                data['doctor suggestions'] = serializer.data
            return Response(data=data, status=status.HTTP_200_OK)
        except Complaint.DoesNotExist:
            raise NotFound(detail='this complaint does not exist')


@api_view(['POST', ])
@permission_classes([IsAuthenticated, UserIsPatient])
def api_add_to_doctors_meet_view(request, username, pk):
    try:
        doctor = Profile.objects.get(user__username=username)
        patient = request.user
        try:
            complaint = Complaint.objects.get(id=pk)
            data = {}
            if doctor.meets.filter(id=patient.id):
                doctor.meets.remove(patient)
                data['message'] = "you have removed yourself from this doctor's meet"
            else:
                if doctor.number_of_meet() < 3:
                    doctor.meets.add(patient)
                    complaint.treated_by = doctor
                    complaint.save()
                    data['message'] = "you have succesfully added yourself to this doctor's meet"
                else:
                    data['message'] = "this doctor already has three meets, please find another qualified doctor"
            return Response(data=data, status=status.HTTP_200_OK)
        except Complaint.DoesNotExist:
            raise NotFound(detail='this complaint does not exist')
    except Profile.DoesNotExist:
        raise NotFound(detail='this profile does not exist')


@api_view(['POST', ])
@permission_classes([IsAuthenticated, UserIsDoctor])
@parser_classes([JSONParser, MultiPartParser])
def api_create_appointment_view(request, username):  
    try:    
        appointment_patient = User.objects.get(username=username)
    
        if request.method == 'POST':
            serializer = AppointmentSerializer(data=request.data, context={'request': request})
            if serializer.is_valid(raise_exception=True):
                serializer.save(owner=request.user.profile, patient=appointment_patient)
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    data['success'] = 'update successful'
                    return Response(data=data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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
                return Response(serializer.data)
    except Appointment.DoesNotExist:
        raise NotFound(detail='this appointment does not exist')