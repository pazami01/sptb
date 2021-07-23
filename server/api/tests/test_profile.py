import json

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from ..serializers import AccountSerializer

USER_MODEL = get_user_model()
PASS = 'password123!'

def create_user(username, email, first_name, last_name, password):
    try:
        user = USER_MODEL.objects.create_user(username, email, first_name, last_name, password)
    except IntegrityError:
        user = USER_MODEL.objects.get(username=username)
    
    return user


class AccountListViewTest(APITestCase):
    # this setup is re-run before each test
    def setUp(self):
        create_user(
            username = 'janedoe',
            email = 'janedoe@fakeuniversity.com',
            first_name = 'Jane',
            last_name = 'Doe',
            password = PASS,
        )
        create_user(
            username = 'jeffdoe',
            email = 'jeffdoe@fakeuniversity.com',
            first_name = 'Jeff',
            last_name = 'Doe',
            password = PASS,
        )
        # create user to be used for making requests
        self.user = create_user(
            username = 'johndoe',
            email = 'johndoe@fakeuniversity.com',
            first_name = 'John',
            last_name = 'Doe',
            password = PASS,
        )

        # prepare data for login
        url = reverse('token_obtain_pair')
        data = {
            'username': self.user.username,
            'password': PASS,
        }
        # log in user
        response = self.client.post(url, data, format='json')

        # add access token to auth header
        self.client.credentials(HTTP_AUTHORIZATION = 'Bearer ' + response.data['access'])

    def test_get_account_list_unauthenticated(self):
        # forcefully unauthenticate the requesting user
        self.client.force_authenticate(user=None)

        url = reverse('account-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_account_list(self):
        # get all users from the database
        accounts = USER_MODEL.objects.all()
        # serialize the accounts data
        accounts_data = AccountSerializer(accounts, many=True).data

        url = reverse('account-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, accounts_data)

    def test_get_account_list_with_search_query(self):
        # update user profile with new roles
        new_data = {
            'profile': {
                'programme': 'New Programme',
                'about': 'New about text.',
                'roles': [
                    'Software Engineer',
                    'Project Manager'
                ]
            }
        }

        url = reverse('account-detail', kwargs={'pk': self.user.pk})
        self.client.patch(url, new_data, format='json')

        # get a list of accounts that have an 'engineer' substring in their roles
        url = f'{reverse("account-list")}?search=engineer'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], self.user.username)

    
class AccountDetailViewTest(APITestCase):
    # this setup is re-run before each test
    def setUp(self):
        # create an extra user for testing authorization
        self.other_user = create_user(
            username = 'jeffdoe',
            email = 'jeffdoe@fakeuniversity.com',
            first_name = 'Jeff',
            last_name = 'Doe',
            password = PASS,
        )
        # create user to be used for making requests
        self.user = create_user(
            username = 'johndoe',
            email = 'johndoe@fakeuniversity.com',
            first_name = 'John',
            last_name = 'Doe',
            password = PASS,
        )

        # prepare data for login
        url = reverse('token_obtain_pair')
        data = {
            'username': self.user.username,
            'password': PASS,
        }
        # log in user
        response = self.client.post(url, data, format='json')

        # add access token to auth header
        self.client.credentials(HTTP_AUTHORIZATION = 'Bearer ' + response.data['access'])

    def test_get_account_detail_unauthenticated(self):
        # forcefully unauthenticate the user
        self.client.force_authenticate(user=None)

        url = reverse('account-detail', kwargs={'pk': self.user.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_account_detail_with_invalid_pk(self):
        INVALID_PK = 2500
        url = reverse('account-detail', kwargs={'pk': INVALID_PK})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_account_detail_with_authenticated_user_pk(self):
        user_data = AccountSerializer(self.user).data

        url = reverse('account-detail', kwargs={'pk': self.user.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, user_data)

    def test_get_account_detail_with_other_user_pk(self):
        other_user_data = AccountSerializer(self.other_user).data

        url = reverse('account-detail', kwargs={'pk': self.other_user.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, other_user_data)

    def test_update_account_detail_unauthenticated(self):
        # forcefully unauthenticate the user
        self.client.force_authenticate(user=None)

        new_data = {
            'profile': {
                'programme': 'New Programme'
            }
        }

        url = reverse('account-detail', kwargs={'pk': self.user.pk})
        response = self.client.get(url, new_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_account_detail_unauthorized(self):
        other_user_data_before_update = AccountSerializer(self.other_user).data

        new_data = {
            'profile': {
                'programme': 'New Programme'
            }
        }

        url = reverse('account-detail', kwargs={'pk': self.other_user.pk})
        response = self.client.patch(url, new_data, format='json')

        # fetch the other user from the database after the update
        other_user_after_update = USER_MODEL.objects.get(pk=self.other_user.pk)
        other_user_data_after_update = AccountSerializer(other_user_after_update).data

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(other_user_data_after_update, other_user_data_before_update)

    def test_update_account_detail_with_invalid_data(self):
        user_data_before_update = AccountSerializer(self.user).data

        new_data = {
            'profile': {
                'programme': 'New Programme',
                'about': 'New about text.',
                'roles': [
                    'New Role 1',
                    'New Role 2',
                    'New Role 3',
                    'New Role 4'  # invalid value - should be a maximum of 3 roles
                ]
            }
        }

        url = reverse('account-detail', kwargs={'pk': self.user.pk})
        response = self.client.patch(url, new_data, format='json')

        # fetch the user from the database after the update
        user_after_update = USER_MODEL.objects.get(pk=self.user.pk)
        user_data_after_update = AccountSerializer(user_after_update).data

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(user_data_after_update, user_data_before_update)

    def test_update_account_detail_with_valid_data(self):
        user_data_before_update = AccountSerializer(self.user).data

        new_data = {
            'profile': {
                'programme': 'New Programme',
                'about': 'New about text.',
                'roles': [
                    'New Role 1',
                    'New Role 2'
                ]
            }
        }

        url = reverse('account-detail', kwargs={'pk': self.user.pk})
        response = self.client.patch(url, new_data, format='json')

        # fetch the user from the database after the update
        user_after_update = USER_MODEL.objects.get(pk=self.user.pk)
        user_data_after_update = AccountSerializer(user_after_update).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, user_data_after_update)
        self.assertNotEqual(user_data_after_update, user_data_before_update)

