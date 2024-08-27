from rest_framework import status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.decorators import (
    api_view, 
    permission_classes, 
    parser_classes, 
    renderer_classes, 
    throttle_classes,
    )
# from django.views.decorators.cache import cache_page
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import TokenAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter

from booking.models import Illness, Appointment
from users.models import Profile, User
from booking.api.serializers import IllnessSerializer, AppointmentSerializer
from users.api.serializers import ProfileSerializer
from booking.api.custom_permissions import (
    UserIsDoctor, 
    UserIsPatient, 
    IllnessDetailPerm, 
    AppointmentDetailPerm, 
    DoctorsIllnessPerm
)


@api_view(['GET', ])
def api_root(request):
    return Response({
        'user': reverse('user-list', request=request),
        'illness': reverse('illness-list', request=request)
    })


@api_view(['POST', ])
@permission_classes([IsAuthenticated, UserIsPatient])
@parser_classes([JSONParser, MultiPartParser])
def api_create_illness_view(request):  
    illness = Illness(patient=request.user)
     
    if request.method == 'POST':
        serializer = IllnessSerializer(illness, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    

@api_view(['PUT', ])
@permission_classes([IsAuthenticated,])
@parser_classes([JSONParser, MultiPartParser])
def api_update_illness_view(request, pk):
    try:
        illness = Illness.objects.get(id=pk)
    except Illness.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    user = request.user
    if illness.patient != user:
        return Response({'response': 'you are not allowed to update this illness detail'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'PUT':
        serializer = IllnessSerializer(illness, data=request.data, partial=True)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data['success'] = 'update successful'
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['DELETE', ])
@permission_classes([IsAuthenticated])
def api_delete_illness_view(request, pk):
    try:
        illness = Illness.objects.get(id=pk)
    except Illness.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    user = request.user
    if illness.patient != user:
        return Response({'response': 'you are not allowed to delete that!'}, status=status.HTTP_403_FORBIDDEN)
       
    if request.method == 'DELETE':
        operation = illness.delete()
        data = {}
        if operation:
            data['success'] = 'delete successful'
        else:
            data['failure'] = 'delete failed'
        return Response(data=data)
    

@api_view(['GET', ])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer, BrowsableAPIRenderer])
def api_illness_detail_view(request, pk):
    try:
        illness = Illness.objects.get(id=pk)
    except Illness.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    permission_class = IllnessDetailPerm()
    if not permission_class.has_object_permission(request, None, illness):
        return Response({'error': 'permission denied'}, status=status.HTTP_403_FORBIDDEN)
    else:
        if request.method == 'GET':
            serializer = IllnessSerializer(illness, context={'request': request})
            return Response(serializer.data)


class api_illness_list_view(ListAPIView):
    serializer_class = IllnessSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, UserIsDoctor, DoctorsIllnessPerm)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)
    filter_backends = ([SearchFilter, OrderingFilter])
    search_fields = ['body_part', 'specific_illness', 'patient__first_name', 'patient__last_name']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.query_params.get('username')
        queryset = Illness.objects.filter(treated_by__username=user)
        return queryset


# needs a lil' change
@api_view(['GET', ])
@permission_classes([IsAuthenticated, UserIsPatient])
def api_related_doctors_list_view(request, specialty, pt_age):
    if request.method == 'GET':
        if pt_age <= 18:
            doctors = Profile.objects.filter(specialized_field=specialty, doctor_type='pediatrician')
        elif pt_age > 18 and pt_age < 40 :
            doctors = Profile.objects.filter(specialized_field=specialty, doctor_type='internist')
        elif pt_age > 40:
            doctors = Profile.objects.filter(specialized_field=specialty, doctor_type='geriatrician')
 
        serializer = ProfileSerializer(doctors, many=True, context={'request': request})
        data = serializer.data
        return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, UserIsPatient])
def api_add_to_doctors_meet_view(request, username):
    doctor = Profile.objects.get(user__username=username)
    patient = request.user
    data = {}
    if doctor.meet.filter(id=patient.id):
        doctor.meet.remove(patient)
        data['message'] = "you have removed yourself from this doctor's meet"
    else:
        if doctor.number_of_meet() < 3:
            doctor.meet.add(patient)
            data['message'] = "you have succesfully added yourself to this doctor's meet"
        else:
            data['message'] = "this doctor already has three meets, please find another qualified doctor"
    return Response(data=data, status=status.HTTP_200_OK)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, UserIsDoctor])
@parser_classes([JSONParser, MultiPartParser])
def api_create_appointment_view(request, username):  
    try:    
        appointment_patient = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'POST':
        serializer = AppointmentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(owner=request.user.profile, patient=appointment_patient)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PUT', ])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser, MultiPartParser])
def api_update_appointment_view(request, pk):
    try:
        appointment = Appointment.objects.get(id=pk)
    except Appointment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    user = request.user
    if appointment.owner != user.profile:
        return Response({'response': 'you are not allowed to update this appointment'}, status=status.HTTP_403_FORBIDDEN)
    else:
        if request.method == 'PUT':
            serializer = AppointmentSerializer(appointment, data=request.data, partial=True)
            data = {}
            if serializer.is_valid():
                serializer.save()
                data['success'] = 'update successful'
                return Response(data=data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET', ])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer, BrowsableAPIRenderer])
def api_appointment_detail_view(request, pk):
    try:
        appointment = Appointment.objects.get(id=pk)
    except Appointment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    permission_class = AppointmentDetailPerm()
    if not permission_class.has_object_permission(request, None, appointment):
        return Response({'error': 'permission denied'}, status=status.HTTP_403_FORBIDDEN)
    else:
        if request.method == 'GET':
            serializer = AppointmentSerializer(appointment, context={'request': request})
            return Response(serializer.data)