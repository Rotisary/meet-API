from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes, renderer_classes
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import UpdateAPIView, ListAPIView
from rest_framework.exceptions import APIException, PermissionDenied, NotFound

from users.api.serializers import (
    UserSerializer, 
    UserUpdateSerializer,
    ProfileSerializer,
    ReviewSerializer, 
    ChangePasswordSerializer
)
from users.models import User, Profile, DoctorReview
from booking.api.custom_permissions import UserIsDoctor, UserIsPatient, ReviewDetailPerm


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
    

class ObtainAuthTokenView(APIView):
    authentication_classes = []
    permission_classes = []
    parser_classes = [JSONParser, MultiPartParser]
    

    def post(self, request):
        context = {}

        email = request.POST.get('username')
        password = request.POST.get('password')
        account = authenticate(email=email, password=password)

        if account:
            try:
                token = Token.objects.get(user=account).key
            except Token.DoesNotExist:
                create_token = Token.objects.create(user=account)
                token = create_token.key

            context['response'] = 'Successfully Authenticated'
            context['pk'] = account.pk
            context['email'] = email
            context['token'] = token
        else:
            context['response'] = 'error'
            context['error_message'] = 'Invalid credentials'
        
        return Response(context)


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
                return Response({'old_password': 'wrong password! please enter correct password'}, status=status.HTTP_400_BAD_REQUEST)

            if confirm_password != new_password:
                return Response({'confirm password': 'the passwords must match!'}, status=status.HTTP_400_BAD_REQUEST)
            
            self.object.set_password(new_password)
            self.object.save()
            return Response({'password': 'password changed successfully!'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
# needs a lil' change
@api_view(['GET', ])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer, BrowsableAPIRenderer])
def api_profile_view(request, username):
    try:
        profile = Profile.objects.get(user__username=username)
    
        if request.user != profile.user:
            raise PermissionDenied
        else:
            data = {}
            if request.method == 'GET':

                reviews = profile.reviews.all()
                no_of_reviews = reviews.count()
                sum_of_stars = 0
                for review in reviews:
                    sum_of_stars += review.stars

                try:
                    rating = sum_of_stars/no_of_reviews
                except ZeroDivisionError:
                    serializer = ProfileSerializer(profile, context={'request': request})
                    data['details'] = serializer.data
                    data['rating'] = "you don't have a rating yet"
                else: 
                    serializer = ProfileSerializer(profile, context={'request': request})
                    data['details'] = serializer.data
                    data['rating'] = rating
                return Response(data=data)
    except Profile.DoesNotExist:
        raise NotFound(detail='this profile does not exist')


@api_view(['PUT', ])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser, MultiPartParser])
def api_update_profile_view(request, username):
    try:
        profile = Profile.objects.get(user__username=username)

    
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
    
        if request.user not in profile.meet.all():
            raise PermissionDenied
        else:
            if request.method == 'POST':
                serializer = ReviewSerializer(data=request.data)
                if serializer.is_valid(raise_exception=True):
                    serializer.save(writer=request.user, doctor=profile)
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
                serializer = ReviewSerializer(review, context={'request': request})
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
@permission_classes([IsAuthenticated, UserIsPatient])
@renderer_classes([JSONRenderer, BrowsableAPIRenderer])
def api_review_list_view(request, username):
    reviews = DoctorReview.objects.filter(doctor__user__username=username)

    if request.method == 'GET':
        serializer = ReviewSerializer(reviews,  many=True, context={'request': request})
        return Response(serializer.data)