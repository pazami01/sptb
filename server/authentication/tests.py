import json

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


USER_MODEL = get_user_model()
PASS = 'password123!'


def create_user(username, email, first_name, last_name, password):
    try:
        user = USER_MODEL.objects.create_user(username, email, first_name, last_name, password)
    except IntegrityError:
        user = USER_MODEL.objects.get(username=username)
    
    return user


class AuthenticationTest(APITestCase):
    def setUp(self):
        self.user = create_user(
            username = 'johndoe',
            email = 'johndoe@fakeuniversity.com',
            first_name = 'John',
            last_name = 'Doe',
            password = PASS,
        )

    def test_authenticate_user(self):
        url = reverse('token_obtain_pair')
        data = {
            'username': self.user.username,
            'password': PASS,
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data['access'])
        self.assertIsNotNone(response.data['refresh'])