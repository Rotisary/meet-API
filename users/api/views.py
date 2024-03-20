from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login

from users.api.serializers import RegistrationSerializer


@api_view(['POST', ])
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

        

        