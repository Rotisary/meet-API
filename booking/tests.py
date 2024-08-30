from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from .models import Illness
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model


class CustomTestCase(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(email='oladotunkolapo@gmail.com',
                                             username='Roti',
                                             password='Roti1805',
                                             first_name='Oladotun',
                                             last_name='Kolapo',
                                             category='PT',
                                            )
    def test_create_illness(self):
        token = Token.objects.get(user__username='Roti')
        url = reverse('illness-create')
        data = {'body_part': 'BN', 'age': '27'}
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Illness.objects.get().id, 1)