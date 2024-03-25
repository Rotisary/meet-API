from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from booking.models import IllnessDetail
from booking.api.serializers import IllnessDetailSerializer


@api_view(['GET', ])
@permission_classes([IsAuthenticated])
def api_detail_illness_detail_view(request, pk):
    try:
        illness_detail = IllnessDetail.objects.get(id=pk)
    except IllnessDetail.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = IllnessDetailSerializer(illness_detail)
        return Response(serializer.data)
    
@api_view(['PUT', ])
@permission_classes([IsAuthenticated])
def api_update_illness_detail_view(request, pk):
    try:
        illness_detail = IllnessDetail.objects.get(id=pk)
    except IllnessDetail.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    user = request.user
    if illness_detail.patient != user:
        return Response({'response': 'you are not allowed to update this illness detail'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'PUT':
        serializer = IllnessDetailSerializer(illness_detail, data=request.data)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data['success'] = 'update successful'
            return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE', ])
@permission_classes([IsAuthenticated])
def api_delete_illness_detail_view(request, pk):
    try:
        illness_detail = IllnessDetail.objects.get(id=pk)
    except IllnessDetail.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    user = request.user
    if illness_detail.patient != user:
        return Response({'response': 'you are not allowed to delete that!'}, status=status.HTTP_403_FORBIDDEN)
       
    if request.method == 'DELETE':
        operation = illness_detail.delete()
        data = {}
        if operation:
            data['success'] = 'delete successful'
        else:
            data['failure'] = 'delete failed'
        return Response(data=data)
    

@api_view(['POST', ])
@permission_classes([IsAuthenticated])
def api_create_illness_detail_view(request):  
    illness_detail = IllnessDetail(patient=request.user)

    if request.user.category == 'DR':
        return Response({'response': 'you are not allowed to enter illness details, sign up for a patient account to do that'},
                        status=status.HTTP_403_FORBIDDEN)
     
    if request.method == 'POST':
        serializer = IllnessDetailSerializer(illness_detail, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)