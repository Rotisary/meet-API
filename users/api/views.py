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

from users.api.serializers import (
    RegistrationSerializer, 
    UserSerializer, 
    UserUpdateSerializer,
    ProfileSerializer,
    ReviewSerializer, 
    ChangePasswordSerializer
)
from users.models import User, Profile, DoctorReview
from booking.api.custom_permissions import UserIsDoctor, UserIsPatient


@api_view(['POST', ])
@permission_classes([])
@parser_classes([JSONParser, MultiPartParser])
def registration_view(request):
    if request.method == 'POST':
        serializer = RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
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
    parser_classes = [JSONParser, ]
    

    def post(self, request):
        context = {}

        email = request.POST.get('username').lower()
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
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    meets = user.meets.all()
    meets_list = []
    for meet in meets:
        meet_username = meet.user.username
        meets_list.append(meet_username)

    if request.user != user or request.user.profile not in user.meets.all():
        return Response({'error': 'permission denied'}, status=status.HTTP_403_FORBIDDEN)
    else:
        data = {}
        if request.method == 'GET':
            serializer = UserSerializer(user, context={'request': request})
            data['details'] = serializer.data
            data['meets'] = meets_list
            return Response(data=data)


@api_view(['PUT', ])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser, MultiPartParser])
def api_update_user_detail_view(request, username):
    try:
        user = User.objects.get(username=username)
    except Profile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.user.username != user.username or request.user.category == 'DR':
        return Response({'permission': 'you are not authorized to update this profile'}, status=status.HTTP_403_FORBIDDEN)
    else:
        if request.method == 'PUT':
            serializer = UserUpdateSerializer(user, data=request.data, partial=True)
            data = {}
            if serializer.is_valid():
                serializer.save()
                data['success'] = 'update successful'
                return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

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


        if serializer.is_valid():
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
        

@api_view(['GET', ])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer, BrowsableAPIRenderer])
def api_profile_view(request, username):
    try:
        profile = Profile.objects.get(user__username=username)
    except Profile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.user != profile.user:
        return Response({'permission': 'you are not authorized to view this profile'}, status=status.HTTP_403_FORBIDDEN)
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


@api_view(['PUT', ])
@permission_classes([IsAuthenticated])
@parser_classes([JSONParser, MultiPartParser])
def api_update_profile_view(request, username):
    try:
        profile = Profile.objects.get(user__username=username)
    except Profile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.user != profile.user:
        return Response({'permission': 'you are not authorized to update this profile'}, status=status.HTTP_403_FORBIDDEN)
    else:
        if request.method == 'PUT':
            serializer = ProfileSerializer(profile, data=request.data, partial=True)
            data = {}
            if serializer.is_valid():
                serializer.save()
                data['success'] = 'update successful'
                return Response(data=data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', ])
@permission_classes([IsAuthenticated, UserIsDoctor])
@parser_classes([JSONParser, MultiPartParser])
def api_create_review_view(request, username):
    try:
        profile = Profile.objects.get(user__username=username, user__category='DR')
    except Profile.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.user not in profile.meet.all():
        return Response({'error': 'permission denied'}, status=status.HTTP_403_FORBIDDEN)
    else:
        if request.method == 'POST':
            serializer = ReviewSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(writer=request.user, doctor=profile)
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET', ])
@permission_classes([IsAuthenticated])
@renderer_classes([JSONRenderer, BrowsableAPIRenderer])
def api_review_detail_view(request, pk):
    try:
        review = DoctorReview.objects.get(id=pk)
    except DoctorReview.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    user = request.user
    if user.category == 'DR' and user != review.doctor.user:
        return Response({'response': 'you are not allowed to view this page'},
                        status=status.HTTP_403_FORBIDDEN)
    else:
        if request.method == 'GET':
            serializer = ReviewSerializer(review, context={'request': request})
            return Response(serializer.data)
    

@api_view(['DELETE', ])
@permission_classes([IsAuthenticated])
def api_delete_review_view(request, pk):
    try:
        review = DoctorReview.objects.get(id=pk)
    except DoctorReview.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    user = request.user
    if review.writer != user:
        return Response({'response': 'you are not allowed to delete that!'}, status=status.HTTP_403_FORBIDDEN)
    else:   
        if request.method == 'DELETE':
            operation = review.delete()
            data = {}
            if operation:
                data['success'] = 'delete successful'
            else:
                data['failure'] = 'delete failed'
            return Response(data=data)
    


@api_view(['GET', ])
@permission_classes([IsAuthenticated, UserIsDoctor])
@renderer_classes([JSONRenderer, BrowsableAPIRenderer])
def api_review_list_view(request, username):
    reviews = DoctorReview.objects.filter(doctor__user__username=username)

    if request.method == 'GET':
        serializer = ReviewSerializer(reviews,  many=True, context={'request': request})
        return Response(serializer.data)