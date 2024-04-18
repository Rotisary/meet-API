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
    ChangePasswordSerializer
)
from users.models import User, Profile
from users.permissions import UserNotOwner


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
    

class ListUserApiView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination


@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
@renderer_classes([JSONRenderer, BrowsableAPIRenderer])
def api_user_detail_view(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = UserSerializer(user, context={'request': request})
        return Response(data=serializer.data)


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
        if request.method == 'GET':
            serializer = ProfileSerializer(profile, context={'request': request})
            return Response(data=serializer.data)


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
                 