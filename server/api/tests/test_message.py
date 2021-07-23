import json

from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from ..models import Project, Membership, PrivateMessage, PublicMessage
from ..serializers import ProjectSerializer, PrivateMessageSerializer, PublicMessageSerializer

USER_MODEL = get_user_model()
PASS = 'password123!'

def create_user(username, email, first_name, last_name, password):
    try:
        user = USER_MODEL.objects.create_user(username, email, first_name, last_name, password)
    except IntegrityError:
        user = USER_MODEL.objects.get(username=username)
    
    return user


class PrivateMessageListViewTest(APITestCase):
    # this setup is re-run before each test
    def setUp(self):
        # create the user to be authenticated and make calls to endpoints
        self.user = create_user(
            username = 'johndoe',
            email = 'johndoe@fakeuniversity.com',
            first_name = 'John',
            last_name = 'Doe',
            password = PASS,
        )
        # create another test user
        self.other_user = create_user(
            username = 'jeffdoe',
            email = 'jeffdoe@fakeuniversity.com',
            first_name = 'Jeff',
            last_name = 'Doe',
            password = PASS,
        )
        # create a project with the authenticated user as the owner
        self.test_project_one = Project.objects.create(
            title = 'Test Project 1',
            description = 'Test project 1 description.',
            category = 'ART',
            owner = self.user,
            owner_role = 'Test Owner Role',
            desired_roles = [
                'Software Engineer',
                'Data Analyst'
            ]
        )
        # create a project with the other test user as the owner
        self.test_project_two = Project.objects.create(
            title = 'Test Project 2',
            description = 'Test project 2 description.',
            category = 'ART',
            owner = self.other_user,
            owner_role = 'Test Owner Role',
            desired_roles = [
                'Director',
                'Actor'
            ]
        )
        # create a project with the other test user as the owner and the authenticated user as a member
        self.test_project_three = Project.objects.create(
            title = 'Test Project 3',
            description = 'Test project 3 description.',
            category = 'ART',
            owner = self.other_user,
            owner_role = 'Test Owner Role',
            desired_roles = [
                'Director',
                'Actor'
            ]
        )

        # create a memebership to make authenticated user a member of test_project_three
        self.test_project_three_membership_one = Membership.objects.create(
            role = 'Test Role',
            project = self.test_project_three,
            user = self.user
        )

        # create a private message for test_project_one by the project owner
        self.test_project_one_private_message_one = PrivateMessage.objects.create(
            user = self.user,
            project = self.test_project_one,
            message = 'Test message 1',
        )

        # create a private message for test_project_two by the project owner
        self.test_project_two_private_message_one = PrivateMessage.objects.create(
            user = self.other_user,
            project = self.test_project_two,
            message = 'Test message 1',
        )

        # create a private message for test_project_three by the project owner
        self.test_project_three_private_message_one = PrivateMessage.objects.create(
            user = self.other_user,
            project = self.test_project_three,
            message = 'Test message 1',
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
    
    def test_get_private_message_list_unauthenticated(self):
        # forcefully unauthenticate the requesting user
        self.client.force_authenticate(user=None)

        # attempt to fetch private messages for test_project_one
        url = reverse('project-private-messages-list', kwargs={'project_pk': self.test_project_one.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_private_message_list_unauthorized(self):
        # attempt to fetch private messages for a project the authenticated user is not a member or owner of
        url = reverse('project-private-messages-list', kwargs={'project_pk': self.test_project_two.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_private_message_list_with_invalid_project_pk(self):
        INVALID_PK = 2500
        
        # attempt to fetch private messages for a project that doesn't exist
        url = reverse('project-private-messages-list', kwargs={'project_pk': INVALID_PK})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_private_message_list_with_valid_project_pk_as_owner(self):
        # fetch the private messages for test_project_one from the database
        test_project_one_private_message = PrivateMessage.objects.filter(project=self.test_project_one)
        # serialize the private message and store the data
        test_project_one_private_message_data = PrivateMessageSerializer(test_project_one_private_message, many=True).data

        # attempt to fetch private messages for test_project_one, which auth user is the owner of
        url = reverse('project-private-messages-list', kwargs={'project_pk': self.test_project_one.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # data sent in the response should match the data stored in the database
        self.assertEqual(response.data, test_project_one_private_message_data)

    def test_get_private_message_list_with_valid_project_pk_as_member(self):
        # fetch the private messages for test_project_three from the database
        test_project_three_private_message = PrivateMessage.objects.filter(project=self.test_project_three)
        # serialize the private message and store the data
        test_project_three_private_message_data = PrivateMessageSerializer(test_project_three_private_message, many=True).data

        # attempt to fetch private messages for test_project_three, which auth user is a member of
        url = reverse('project-private-messages-list', kwargs={'project_pk': self.test_project_three.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # data sent in the response should match the data stored in the database
        self.assertEqual(response.data, test_project_three_private_message_data)

    def test_create_private_message_unauthenticated(self):
        # forcefully unauthenticate the requesting user
        self.client.force_authenticate(user=None)

        # initial private message count in the database for test_project_one
        initial_test_project_one_private_message_count = PrivateMessage.objects.filter(project=self.test_project_one).count()

        message_data = {
            'message': 'This is a test message'
        }

        # attempt to create a private message for test_project_one, which the auth user is the owner of
        url = reverse('project-private-messages-list', kwargs={'project_pk': self.test_project_one.pk})
        response = self.client.post(url, message_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # no new message should have been added
        self.assertEqual(
            PrivateMessage.objects.filter(project=self.test_project_one).count(),
            initial_test_project_one_private_message_count
        )

    def test_create_private_message_unauthorized(self):
        # initial private message count in the database for test_project_two
        initial_test_project_two_private_message_count = PrivateMessage.objects.filter(project=self.test_project_two).count()

        message_data = {
            'message': 'This is a test message'
        }

        # attempt to create a private message for test_project_two, which the auth user is NOT a member or owner of
        url = reverse('project-private-messages-list', kwargs={'project_pk': self.test_project_two.pk})
        response = self.client.post(url, message_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # no new message should have been added
        self.assertEqual(
            PrivateMessage.objects.filter(project=self.test_project_two).count(),
            initial_test_project_two_private_message_count
        )

    def test_create_private_message_with_invalid_project_pk(self):
        INVALID_PK = 2500

        message_data = {
            'message': 'This is a test message'
        }

        # attempt to create a private message for a project that doesn't exist
        url = reverse('project-private-messages-list', kwargs={'project_pk': INVALID_PK})
        response = self.client.post(url, message_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_private_message_with_valid_project_pk_as_owner(self):
        # initial private message count in the database for test_project_one
        initial_test_project_one_private_message_count = PrivateMessage.objects.filter(project=self.test_project_one).count()

        message_data = {
            'message': 'This is a test message'
        }

        # attempt to create a private message for test_project_one, which the auth user is the owner of
        url = reverse('project-private-messages-list', kwargs={'project_pk': self.test_project_one.pk})
        response = self.client.post(url, message_data, format='json')

        # make sure the private message was created in the database
        try:
            new_private_message = PrivateMessage.objects.get(pk=response.data['id'])
        except PrivateMessage.DoesNotExist:
            self.fail('Message was not created')
        
        # serialize the private message
        new_private_message = PrivateMessageSerializer(new_private_message).data

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # private message count should have increased by 1
        self.assertEqual(
            PrivateMessage.objects.filter(project=self.test_project_one).count(),
            initial_test_project_one_private_message_count + 1
        )
        # check the returned data is equal to what is saved in the database
        self.assertEqual(response.data, new_private_message)
        # check the returned data equals the data given to create the message
        self.assertEqual(response.data['message'], new_private_message['message'])

    def test_create_private_message_with_valid_project_pk_as_member(self):
        # initial private message count in the database for test_project_three
        initial_test_project_three_private_message_count = PrivateMessage.objects.filter(project=self.test_project_three).count()

        message_data = {
            'message': 'This is a test message'
        }

        # attempt to create a private message for test_project_three, which the auth user is a member of
        url = reverse('project-private-messages-list', kwargs={'project_pk': self.test_project_three.pk})
        response = self.client.post(url, message_data, format='json')

        # make sure the private message was created in the database
        try:
            new_private_message = PrivateMessage.objects.get(pk=response.data['id'])
        except PrivateMessage.DoesNotExist:
            self.fail('Message was not created')
        
        # serialize the private message
        new_private_message = PrivateMessageSerializer(new_private_message).data

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # private message count should have increased by 1
        self.assertEqual(
            PrivateMessage.objects.filter(project=self.test_project_three).count(),
            initial_test_project_three_private_message_count + 1
        )
        # check the returned data is equal to what is saved in the database
        self.assertEqual(response.data, new_private_message)
        # check the returned data equals the data given to create the message
        self.assertEqual(response.data['message'], new_private_message['message'])

class PrivateMessageDetailViewTest(APITestCase):
    # this setup is re-run before each test
    def setUp(self):
        # create the user to be authenticated and make calls to endpoints
        self.user = create_user(
            username = 'johndoe',
            email = 'johndoe@fakeuniversity.com',
            first_name = 'John',
            last_name = 'Doe',
            password = PASS,
        )
        # create another test user
        self.other_user = create_user(
            username = 'jeffdoe',
            email = 'jeffdoe@fakeuniversity.com',
            first_name = 'Jeff',
            last_name = 'Doe',
            password = PASS,
        )
        # create a project with the authenticated user as the owner
        self.test_project_one = Project.objects.create(
            title = 'Test Project 1',
            description = 'Test project 1 description.',
            category = 'ART',
            owner = self.user,
            owner_role = 'Test Owner Role',
            desired_roles = [
                'Software Engineer',
                'Data Analyst'
            ]
        )
        # create a project with the other test user as the owner
        self.test_project_two = Project.objects.create(
            title = 'Test Project 2',
            description = 'Test project 2 description.',
            category = 'ART',
            owner = self.other_user,
            owner_role = 'Test Owner Role',
            desired_roles = [
                'Director',
                'Actor'
            ]
        )
        # create a project with the other test user as the owner and the authenticated user as a member
        self.test_project_three = Project.objects.create(
            title = 'Test Project 3',
            description = 'Test project 3 description.',
            category = 'ART',
            owner = self.other_user,
            owner_role = 'Test Owner Role',
            desired_roles = [
                'Director',
                'Actor'
            ]
        )

        # create a memebership to make authenticated user a member of test_project_three
        self.test_project_three_membership_one = Membership.objects.create(
            role = 'Test Role',
            project = self.test_project_three,
            user = self.user
        )

        # create a private message for test_project_one by the project owner
        self.test_project_one_private_message_one = PrivateMessage.objects.create(
            user = self.user,
            project = self.test_project_one,
            message = 'Test message 1',
        )

        # create a private message for test_project_two by the project owner
        self.test_project_two_private_message_one = PrivateMessage.objects.create(
            user = self.other_user,
            project = self.test_project_two,
            message = 'Test message 1',
        )

        # create a private message for test_project_three by the project owner
        self.test_project_three_private_message_one = PrivateMessage.objects.create(
            user = self.other_user,
            project = self.test_project_three,
            message = 'Test message 1',
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
    
    def test_get_private_message_detail_unauthenticated(self):
        # forcefully unauthenticate the requesting user
        self.client.force_authenticate(user=None)

        # attempt to fetch a private message for test_project_one, which the auth user is the owner of
        url = reverse(
            'project-private-messages-detail',
            kwargs={
                'project_pk': self.test_project_one.pk,
                'message_pk': self.test_project_one_private_message_one.pk
            }
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_private_message_detail_unauthorized(self):
        # attempt to fetch a private message for test_project_two,
        # which the auth user is NOT a member or owner of
        url = reverse(
            'project-private-messages-detail',
            kwargs={
                'project_pk': self.test_project_two.pk,
                'message_pk': self.test_project_two_private_message_one.pk
            }
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_private_message_detail_with_invalid_project_pk(self):
        INVALID_PK = 2500

        # attempt to fetch a private message for a project that doesn't exist
        url = reverse(
            'project-private-messages-detail',
            kwargs={
                'project_pk': INVALID_PK,
                'message_pk': INVALID_PK
            }
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_private_message_detail_with_invalid_message_pk(self):
        INVALID_PK = 2500

        # attempt to fetch a private message that doesn't exist
        # for test_project_one, which the auth user is the owner of
        url = reverse(
            'project-private-messages-detail',
            kwargs={
                'project_pk': self.test_project_one.pk,
                'message_pk': INVALID_PK
            }
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_private_message_detail_with_valid_project_pk_and_message_pk_as_owner(self):
        # serialize the private message and store the data
        test_project_one_private_message_one_data = PrivateMessageSerializer(self.test_project_one_private_message_one).data


        # attempt to fetch a private message for test_project_one, 
        # which the auth user is the owner of
        url = reverse(
            'project-private-messages-detail',
            kwargs={
                'project_pk': self.test_project_one.pk,
                'message_pk': self.test_project_one_private_message_one.pk
            }
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # data sent in the response should match the data stored in the database
        self.assertEqual(response.data, test_project_one_private_message_one_data)

    def test_get_private_message_detail_with_valid_project_pk_and_message_pk_as_member(self):
        # serialize the private message and store the data
        test_project_three_private_message_one_data = PrivateMessageSerializer(self.test_project_three_private_message_one).data


        # attempt to fetch a private message for test_project_three, 
        # which the auth user is a member of
        url = reverse(
            'project-private-messages-detail',
            kwargs={
                'project_pk': self.test_project_three.pk,
                'message_pk': self.test_project_three_private_message_one.pk
            }
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # data sent in the response should match the data stored in the database
        self.assertEqual(response.data, test_project_three_private_message_one_data)
    
class PublicMessageListViewTest(APITestCase):
    # this setup is re-run before each test
    def setUp(self):
        # create the user to be authenticated and make calls to endpoints
        self.user = create_user(
            username = 'johndoe',
            email = 'johndoe@fakeuniversity.com',
            first_name = 'John',
            last_name = 'Doe',
            password = PASS,
        )
        # create another test user
        self.other_user = create_user(
            username = 'jeffdoe',
            email = 'jeffdoe@fakeuniversity.com',
            first_name = 'Jeff',
            last_name = 'Doe',
            password = PASS,
        )
        # create a project with the authenticated user as the owner
        self.test_project_one = Project.objects.create(
            title = 'Test Project 1',
            description = 'Test project 1 description.',
            category = 'ART',
            owner = self.user,
            owner_role = 'Test Owner Role',
            desired_roles = [
                'Software Engineer',
                'Data Analyst'
            ]
        )
        # create a project with the other test user as the owner
        self.test_project_two = Project.objects.create(
            title = 'Test Project 2',
            description = 'Test project 2 description.',
            category = 'ART',
            owner = self.other_user,
            owner_role = 'Test Owner Role',
            desired_roles = [
                'Director',
                'Actor'
            ]
        )
        # create a project with the other test user as the owner and the authenticated user as a member
        self.test_project_three = Project.objects.create(
            title = 'Test Project 3',
            description = 'Test project 3 description.',
            category = 'ART',
            owner = self.other_user,
            owner_role = 'Test Owner Role',
            desired_roles = [
                'Director',
                'Actor'
            ]
        )

        # create a memebership to make authenticated user a member of test_project_three
        self.test_project_three_membership_one = Membership.objects.create(
            role = 'Test Role',
            project = self.test_project_three,
            user = self.user
        )

        # create a public message for test_project_one by the project owner
        self.test_project_one_public_message_one = PublicMessage.objects.create(
            user = self.user,
            project = self.test_project_one,
            message = 'Test message 1',
        )

        # create a public message for test_project_two by the project owner
        self.test_project_two_public_message_one = PublicMessage.objects.create(
            user = self.other_user,
            project = self.test_project_two,
            message = 'Test message 1',
        )

        # create a public message for test_project_three by the project owner
        self.test_project_three_public_message_one = PublicMessage.objects.create(
            user = self.other_user,
            project = self.test_project_three,
            message = 'Test message 1',
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
    
    def test_get_public_message_list_unauthenticated(self):
        # forcefully unauthenticate the requesting user
        self.client.force_authenticate(user=None)

        # attempt to fetch public messages for test_project_one
        url = reverse('project-public-messages-list', kwargs={'project_pk': self.test_project_one.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_public_message_list_with_invalid_project_pk(self):
        INVALID_PK = 2500
        
        # attempt to fetch public messages for a project that doesn't exist
        url = reverse('project-public-messages-list', kwargs={'project_pk': INVALID_PK})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_public_message_list_with_valid_project_pk_as_owner(self):
        # fetch the public messages for test_project_one from the database
        test_project_one_public_message = PublicMessage.objects.filter(project=self.test_project_one)
        # serialize the public message and store the data
        test_project_one_public_message_data = PublicMessageSerializer(test_project_one_public_message, many=True).data

        # attempt to fetch public messages for test_project_one, which auth user is the owner of
        url = reverse('project-public-messages-list', kwargs={'project_pk': self.test_project_one.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # data sent in the response should match the data stored in the database
        self.assertEqual(response.data, test_project_one_public_message_data)

    def test_get_public_message_list_with_valid_project_pk_as_member(self):
        # fetch the public messages for test_project_three from the database
        test_project_three_public_message = PublicMessage.objects.filter(project=self.test_project_three)
        # serialize the public message and store the data
        test_project_three_public_message_data = PublicMessageSerializer(test_project_three_public_message, many=True).data

        # attempt to fetch public messages for test_project_three, which auth user is a member of
        url = reverse('project-public-messages-list', kwargs={'project_pk': self.test_project_three.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # data sent in the response should match the data stored in the database
        self.assertEqual(response.data, test_project_three_public_message_data)

    def test_get_public_message_list_with_valid_project_pk_as_guest(self):
        # fetch the public messages for test_project_two from the database
        test_project_two_public_message = PublicMessage.objects.filter(project=self.test_project_two)
        # serialize the public message and store the data
        test_project_two_public_message_data = PublicMessageSerializer(test_project_two_public_message, many=True).data

        # attempt to fetch public messages for test_project_two, which auth user is NOT the owner or member of
        url = reverse('project-public-messages-list', kwargs={'project_pk': self.test_project_two.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # data sent in the response should match the data stored in the database
        self.assertEqual(response.data, test_project_two_public_message_data)

    def test_create_public_message_unauthenticated(self):
        # forcefully unauthenticate the requesting user
        self.client.force_authenticate(user=None)

        # initial public message count in the database for test_project_one
        initial_test_project_one_public_message_count = PublicMessage.objects.filter(project=self.test_project_one).count()

        message_data = {
            'message': 'This is a test message'
        }

        # attempt to create a public message for test_project_one, which the auth user is the owner of
        url = reverse('project-public-messages-list', kwargs={'project_pk': self.test_project_one.pk})
        response = self.client.post(url, message_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # no new message should have been added
        self.assertEqual(
            PublicMessage.objects.filter(project=self.test_project_one).count(),
            initial_test_project_one_public_message_count
        )

    def test_create_public_message_with_invalid_project_pk(self):
        INVALID_PK = 2500

        message_data = {
            'message': 'This is a test message'
        }

        # attempt to create a public message for a project that doesn't exist
        url = reverse('project-public-messages-list', kwargs={'project_pk': INVALID_PK})
        response = self.client.post(url, message_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_public_message_with_valid_project_pk_as_owner(self):
        # initial public message count in the database for test_project_one
        initial_test_project_one_public_message_count = PublicMessage.objects.filter(project=self.test_project_one).count()

        message_data = {
            'message': 'This is a test message'
        }

        # attempt to create a public message for test_project_one, which the auth user is the owner of
        url = reverse('project-public-messages-list', kwargs={'project_pk': self.test_project_one.pk})
        response = self.client.post(url, message_data, format='json')

        # make sure the public message was created in the database
        try:
            new_public_message = PublicMessage.objects.get(pk=response.data['id'])
        except PublicMessage.DoesNotExist:
            self.fail('Message was not created')
        
        # serialize the public message
        new_public_message = PublicMessageSerializer(new_public_message).data

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # public message count should have increased by 1
        self.assertEqual(
            PublicMessage.objects.filter(project=self.test_project_one).count(),
            initial_test_project_one_public_message_count + 1
        )
        # check the returned data is equal to what is saved in the database
        self.assertEqual(response.data, new_public_message)
        # check the returned data equals the data given to create the message
        self.assertEqual(response.data['message'], new_public_message['message'])

    def test_create_public_message_with_valid_project_pk_as_member(self):
        # initial public message count in the database for test_project_three
        initial_test_project_three_public_message_count = PublicMessage.objects.filter(project=self.test_project_three).count()

        message_data = {
            'message': 'This is a test message'
        }

        # attempt to create a public message for test_project_three, which the auth user is a member of
        url = reverse('project-public-messages-list', kwargs={'project_pk': self.test_project_three.pk})
        response = self.client.post(url, message_data, format='json')

        # make sure the public message was created in the database
        try:
            new_public_message = PublicMessage.objects.get(pk=response.data['id'])
        except PublicMessage.DoesNotExist:
            self.fail('Message was not created')
        
        # serialize the public message
        new_public_message = PublicMessageSerializer(new_public_message).data

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # public message count should have increased by 1
        self.assertEqual(
            PublicMessage.objects.filter(project=self.test_project_three).count(),
            initial_test_project_three_public_message_count + 1
        )
        # check the returned data is equal to what is saved in the database
        self.assertEqual(response.data, new_public_message)
        # check the returned data equals the data given to create the message
        self.assertEqual(response.data['message'], new_public_message['message'])

    def test_create_public_message_with_valid_project_pk_as_member(self):
        # initial public message count in the database for test_project_two
        initial_test_project_two_public_message_count = PublicMessage.objects.filter(project=self.test_project_two).count()

        message_data = {
            'message': 'This is a test message'
        }

        # attempt to create a public message for test_project_two, which the auth user NOT the owner or a member of
        url = reverse('project-public-messages-list', kwargs={'project_pk': self.test_project_two.pk})
        response = self.client.post(url, message_data, format='json')

        # make sure the public message was created in the database
        try:
            new_public_message = PublicMessage.objects.get(pk=response.data['id'])
        except PublicMessage.DoesNotExist:
            self.fail('Message was not created')
        
        # serialize the public message
        new_public_message = PublicMessageSerializer(new_public_message).data

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # public message count should have increased by 1
        self.assertEqual(
            PublicMessage.objects.filter(project=self.test_project_two).count(),
            initial_test_project_two_public_message_count + 1
        )
        # check the returned data is equal to what is saved in the database
        self.assertEqual(response.data, new_public_message)
        # check the returned data equals the data given to create the message
        self.assertEqual(response.data['message'], new_public_message['message'])

class PublicMessageDetailViewTest(APITestCase):
    # this setup is re-run before each test
    def setUp(self):
        # create the user to be authenticated and make calls to endpoints
        self.user = create_user(
            username = 'johndoe',
            email = 'johndoe@fakeuniversity.com',
            first_name = 'John',
            last_name = 'Doe',
            password = PASS,
        )
        # create another test user
        self.other_user = create_user(
            username = 'jeffdoe',
            email = 'jeffdoe@fakeuniversity.com',
            first_name = 'Jeff',
            last_name = 'Doe',
            password = PASS,
        )
        # create a project with the authenticated user as the owner
        self.test_project_one = Project.objects.create(
            title = 'Test Project 1',
            description = 'Test project 1 description.',
            category = 'ART',
            owner = self.user,
            owner_role = 'Test Owner Role',
            desired_roles = [
                'Software Engineer',
                'Data Analyst'
            ]
        )
        # create a project with the other test user as the owner
        self.test_project_two = Project.objects.create(
            title = 'Test Project 2',
            description = 'Test project 2 description.',
            category = 'ART',
            owner = self.other_user,
            owner_role = 'Test Owner Role',
            desired_roles = [
                'Director',
                'Actor'
            ]
        )
        # create a project with the other test user as the owner and the authenticated user as a member
        self.test_project_three = Project.objects.create(
            title = 'Test Project 3',
            description = 'Test project 3 description.',
            category = 'ART',
            owner = self.other_user,
            owner_role = 'Test Owner Role',
            desired_roles = [
                'Director',
                'Actor'
            ]
        )

        # create a memebership to make authenticated user a member of test_project_three
        self.test_project_three_membership_one = Membership.objects.create(
            role = 'Test Role',
            project = self.test_project_three,
            user = self.user
        )

        # create a public message for test_project_one by the project owner
        self.test_project_one_public_message_one = PublicMessage.objects.create(
            user = self.user,
            project = self.test_project_one,
            message = 'Test message 1',
        )

        # create a public message for test_project_two by the project owner
        self.test_project_two_public_message_one = PublicMessage.objects.create(
            user = self.other_user,
            project = self.test_project_two,
            message = 'Test message 1',
        )

        # create a public message for test_project_three by the project owner
        self.test_project_three_public_message_one = PublicMessage.objects.create(
            user = self.other_user,
            project = self.test_project_three,
            message = 'Test message 1',
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
    
    def test_get_public_message_detail_unauthenticated(self):
        # forcefully unauthenticate the requesting user
        self.client.force_authenticate(user=None)

        # attempt to fetch a public message for test_project_one, which the auth user is the owner of
        url = reverse(
            'project-public-messages-detail',
            kwargs={
                'project_pk': self.test_project_one.pk,
                'message_pk': self.test_project_one_public_message_one.pk
            }
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_public_message_detail_with_invalid_project_pk(self):
        INVALID_PK = 2500

        # attempt to fetch a public message for a project that doesn't exist
        url = reverse(
            'project-public-messages-detail',
            kwargs={
                'project_pk': INVALID_PK,
                'message_pk': INVALID_PK
            }
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_public_message_detail_with_invalid_message_pk(self):
        INVALID_PK = 2500

        # attempt to fetch a public message that doesn't exist
        # for test_project_one, which the auth user is the owner of
        url = reverse(
            'project-public-messages-detail',
            kwargs={
                'project_pk': self.test_project_one.pk,
                'message_pk': INVALID_PK
            }
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_public_message_detail_with_valid_project_pk_and_message_pk_as_owner(self):
        # serialize the public message and store the data
        test_project_one_public_message_one_data = PublicMessageSerializer(self.test_project_one_public_message_one).data


        # attempt to fetch a public message for test_project_one, 
        # which the auth user is the owner of
        url = reverse(
            'project-public-messages-detail',
            kwargs={
                'project_pk': self.test_project_one.pk,
                'message_pk': self.test_project_one_public_message_one.pk
            }
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # data sent in the response should match the data stored in the database
        self.assertEqual(response.data, test_project_one_public_message_one_data)

    def test_get_public_message_detail_with_valid_project_pk_and_message_pk_as_member(self):
        # serialize the public message and store the data
        test_project_three_public_message_one_data = PublicMessageSerializer(self.test_project_three_public_message_one).data


        # attempt to fetch a public message for test_project_three, 
        # which the auth user is a member of
        url = reverse(
            'project-public-messages-detail',
            kwargs={
                'project_pk': self.test_project_three.pk,
                'message_pk': self.test_project_three_public_message_one.pk
            }
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # data sent in the response should match the data stored in the database
        self.assertEqual(response.data, test_project_three_public_message_one_data)

    def test_get_public_message_detail_with_valid_project_pk_and_message_pk_as_guest(self):
        # serialize the public message and store the data
        test_project_two_public_message_one_data = PublicMessageSerializer(self.test_project_two_public_message_one).data


        # attempt to fetch a public message for test_project_two, 
        # which the auth user is NOT the owner or a member of
        url = reverse(
            'project-public-messages-detail',
            kwargs={
                'project_pk': self.test_project_two.pk,
                'message_pk': self.test_project_two_public_message_one.pk
            }
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # data sent in the response should match the data stored in the database
        self.assertEqual(response.data, test_project_two_public_message_one_data)
    





