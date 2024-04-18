from rest_framework import status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.decorators import api_view, permission_classes, parser_classes, renderer_classes
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.authentication import TokenAuthentication
from rest_framework.filters import SearchFilter, OrderingFilter

from booking.models import Illness
from booking.api.serializers import IllnessSerializer


@api_view(['GET', ])
def api_root(request):
    return Response({
        'user': reverse('user-list', request=request),
        'illness': reverse('illness-list', request=request)
    })

@api_view(['POST', ])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser, MultiPartParser])
def api_create_illness_view(request):  
    illness = Illness(patient=request.user)

    if request.user.category == 'DR':
        return Response({'response': 'you are not allowed to enter illness details, sign up for a patient account to do that'},
                        status=status.HTTP_403_FORBIDDEN)
     
    if request.method == 'POST':
        serializer = IllnessSerializer(illness, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PUT', ])
@permission_classes([IsAuthenticated])
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
    
    if request.method == 'GET':
        serializer = IllnessSerializer(illness, context={'request': request})
        return Response(serializer.data)


class api_illness_list_view(ListAPIView):
    queryset = Illness.objects.all()
    serializer_class = IllnessSerializer
    zauthentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer, BrowsableAPIRenderer)
    pagination_class = PageNumberPagination
    filter_backends = ([SearchFilter, OrderingFilter])
    search_fields = ['body_part', 'illness', 'patient__first_name', 'patient__last_name']