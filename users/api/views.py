from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login
from rest_framework.decorators import permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import UpdateAPIView

from users.api.serializers import RegistrationSerializer, ChangePasswordSerializer
from users.models import User


@api_view(['POST', ])
@permission_classes([])
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

    

class ChangePasswordApiView(UpdateAPIView):
    authentication_classes = ([TokenAuthentication, ])
    permission_classes = ([IsAuthenticated, ])
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
                 