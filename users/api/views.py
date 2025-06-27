from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import (
    api_view, 
    permission_classes, 
    parser_classes, 
    renderer_classes, 
    authentication_classes
)
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.core.cache import cache
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import UpdateAPIView
from rest_framework.exceptions import PermissionDenied, NotFound

from users.api.serializers import (
    UserSerializer, 
    UserUpdateSerializer,
    ProfileSerializer,
    ReviewSerializer, 
    ChangePasswordSerializer
)
from users.models import User, Profile, DoctorReview
from .core.utils import CustomPagination
from .core.custom_permissions import (
    UserIsDoctor,
    UserIsPatient,
    OTPVerifiedPermission,
    ReviewDetailPerm
)
from .core.tasks import update_rating
from .utils.password_utils import generate_otp


@api_view(['POST', ])
@permission_classes([])
@parser_classes([JSONParser, MultiPartParser])
def registration_view(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        data = {}
        serializer.is_valid(raise_exception=True)
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
        return Response(data, status=status.HTTP_201_CREATED)


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
            serializer = UserSerializer(user, context={'request': request})
            data = serializer.data
            return Response(data=data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        raise NotFound(detail='this user does not exist')


@api_view(['PATCH', ])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser, MultiPartParser])
def api_update_user_detail_view(request, username):
    try:
        user = User.objects.get(username=username)
    
        if request.user != user:
             raise PermissionDenied
        else:
            if request.method == 'PATCH':
                serializer = UserUpdateSerializer(user, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                instance = serializer.save()
                serializer = UserSerializer(instance, context={'request': request})
                data = {
                    "success": "update successful",
                    "details": serializer.data
                }
                return Response(data=data, status=status.HTTP_200_OK)
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


@api_view(['GET', ])
@authentication_classes([])
@permission_classes([])
@renderer_classes([JSONRenderer, BrowsableAPIRenderer])
def api_request_otp_view(request):
    user_email = request.query_params.get('email')
    try:
        user = User.objects.get(email=user_email)
        generate_otp(user_email)
        return Response(data={'message':'the otp has been sent to your email'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        raise NotFound(detail='invalid credentials')


@api_view(['GET', ])
@authentication_classes([])
@permission_classes([])
@renderer_classes([JSONRenderer, BrowsableAPIRenderer])
def api_verify_otp_view(request):
    email = request.query_params.get('email')
    user_otp = request.query_params.get('otp')
    saved_otp = cache.get(f'{email}_otp')

    if not saved_otp:
        return Response(data={'error': 'otp has expired'}, status=status.HTTP_400_BAD_REQUEST)
    elif int(user_otp) != saved_otp:
        return Response(data={'error': 'invalid otp'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        cache.delete(f"{email}_otp")
        cache.set(f"otp_verified_{email}", True, timeout=600)
        return Response(data={"message": "OTP verified"}, status=status.HTTP_200_OK)



class ChangePasswordApiView(UpdateAPIView):
    authentication_classes = ([])
    permission_classes = ([OTPVerifiedPermission, ])
    parser_classes = [JSONParser, MultiPartParser]
    serializer_class = ChangePasswordSerializer
    model = User

    def get_object(self, queryset=None): 
        email = self.request.query_params.get('email')
        if not email:
            raise NotFound(detail='email not provided')
        else:
            try:
                obj = User.objects.get(email=email)
                return obj 
            except User.DoesNotExist:
                raise NotFound(detail='this user does not exist')

 
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        new_password = serializer.validated_data['new_password']
        confirm_password = serializer.validated_data['confirm_password']

        if confirm_password != new_password:
            return Response({
                'confirm password': 'the passwords must match!'}, 
                status=status.HTTP_400_BAD_REQUEST
                )
        
        user.set_password(new_password)
        user.save()
        return Response({
            'password': 'password changed successfully!'}, 
            status=status.HTTP_200_OK
            )


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
                if request.user.category == 'PT':
                    data.pop('meets_booked_for')
                    data.pop('appointments_booked')

                return Response(data=data, status=status.HTTP_200_OK)
    except Profile.DoesNotExist:
        raise NotFound(detail='this profile does not exist')


@api_view(['PATCH', ])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser, MultiPartParser])
def api_update_profile_view(request, slug):
    try:
        profile = Profile.objects.get(slug=slug)

    
        if request.user != profile.user:
            raise PermissionDenied
        else:
            if request.method == 'PATCH':
                serializer = ProfileSerializer(profile, data=request.data, partial=True)
                
                serializer.is_valid(raise_exception=True)
                instance = serializer.save()
                serializer = ProfileSerializer(instance, context={'request': request})
                data = {
                    "success": "update successful",
                    "details": serializer.data
                }
                return Response(data=data, status=status.HTTP_200_OK)
    except Profile.DoesNotExist:
        raise NotFound(detail='this profile does not exist')


@api_view(['POST', ])
@permission_classes([IsAuthenticated, UserIsPatient])
@parser_classes([JSONParser, MultiPartParser])
def api_create_review_view(request, username):
    try:
        profile = Profile.objects.get(user__username=username, user__category='DR')
    
        meet_list =  profile.meets_booked_for.filter(patient=request.user)
        if not meet_list.exists():
            raise PermissionDenied
        else:
            if request.method == 'POST':
                serializer = ReviewSerializer(data=request.data, context={'request': request})
                serializer.is_valid(raise_exception=True)
                serializer.save(writer=request.user, doctor=profile)
                update_rating.delay_on_commit(profile.id)
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)
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
