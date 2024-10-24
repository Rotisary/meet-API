from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes, renderer_classes
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import UpdateAPIView
from rest_framework.exceptions import PermissionDenied, NotFound

from users.api.serializers import (
    UserSerializer, 
    UserUpdateSerializer,
    ProfileSerializer,
    ReviewSerializer, 
    ChangePasswordSerializer,
    APIUserSerializer
)
from users.models import User, Profile, DoctorReview
from booking.api.custom_permissions import UserIsPatient, ReviewDetailPerm
from .utils import CustomPagination
from .custom_functions import update_rating


@api_view(['POST', ])
@permission_classes([])
@parser_classes([JSONParser, MultiPartParser])
def registration_view(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        data = {}
        if serializer.is_valid(raise_exception=True):
            newuser = serializer.save()
            token = Token.objects.get(user=newuser).key
            data['respone'] = 'successfully registered user'
            data['email'] = newuser.email
            data['username'] = newuser.username
            data['category'] = newuser.category
            data['first_name'] = newuser.first_name
            data['last_name'] = newuser.last_name
            data['phone_number'] = newuser.phone_number
            data['token'] = token
        else:
            data = serializer.errors
        return Response(data)
 

@api_view(['POST', ])
@permission_classes([])
def CreateAPIAccount(request):
    if request.method == "POST":
        serializer = APIUserSerializer(data=request.data, context={'request': request})
        data = {}
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            token = Token.objects.get(user=user).key
            data['response'] = 'account created'
            data['token'] = token
        else:
            data = serializer.errors

        return Response(data=data, status=status.HTTP_201_CREATED)


class ObtainAuthTokenView(APIView):
    authentication_classes = []
    permission_classes = []
    parser_classes = [JSONParser, MultiPartParser]
    

    def post(self, request):
        data = {}

        email = request.data.get('email')
        password = request.data.get('password')
        account = authenticate(email=email, password=password)

        if account:
            try:
                token = Token.objects.get(user=account).key
            except Token.DoesNotExist:
                create_token = Token.objects.create(user=account)
                token = create_token.key

            data['response'] = 'Successfully Authenticated'
            data['pk'] = account.pk
            data['email'] = email
            data['token'] = token
            status_code = status.HTTP_200_OK
        else:
            data['response'] = 'error'
            data['error_message'] = 'Invalid credentials'
            status_code = status.HTTP_400_BAD_REQUEST
        
        return Response(data=data, status=status_code)


@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@renderer_classes([JSONRenderer, BrowsableAPIRenderer])
def api_user_detail_view(request, username):
    try:
        user = User.objects.get(username=username)

        if request.user != user:
            raise PermissionDenied
        else:
            if request.method == 'GET':
                serializer = UserSerializer(user, context={'request': request})
                data = serializer.data
                return Response(data=data)
    except User.DoesNotExist:
        raise NotFound(detail='this user does not exist')



@api_view(['PUT', ])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser, MultiPartParser])
def api_update_user_detail_view(request, username):
    try:
        user = User.objects.get(username=username)
    
        if request.user != user:
             raise PermissionDenied
        else:
            if request.method == 'PUT':
                serializer = UserUpdateSerializer(user, data=request.data, partial=True)
                data = {}
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    data['success'] = 'update successful'
                    return Response(data=data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Profile.DoesNotExist:
        raise NotFound(detail='this user does not exist')
    

@api_view(['DELETE', ])
@permission_classes([IsAuthenticated])
def api_delete_user_view(request, username):
    try:
        user = User.objects.get(username=username)
   
        if request.user != user:
            raise PermissionDenied
        else:
            data = {}
            if request.method == 'DELETE':
                operation = user.delete()
                if operation:
                    data['success'] = 'delete successful'
                    status_code = status.HTTP_200_OK
                else:
                    data['error'] = 'failed to delete user'
                    status_code = status.HTTP_400_BAD_REQUEST
                
                return Response(data=data, status=status_code)
    except User.DoesNotExist:
        raise NotFound(detail='this user has already been deleted')
    

class ChangePasswordApiView(UpdateAPIView):
    authentication_classes = ([TokenAuthentication, ])
    permission_classes = ([IsAuthenticated, ])
    parser_classes = [JSONParser, MultiPartParser]
    serializer_class = ChangePasswordSerializer
    model = User


    def get_object(self, queryset=None):
        obj = self.request.user
        return obj 
 
    
    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)


        if serializer.is_valid(raise_exception=True):
            new_password = serializer.validated_data['password']
            confirm_password = serializer.validated_data['confirm_password']
            if not self.object.check_password(serializer.validated_data['old_password']):
                return Response({
                    'old_password': 'wrong password! please enter correct password'}, 
                    status=status.HTTP_400_BAD_REQUEST
                    )

            if confirm_password != new_password:
                return Response({
                    'confirm password': 'the passwords must match!'}, 
                    status=status.HTTP_400_BAD_REQUEST
                    )
            
            self.object.set_password(new_password)
            self.object.save()
            return Response({
                'password': 'password changed successfully!'}, 
                status=status.HTTP_200_OK
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', ])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer, BrowsableAPIRenderer])
def api_profile_view(request, slug):
    try:
        profile = Profile.objects.get(slug=slug)
    
        if request.method == 'GET': 
            if request.user.category == "DR" and request.user != profile.user:
                raise PermissionDenied
            else:
                serializer = ProfileSerializer(profile, context={'request': request})
                data = serializer.data
                if request.user != profile.user:
                    data.pop('meets')
                    data.pop('appointments_booked')

                return Response(data=data, status=status.HTTP_200_OK)
    except Profile.DoesNotExist:
        raise NotFound(detail='this profile does not exist')


@api_view(['PUT', ])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser, MultiPartParser])
def api_update_profile_view(request, slug):
    try:
        profile = Profile.objects.get(slug=slug)

    
        if request.user != profile.user:
            raise PermissionDenied
        else:
            if request.method == 'PUT':
                serializer = ProfileSerializer(profile, data=request.data, partial=True)
                data = {}
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    data['success'] = 'update successful'
                    return Response(data=data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Profile.DoesNotExist:
        raise NotFound(detail='this profile does not exist')


@api_view(['POST', ])
@permission_classes([IsAuthenticated, UserIsPatient])
@parser_classes([JSONParser, MultiPartParser])
def api_create_review_view(request, username):
    try:
        profile = Profile.objects.get(user__username=username, user__category='DR')
    
        if request.user not in profile.meets.all():
            raise PermissionDenied
        else:
            if request.method == 'POST':
                serializer = ReviewSerializer(data=request.data)
                if serializer.is_valid(raise_exception=True):
                    serializer.save(writer=request.user, doctor=profile)
                    update_rating(profile)
                    return Response(data=serializer.data, status=status.HTTP_201_CREATED)
                return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Profile.DoesNotExist:
        raise NotFound(detail='this doctor does not exist')
    

@api_view(['GET', ])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer, BrowsableAPIRenderer])
def api_review_detail_view(request, pk):
    try:
        review = DoctorReview.objects.get(id=pk)
    
        permission_class = ReviewDetailPerm()
        if not permission_class.has_object_permission(request, None, review):
            raise PermissionDenied
        else:
            if request.method == 'GET':
                serializer = ReviewSerializer(review)
                return Response(serializer.data)
    except DoctorReview.DoesNotExist:
        raise NotFound(detail='this review does not exist')


@api_view(['DELETE', ])
@permission_classes([IsAuthenticated])
def api_delete_review_view(request, pk):
    try:
        review = DoctorReview.objects.get(id=pk)
    
        user = request.user
        if review.writer != user:
            raise PermissionDenied
        else:   
            if request.method == 'DELETE':
                operation = review.delete()
                data = {}
                if operation:
                    data['success'] = 'delete successful'
                else:
                    data['failure'] = 'delete failed'
                return Response(data=data)
    except DoctorReview.DoesNotExist:
        raise NotFound(detail='this review does not exist')
    

@api_view(['GET', ])
@permission_classes([IsAuthenticated,  UserIsPatient])
@renderer_classes([JSONRenderer, BrowsableAPIRenderer])
def api_review_list_view(request, username):
    reviews = DoctorReview.objects.filter(doctor__user__username=username).order_by('-created_at')

    if request.method == 'GET':
        paginator_class = CustomPagination()
        queryset = paginator_class.paginate_queryset(reviews, request, None)
        serializer = ReviewSerializer(queryset,  many=True)
        return paginator_class.get_paginated_response(data=serializer.data)   
