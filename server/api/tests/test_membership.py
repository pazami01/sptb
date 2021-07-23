import json

from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from ..models import Membership, Project, Request
from ..serializers import (MembershipSerializer, ProjectSerializer,
                           RequestSerializer, RequestUpdateSerializer)

USER_MODEL = get_user_model()
PASS = 'password123!'

def create_user(username, email, first_name, last_name, password):
    try:
        user = USER_MODEL.objects.create_user(username, email, first_name, last_name, password)
    except IntegrityError:
        user = USER_MODEL.objects.get(username=username)
    
    return user


class MembershipListViewTest(APITestCase):
    # this setup is re-run before each test
    def setUp(self):
        self.user = create_user(
            username = 'johndoe',
            email = 'johndoe@fakeuniversity.com',
            first_name = 'John',
            last_name = 'Doe',
            password = PASS,
        )
        self.other_user = create_user(
            username = 'jeffdoe',
            email = 'jeffdoe@fakeuniversity.com',
            first_name = 'Jeff',
            last_name = 'Doe',
            password = PASS,
        )
        self.project_one = Project.objects.create(
            title = 'Test Project 1',
            description = 'Test project 1 description.',
            category = 'ART',
            owner = self.user,
            owner_role = 'Test Owner Role',
            desired_roles = [
                'Test Role 1',
                'Test Role 2'
            ]
        )
        self.project_two = Project.objects.create(
            title = 'Test Project 2',
            description = 'Test project 2 description.',
            category = 'ART',
            owner = self.other_user,
            owner_role = 'Test Owner Role',
            desired_roles = [
                'Test Role 1',
                'Test Role 2'
            ]
        )
        self.project_three = Project.objects.create(
            title = 'Test Project 3',
            description = 'Test project 3 description.',
            category = 'ART',
            owner = self.other_user,
            owner_role = 'Test Owner Role',
            desired_roles = [
                'Test Role 1',
                'Test Role 2'
            ]
        )
        # create two memberships for the requesting user
        self.membership_one = Membership.objects.create(
            role = 'Test Role',
            project = self.project_two,
            user = self.user
        )
        self.membership_two = Membership.objects.create(
            role = 'Test Role',
            project = self.project_three,
            user = self.user
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
    
    def test_get_membership_list_unauthenticated(self):
        # forcefully unauthenticate the requesting user
        self.client.force_authenticate(user=None)

        url = reverse('membership-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_membership_list(self):
        # get all memberships of the authenticated user
        memberships = Membership.objects.filter(user=self.user)
        # serialize the projects data
        memberships_data = MembershipSerializer(memberships, many=True).data

        url = reverse('membership-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, memberships_data)


class MembershipDetailViewTest(APITestCase):
    # this setup is re-run before each test
    def setUp(self):
        self.user = create_user(
            username = 'johndoe',
            email = 'johndoe@fakeuniversity.com',
            first_name = 'John',
            last_name = 'Doe',
            password = PASS,
        )
        self.other_user = create_user(
            username = 'jeffdoe',
            email = 'jeffdoe@fakeuniversity.com',
            first_name = 'Jeff',
            last_name = 'Doe',
            password = PASS,
        )
        self.project_one = Project.objects.create(
            title = 'Test Project 1',
            description = 'Test project 1 description.',
            category = 'ART',
            owner = self.user,
            owner_role = 'Test Owner Role',
            desired_roles = [
                'Test Role 1',
                'Test Role 2'
            ]
        )
        self.project_two = Project.objects.create(
            title = 'Test Project 2',
            description = 'Test project 2 description.',
            category = 'ART',
            owner = self.other_user,
            owner_role = 'Test Owner Role',
            desired_roles = [
                'Test Role 1',
                'Test Role 2'
            ]
        )
        self.project_three = Project.objects.create(
            title = 'Test Project 3',
            description = 'Test project 3 description.',
            category = 'ART',
            owner = self.other_user,
            owner_role = 'Test Owner Role',
            desired_roles = [
                'Test Role 1',
                'Test Role 2'
            ]
        )
        # create two memberships for the requesting user
        self.membership_one = Membership.objects.create(
            role = 'Test Role',
            project = self.project_two,
            user = self.user
        )
        self.membership_two = Membership.objects.create(
            role = 'Test Role',
            project = self.project_three,
            user = self.user
        )
        # create one membership for other user
        self.other_membership_one = Membership.objects.create(
            role = 'Test Role',
            project = self.project_one,
            user = self.other_user
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

    def test_get_membership_detail_unauthenticated(self):
        # forcefully unauthenticate the requesting user
        self.client.force_authenticate(user=None)

        url = reverse('membership-detail', kwargs={'membership_pk': self.membership_one.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_membership_detail_invalid_pk(self):
        INVALID_PK = 2500
        url = reverse('membership-detail', kwargs={'membership_pk': INVALID_PK})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_membership_detail_as_the_member(self):
        # requesting user is the member of membership_one

        membership_data = MembershipSerializer(self.membership_one).data

        # the authenticated user is the owner of project_one
        url = reverse('membership-detail', kwargs={'membership_pk': self.membership_one.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, membership_data)

    def test_get_membership_detail_as_other_user(self):
        # requesting user is NOT the member of other_membership_one
        
        membership_data = MembershipSerializer(self.other_membership_one).data

        # the authenticated user is the owner of project_one
        url = reverse('membership-detail', kwargs={'membership_pk': self.other_membership_one.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, membership_data)

    def test_update_memebership_detail_unauthenticated(self):
        # forcefully unauthenticate the user
        self.client.force_authenticate(user=None)

        new_data = {
            'role': 'New Updated Role'
        }

        url = reverse('membership-detail', kwargs={'membership_pk': self.membership_one.pk})
        response = self.client.put(url, new_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_membership_detail_with_invalid_pk(self):
        INVALID_PK = 2500
        new_data = {
            'role': 'New Updated Role'
        }

        url = reverse('membership-detail', kwargs={'membership_pk': INVALID_PK})
        response = self.client.put(url, new_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_membership_detail_unauthorized(self):
        # the authenticated user is the member of membership_one
        membership_data_before_update = MembershipSerializer(self.membership_one).data

        new_data = {
            'role': 'New Updated Role'
        }

        # the member is trying to update their own membership role
        url = reverse('membership-detail', kwargs={'membership_pk': self.membership_one.pk})
        response = self.client.put(url, new_data, format='json')

        # fetch the membership from the database after the update
        membership_after_update = Membership.objects.get(pk=self.membership_one.pk)
        membership_data_after_update = MembershipSerializer(membership_after_update).data

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # member should not be able to update their membership role
        self.assertEqual(membership_data_after_update, membership_data_before_update)

    def test_update_membership_detail_with_invalid_data(self):
        # the authenticated user is the owner of the project associated with other_membership_one
        membership_data_before_update = MembershipSerializer(self.other_membership_one).data

        new_data = {
            'role': ['New Role']  # invalid value
        }

        # the member is trying to update the role of one of the members of his/her project
        url = reverse('membership-detail', kwargs={'membership_pk': self.other_membership_one.pk})
        response = self.client.put(url, new_data, format='json')

        # fetch the membership from the database after the update
        membership_after_update = Membership.objects.get(pk=self.other_membership_one.pk)
        membership_data_after_update = MembershipSerializer(membership_after_update).data

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # membership role should remain unchanged
        self.assertEqual(membership_data_after_update, membership_data_before_update)

    def test_update_membership_detail_with_valid_data(self):
        # the authenticated user is the owner of the project associated with other_membership_one
        membership_data_before_update = MembershipSerializer(self.other_membership_one).data

        new_data = {
            'role': 'New Updated Role'
        }

        # the user is trying to update the role of one of the members of his/her project
        url = reverse('membership-detail', kwargs={'membership_pk': self.other_membership_one.pk})
        response = self.client.put(url, new_data, format='json')

        # fetch the membership from the database after the update
        membership_after_update = Membership.objects.get(pk=self.other_membership_one.pk)
        membership_data_after_update = MembershipSerializer(membership_after_update).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], new_data['role'])
        # the project owner should be able to update the role of his/her project's members
        self.assertNotEqual(membership_data_after_update, membership_data_before_update)

    def test_delete_membership_detail_unauthenticated(self):
        # forcefully unauthenticate the requesting user
        self.client.force_authenticate(user=None)

        url = reverse('membership-detail', kwargs={'membership_pk': self.membership_one.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_membership_detail_with_invalid_pk(self):
        INVALID_PK = 2500

        url = reverse('membership-detail', kwargs={'membership_pk': INVALID_PK})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_membership_detail_unauthorized(self):
        new_user = create_user(
            username = 'samroe',
            email = 'samroe@fakeuniversity.com',
            first_name = 'Sam',
            last_name = 'Roe',
            password = PASS,
        )
        # create a new membership with the new user
        new_user_membership = Membership.objects.create(
            role = 'Test Role',
            project = self.project_two,  # project not owned by requesting/authenticated user
            user = new_user
        )

        # req/auth user attempts to delete a user's membership to a project he/she doesn't own
        url = reverse('membership-detail', kwargs={'membership_pk': new_user_membership.pk})
        response = self.client.delete(url)

        # make sure the membership was not deleted
        try:
            Membership.objects.get(pk=new_user_membership.pk)
        except Membership.DoesNotExist:
            self.fail('Membership was deleted by an unauthorized user')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_membership_detail_as_the_project_owner(self):
        # the authenticated user attempts to delete a membership associated with his/her project
        url = reverse('membership-detail', kwargs={'membership_pk': self.other_membership_one.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # make sure the membership has been deleted from the database
        self.assertRaises(Membership.DoesNotExist, Membership.objects.get, pk=self.other_membership_one.pk)

    def test_delete_membership_detail_as_the_member(self):
        # the authenticated user attempts to delete a membership where he/she is the member
        url = reverse('membership-detail', kwargs={'membership_pk': self.membership_one.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # make sure the membership has been deleted from the database
        self.assertRaises(Membership.DoesNotExist, Membership.objects.get, pk=self.membership_one.pk)

class RequestListViewTest(APITestCase):
    # this setup is re-run before each test
    def setUp(self):
        self.user = create_user(
            username = 'johndoe',
            email = 'johndoe@fakeuniversity.com',
            first_name = 'John',
            last_name = 'Doe',
            password = PASS,
        )
        self.other_user_one = create_user(
            username = 'jeffdoe',
            email = 'jeffdoe@fakeuniversity.com',
            first_name = 'Jeff',
            last_name = 'Doe',
            password = PASS,
        )
        self.other_user_two = create_user(
            username = 'samroe',
            email = 'samroe@fakeuniversity.com',
            first_name = 'Sam',
            last_name = 'Roe',
            password = PASS,
        )
        self.other_user_three = create_user(
            username = 'janeroe',
            email = 'janeroe@fakeuniversity.com',
            first_name = 'Jane',
            last_name = 'Roe',
            password = PASS,
        )
        self.project_one = Project.objects.create(
            title = 'Test Project 1',
            description = 'Test project 1 description.',
            category = 'ART',
            owner = self.user,
            owner_role = 'Test Owner Role',
            desired_roles = [
                'Test Role 1',
                'Test Role 2'
            ]
        )
        self.project_two = Project.objects.create(
            title = 'Test Project 2',
            description = 'Test project 2 description.',
            category = 'ART',
            owner = self.other_user_one,
            owner_role = 'Test Owner Role',
            desired_roles = [
                'Test Role 1',
                'Test Role 2'
            ]
        )
        self.project_three = Project.objects.create(
            title = 'Test Project 3',
            description = 'Test project 3 description.',
            category = 'ART',
            owner = self.other_user_one,
            owner_role = 'Test Owner Role',
            desired_roles = [
                'Test Role 1',
                'Test Role 2'
            ]
        )
        self.project_four = Project.objects.create(
            title = 'Test Project 4',
            description = 'Test project 4 description.',
            category = 'ART',
            owner = self.other_user_two,
            owner_role = 'Test Owner Role',
            desired_roles = [
                'Test Role 1',
                'Test Role 2'
            ]
        )
        self.project_five = Project.objects.create(
            title = 'Test Project 5',
            description = 'Test project 5 description.',
            category = 'ART',
            owner = self.other_user_two,
            owner_role = 'Test Owner Role',
            desired_roles = [
                'Test Role 1',
                'Test Role 2'
            ]
        )
        # create two memberships for the requesting user
        self.membership_one = Membership.objects.create(
            role = 'Test Role',
            project = self.project_two,
            user = self.user
        )
        self.membership_two = Membership.objects.create(
            role = 'Test Role',
            project = self.project_three,
            user = self.user
        )
        # create one membership for other user
        self.other_membership_one = Membership.objects.create(
            role = 'Test Role',
            project = self.project_one,
            user = self.other_user_one
        )
        # create request where requesting (authenticated) user invites other_user_two to join his/her project
        self.request_one = Request.objects.create(
            requester = self.user,
            requestee = self.other_user_two,
            project = self.project_one,
            role = 'Test Role'
        )
        # create request where requesting (authenticated) user is invited to join project_four
        self.request_two = Request.objects.create(
            requester = self.other_user_two,
            requestee = self.user,
            project = self.project_four,
            role = 'Test Role'
        )
        # create an inactive request for the requesting (authenticated) user
        self.inactive_request = Request.objects.create(
            requester = self.other_user_two,
            requestee = self.user,
            project = self.project_four,
            role = 'Test Role',
            is_active = False
        )

        """
        SUMMARY OF THE OBJECTS IN THE DB BEFORE EACH TEST:

        user (requesting/authenticated):
            - owner of project_one
            - member of project_two (membership_one)
            - member of project_three (membership_two)
            - sent request (request_one) to other_user_two to join project_one

        other_user_one:
            - owner of project_two
            - owner of project_three
            - member of project_one (other_membership_one)

        other_user_two:
            - owner of project_four
            - owner of project_five
            - sent request (request_two) to user to join project_four
            - sent request (inactive_request) to user to join project_four (INACTIVE)
        other_user_three:
            - not an owner of any projects
            - no membership
            - no requests
        """

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

    def test_get_request_list_unauthenticated(self):
        # forcefully unauthenticate the requesting user
        self.client.force_authenticate(user=None)

        url = reverse('request-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_request_list(self):
        # get all active requests to and from the authenticated user
        requests = Request.objects.filter((Q(requester=self.user.pk) | Q(requestee=self.user.pk)) & Q(is_active=True))
        # serialize the requests data
        requests_data = RequestSerializer(requests, many=True).data

        url = reverse('request-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, requests_data)

    def test_create_request_list_unauthenticated(self):
        # forcefully unauthenticate the requesting user
        self.client.force_authenticate(user=None)
        # initial count of active requests for the auth user in the database
        initial_active_user_request_count = Request.objects.filter((Q(requester=self.user.pk) | Q(requestee=self.user.pk)) & Q(is_active=True)).count()

        # request data for other_user_three to join project_one
        request_data = {
            'requestee': self.other_user_three.pk,
            'project': self.project_one.pk,
            'role': 'Test Role'
        }

        # attempt to create the request
        url = reverse('request-list')
        response = self.client.post(url, request_data, format='json')

        active_user_request_count_after_creation_attempt = Request.objects.filter((Q(requester=self.user.pk) | Q(requestee=self.user.pk)) & Q(is_active=True)).count()

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(active_user_request_count_after_creation_attempt, initial_active_user_request_count)

    def test_create_request_list_from_project_owner_to_themselves(self):
        # initial count of active requests for the auth user in the database
        initial_active_user_request_count = Request.objects.filter((Q(requester=self.user.pk) | Q(requestee=self.user.pk)) & Q(is_active=True)).count()

        # request data where requester is also the requestee and owner of project_one
        request_data = {
            'requestee': self.user.pk,
            'project': self.project_one.pk,
            'role': 'Test Role'
        }

        # attempt to create the request
        url = reverse('request-list')
        response = self.client.post(url, request_data, format='json')

        active_user_request_count_after_creation_attempt = Request.objects.filter((Q(requester=self.user.pk) | Q(requestee=self.user.pk)) & Q(is_active=True)).count()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(active_user_request_count_after_creation_attempt, initial_active_user_request_count)

    def test_create_request_list_from_non_project_owner_to_themselves(self):
        # initial count of active requests for the auth user in the database
        initial_active_user_request_count = Request.objects.filter((Q(requester=self.user.pk) | Q(requestee=self.user.pk)) & Q(is_active=True)).count()

        # request data where requester is not the owner of project_five and they invite themselves to join
        request_data = {
            'requestee': self.user.pk,
            'project': self.project_five.pk,
            'role': 'Test Role'
        }

        # attempt to create the request
        url = reverse('request-list')
        response = self.client.post(url, request_data, format='json')

        active_user_request_count_after_creation_attempt = Request.objects.filter((Q(requester=self.user.pk) | Q(requestee=self.user.pk)) & Q(is_active=True)).count()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(active_user_request_count_after_creation_attempt, initial_active_user_request_count)

    def test_create_request_list_from_project_owner_to_existing_member(self):
        # initial count of active requests for the auth user in the database
        initial_active_user_request_count = Request.objects.filter((Q(requester=self.user.pk) | Q(requestee=self.user.pk)) & Q(is_active=True)).count()

        # request data where requester is the owner of project_one and is inviting other_user_one who is already a member of that project
        request_data = {
            'requestee': self.other_user_one.pk,
            'project': self.project_one.pk,
            'role': 'Test Role'
        }

        # attempt to create the request
        url = reverse('request-list')
        response = self.client.post(url, request_data, format='json')

        active_user_request_count_after_creation_attempt = Request.objects.filter((Q(requester=self.user.pk) | Q(requestee=self.user.pk)) & Q(is_active=True)).count()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(active_user_request_count_after_creation_attempt, initial_active_user_request_count)

    def test_create_request_list_from_existing_member_to_project_owner(self):
        # initial count of active requests for the auth user in the database
        initial_active_user_request_count = Request.objects.filter((Q(requester=self.user.pk) | Q(requestee=self.user.pk)) & Q(is_active=True)).count()

        # request data where requester is requesting to join a project they are already a member of
        request_data = {
            'requestee': self.other_user_one.pk,
            'project': self.project_two.pk,
            'role': 'Test Role'
        }

        # attempt to create the request
        url = reverse('request-list')
        response = self.client.post(url, request_data, format='json')

        active_user_request_count_after_creation_attempt = Request.objects.filter((Q(requester=self.user.pk) | Q(requestee=self.user.pk)) & Q(is_active=True)).count()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(active_user_request_count_after_creation_attempt, initial_active_user_request_count)

    def test_create_request_list_from_non_project_owner_to_non_project_owner(self):
        # initial count of active requests for the auth user in the database
        initial_active_user_request_count = Request.objects.filter((Q(requester=self.user.pk) | Q(requestee=self.user.pk)) & Q(is_active=True)).count()

        # request data where requester is not the project owner and is requesting another user to join the project
        request_data = {
            'requestee': self.other_user_one.pk,
            'project': self.project_five.pk,
            'role': 'Test Role'
        }

        # attempt to create the request
        url = reverse('request-list')
        response = self.client.post(url, request_data, format='json')

        active_user_request_count_after_creation_attempt = Request.objects.filter((Q(requester=self.user.pk) | Q(requestee=self.user.pk)) & Q(is_active=True)).count()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(active_user_request_count_after_creation_attempt, initial_active_user_request_count)

    def test_create_request_list_where_exact_active_request_already_exists(self):
        # initial count of active requests for the auth user in the database
        initial_active_user_request_count = Request.objects.filter((Q(requester=self.user.pk) | Q(requestee=self.user.pk)) & Q(is_active=True)).count()

        # there is already an active request between requesting user and other_user_two for project_one
        request_data = {
            'requestee': self.other_user_two.pk,
            'project': self.project_one.pk,
            'role': 'Test Role'
        }

        # attempt to create the request
        url = reverse('request-list')
        response = self.client.post(url, request_data, format='json')

        active_user_request_count_after_creation_attempt = Request.objects.filter((Q(requester=self.user.pk) | Q(requestee=self.user.pk)) & Q(is_active=True)).count()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(active_user_request_count_after_creation_attempt, initial_active_user_request_count)

    def test_create_request_list_from_project_owner_to_non_member(self):
        # initial count of active requests for the auth user in the database
        initial_active_user_request_count = Request.objects.filter(
            (Q(requester=self.user.pk) | Q(requestee=self.user.pk)) & Q(is_active=True)
        ).count()

        # prepare request data for other_user_three to join project_one as a member
        request_data = {
            'requestee': self.other_user_three.pk,
            'project': self.project_one.pk,
            'role': 'Test Role'
        }

        url = reverse('request-list')
        # attempt to create the request via a POST HTTP request
        response = self.client.post(url, request_data, format='json')

        # make sure the request was created in the database
        try:
            new_request = Request.objects.get(pk=response.data['id'])
        except Request.DoesNotExist:
            self.fail('Request was not created')
        
        # serialize the new request data
        new_request_data = RequestSerializer(new_request).data
        # count of active requests for the auth user in the database after creation
        active_user_request_count_after_creation_attempt = Request.objects.filter(
            (Q(requester=self.user.pk) | Q(requestee=self.user.pk)) & Q(is_active=True)
        ).count()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            active_user_request_count_after_creation_attempt,
            initial_active_user_request_count + 1
        )
        # check the returned data is equal to what is saved in the database
        self.assertEqual(response.data, new_request_data)
        # check the returned data equals the data given to create the request
        self.assertEqual(response.data['requestee'], request_data['requestee'])
        self.assertEqual(response.data['project'], request_data['project'])
        self.assertEqual(response.data['role'], request_data['role'])

    def test_create_request_list_from_non_member_to_project_owner(self):
        # initial count of active requests for the auth user in the database
        initial_active_user_request_count = Request.objects.filter((Q(requester=self.user.pk) | Q(requestee=self.user.pk)) & Q(is_active=True)).count()

        # request to join other_user_two's project_five as a member
        request_data = {
            'requestee': self.other_user_two.pk,
            'project': self.project_five.pk,
            'role': 'Test Role'
        }

        # attempt to create the request
        url = reverse('request-list')
        response = self.client.post(url, request_data, format='json')

        # make sure the request was created in the database
        try:
            new_request = Request.objects.get(pk=response.data['id'])
        except Request.DoesNotExist:
            self.fail('Request was not created')

        new_request_data = RequestSerializer(new_request).data
        active_user_request_count_after_creation_attempt = Request.objects.filter((Q(requester=self.user.pk) | Q(requestee=self.user.pk)) & Q(is_active=True)).count()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(active_user_request_count_after_creation_attempt, initial_active_user_request_count + 1)
        # check the returned data is equal to what is saved in the database
        self.assertEqual(response.data, new_request_data)
        # check the returned data equals the data given to create the request
        self.assertEqual(response.data['requestee'], request_data['requestee'])
        self.assertEqual(response.data['project'], request_data['project'])
        self.assertEqual(response.data['role'], request_data['role'])


class RequestDetailViewTest(APITestCase):
    # this setup is re-run before each test
    def setUp(self):
        self.user = create_user(
            username = 'johndoe',
            email = 'johndoe@fakeuniversity.com',
            first_name = 'John',
            last_name = 'Doe',
            password = PASS,
        )
        self.other_user_one = create_user(
            username = 'jeffdoe',
            email = 'jeffdoe@fakeuniversity.com',
            first_name = 'Jeff',
            last_name = 'Doe',
            password = PASS,
        )
        self.other_user_two = create_user(
            username = 'samroe',
            email = 'samroe@fakeuniversity.com',
            first_name = 'Sam',
            last_name = 'Roe',
            password = PASS,
        )
        self.other_user_three = create_user(
            username = 'janeroe',
            email = 'janeroe@fakeuniversity.com',
            first_name = 'Jane',
            last_name = 'Roe',
            password = PASS,
        )
        self.project_one = Project.objects.create(
            title = 'Test Project 1',
            description = 'Test project 1 description.',
            category = 'ART',
            owner = self.user,
            owner_role = 'Test Owner Role',
            desired_roles = [
                'Test Role 1',
                'Test Role 2'
            ]
        )
        self.project_two = Project.objects.create(
            title = 'Test Project 2',
            description = 'Test project 2 description.',
            category = 'ART',
            owner = self.other_user_one,
            owner_role = 'Test Owner Role',
            desired_roles = [
                'Test Role 1',
                'Test Role 2'
            ]
        )
        self.project_three = Project.objects.create(
            title = 'Test Project 3',
            description = 'Test project 3 description.',
            category = 'ART',
            owner = self.other_user_one,
            owner_role = 'Test Owner Role',
            desired_roles = [
                'Test Role 1',
                'Test Role 2'
            ]
        )
        self.project_four = Project.objects.create(
            title = 'Test Project 4',
            description = 'Test project 4 description.',
            category = 'ART',
            owner = self.other_user_two,
            owner_role = 'Test Owner Role',
            desired_roles = [
                'Test Role 1',
                'Test Role 2'
            ]
        )
        self.project_five = Project.objects.create(
            title = 'Test Project 5',
            description = 'Test project 5 description.',
            category = 'ART',
            owner = self.other_user_two,
            owner_role = 'Test Owner Role',
            desired_roles = [
                'Test Role 1',
                'Test Role 2'
            ]
        )
        self.project_six = Project.objects.create(
            title = 'Test Project 6',
            description = 'Test project 6 description.',
            category = 'ART',
            owner = self.user,
            owner_role = 'Test Owner Role',
            desired_roles = [
                'Test Role 1',
                'Test Role 2'
            ]
        )
        # create two memberships for the requesting user
        self.membership_one = Membership.objects.create(
            role = 'Test Role',
            project = self.project_two,
            user = self.user
        )
        self.membership_two = Membership.objects.create(
            role = 'Test Role',
            project = self.project_three,
            user = self.user
        )
        # create one membership for other user
        self.other_membership_one = Membership.objects.create(
            role = 'Test Role',
            project = self.project_one,
            user = self.other_user_one
        )
        # create request where requesting (authenticated) user invites other_user_two to join his/her project
        self.request_one = Request.objects.create(
            requester = self.user,
            requestee = self.other_user_two,
            project = self.project_one,
            role = 'Test Role'
        )
        # create request where requesting (authenticated) user is invited to join project_four
        self.request_two = Request.objects.create(
            requester = self.other_user_two,
            requestee = self.user,
            project = self.project_four,
            role = 'Test Role'
        )
        # create request where other_user_one invites other_user_two to join project_three
        self.request_three = Request.objects.create(
            requester = self.other_user_one,
            requestee = self.other_user_two,
            project = self.project_three,
            role = 'Test Role'
        )
        # create request where other_user_one invites other_user_two to join project_three
        self.request_four = Request.objects.create(
            requester = self.other_user_three,
            requestee = self.user,
            project = self.project_six,
            role = 'Test Role'
        )
        # create request where requesting (authenticated) user is requesting other_user_two to join project_five
        self.request_five = Request.objects.create(
            requester = self.user,
            requestee = self.other_user_two,
            project = self.project_five,
            role = 'Test Role'
        )
        # create an inactive request for the requesting (authenticated) user
        self.inactive_request = Request.objects.create(
            requester = self.other_user_two,
            requestee = self.user,
            project = self.project_four,
            role = 'Test Role',
            is_active = False
        )

        """
        SUMMARY OF THE OBJECTS IN THE DB BEFORE EACH TEST:

        user (requesting/authenticated):
            - owner of project_one
            - owner of project_six
            - member of project_two (membership_one)
            - member of project_three (membership_two)
            - sent request (request_one) to other_user_two to join project_one
            - sent request (request_five) to other_user_two to join project_five

        other_user_one:
            - owner of project_two
            - owner of project_three
            - member of project_one (other_membership_one)
            - sent request (request_three) to other_user_two to join project_three

        other_user_two:
            - owner of project_four
            - owner of project_five
            - sent request (request_two) to user to join project_four
            - sent request (inactive_request) to user to join project_four (INACTIVE)
        other_user_three:
            - not an owner of any projects
            - no membership
            - sent request (request_four) to user to join their project_six
        """

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

    def test_get_request_detail_unauthenticated(self):
        # forcefully unauthenticate the requesting user
        self.client.force_authenticate(user=None)

        # attempt to fetch a request
        url = reverse('request-detail', kwargs={'request_pk': self.request_one.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_request_detail_with_invalid_pk(self):
        INVALID_PK = 2500
        url = reverse('request-detail', kwargs={'request_pk': INVALID_PK})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_request_detail_with_active_equal_to_false(self):
        # inactive request sent from other_user_two to user (authenticated) for project_four
        url = reverse('request-detail', kwargs={'request_pk': self.inactive_request.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_request_detail_unauthorized(self):
        # attempt to fetch an active request where the user (authenticated) is not the requester or the requestee
        url = reverse('request-detail', kwargs={'request_pk': self.request_three.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_request_detail_as_the_requester(self):
        request_data = RequestSerializer(self.request_one).data

        # attempt to fetch an active request where the user (authenticated) is the requester
        url = reverse('request-detail', kwargs={'request_pk': self.request_one.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, request_data)

    def test_get_request_detail_as_the_requestee(self):
        request_data = RequestSerializer(self.request_two).data

        # attempt to fetch an active request where the user (authenticated) is the requestee
        url = reverse('request-detail', kwargs={'request_pk': self.request_two.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, request_data)

    def test_update_request_detail_unauthenticated(self):
        # forcefully unauthenticate the user
        self.client.force_authenticate(user=None)

        new_data = {
            'status': 'ACP'
        }

        url = reverse('request-detail', kwargs={'request_pk': self.request_two.pk})
        response = self.client.put(url, new_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_request_detail_with_invalid_pk(self):
        INVALID_PK = 2500

        new_data = {
            'status': 'ACP'
        }

        url = reverse('request-detail', kwargs={'request_pk': INVALID_PK})
        response = self.client.put(url, new_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_request_detail_with_active_equal_to_false(self):
        new_data = {
            'status': 'ACP'
        }

        url = reverse('request-detail', kwargs={'request_pk': self.inactive_request.pk})
        response = self.client.put(url, new_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_request_detail_unauthorized(self):
        # authenticated user is not the requester or requestee of request_three (i.e. is unauthorized)
        request_data_before_update = RequestUpdateSerializer(self.request_three).data

        new_data = {
            'status': 'ACP'
        }
        
        # attempt to update a request where the authenticated user has no association
        url = reverse('request-detail', kwargs={'request_pk': self.request_three.pk})
        response = self.client.put(url, new_data, format='json')

        # fetch the request from the database after the update attempt
        request_after_update = Request.objects.get(pk=self.request_three.pk)
        request_data_after_update = RequestUpdateSerializer(request_after_update).data

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(request_data_after_update, request_data_before_update)

    def test_update_request_detail_as_requester_and_project_owner_accept_request(self):
        # authenticated user is the requester of request_one and the owner of the associated project
        request_data_before_update = RequestUpdateSerializer(self.request_one).data

        new_data = {
            'status': 'ACP'
        }
        
        # authenticated user attempts to accept their own request
        url = reverse('request-detail', kwargs={'request_pk': self.request_one.pk})
        response = self.client.put(url, new_data, format='json')

        # fetch the request from the database after the update attempt
        request_after_update = Request.objects.get(pk=self.request_one.pk)
        request_data_after_update = RequestUpdateSerializer(request_after_update).data

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(request_data_after_update, request_data_before_update)

    def test_update_request_detail_as_requester_and_project_owner_decline_request(self):
        # authenticated user is the requester of request_one and the owner of the associated project
        request_data_before_update = RequestUpdateSerializer(self.request_one).data

        new_data = {
            'status': 'DCN'
        }
        
        # authenticated user attempts to decline their own request
        url = reverse('request-detail', kwargs={'request_pk': self.request_one.pk})
        response = self.client.put(url, new_data, format='json')

        # fetch the request from the database after the update attempt
        request_after_update = Request.objects.get(pk=self.request_one.pk)
        request_data_after_update = RequestUpdateSerializer(request_after_update).data

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(request_data_after_update, request_data_before_update)

    def test_update_request_detail_as_requester_and_project_owner_cancel_request(self):
        # authenticated user is the requester of request_one and the owner of the associated project
        request_data_before_update = RequestUpdateSerializer(self.request_one).data

        new_data = {
            'status': 'CNL'
        }
        
        # authenticated user attempts to cancel their own request
        url = reverse('request-detail', kwargs={'request_pk': self.request_one.pk})
        response = self.client.put(url, new_data, format='json')

        # fetch the request from the database after the update attempt
        request_after_update = Request.objects.get(pk=self.request_one.pk)
        request_data_after_update = RequestUpdateSerializer(request_after_update).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # the request should now be made inactive
        self.assertEqual(request_after_update.is_active, False)
        self.assertNotEqual(request_data_after_update, request_data_before_update)
        # make sure a membership for the project was not created
        self.assertRaises(Membership.DoesNotExist, Membership.objects.get, role=self.request_one.role, project=self.request_one.project, user=self.request_one.requestee)

    def test_update_request_detail_as_requestee_and_project_owner_accept_request(self):
        # authenticated user is the requestee of request_four and the owner of the associated project
        request_data_before_update = RequestUpdateSerializer(self.request_four).data

        new_data = {
            'status': 'ACP'
        }
        
        # authenticated user attempts to accept the request sent from another user to join project_six
        url = reverse('request-detail', kwargs={'request_pk': self.request_four.pk})
        response = self.client.put(url, new_data, format='json')

        # fetch the request from the database after the update attempt
        request_after_update = Request.objects.get(pk=self.request_four.pk)
        request_data_after_update = RequestUpdateSerializer(request_after_update).data

        try:
            Membership.objects.get(role=self.request_four.role, project=self.request_four.project, user=self.request_four.requester)
        except Membership.DoesNotExist:
            self.fail('Membership was not created')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # the request should now be made inactive
        self.assertEqual(request_after_update.is_active, False)
        self.assertNotEqual(request_data_after_update, request_data_before_update)

    def test_update_request_detail_as_requestee_and_project_owner_decline_request(self):
        # authenticated user is the requestee of request_four and the owner of the associated project
        request_data_before_update = RequestUpdateSerializer(self.request_four).data

        new_data = {
            'status': 'DCN'
        }
        
        # authenticated user attempts to decline the request sent from another user to join project_six
        url = reverse('request-detail', kwargs={'request_pk': self.request_four.pk})
        response = self.client.put(url, new_data, format='json')

        # fetch the request from the database after the update attempt
        request_after_update = Request.objects.get(pk=self.request_four.pk)
        request_data_after_update = RequestUpdateSerializer(request_after_update).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # the request should now be made inactive
        self.assertEqual(request_after_update.is_active, False)
        self.assertNotEqual(request_data_after_update, request_data_before_update)
        # make sure a membership for the project was not created
        self.assertRaises(Membership.DoesNotExist, Membership.objects.get, role=self.request_four.role, project=self.request_four.project, user=self.request_four.requester)

    def test_update_request_detail_as_requestee_and_project_owner_cancel_request(self):
        # authenticated user is the requestee of request_four and the owner of the associated project
        request_data_before_update = RequestUpdateSerializer(self.request_four).data

        new_data = {
            'status': 'CNL'
        }
        
        # authenticated user attempts to cancel the request sent from another user to join project_six
        url = reverse('request-detail', kwargs={'request_pk': self.request_four.pk})
        response = self.client.put(url, new_data, format='json')

        # fetch the request from the database after the update attempt
        request_after_update = Request.objects.get(pk=self.request_four.pk)
        request_data_after_update = RequestUpdateSerializer(request_after_update).data

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # data should be unchaged as a requestee cannot cancel a request
        self.assertEqual(request_data_after_update, request_data_before_update)

    def test_update_request_detail_as_requester_accept_request(self):
        # authenticated user is the requester of request_five but NOT the owner of the associated project
        request_data_before_update = RequestUpdateSerializer(self.request_five).data

        new_data = {
            'status': 'ACP'
        }
        
        # authenticated user attempts to accept their own request
        url = reverse('request-detail', kwargs={'request_pk': self.request_five.pk})
        response = self.client.put(url, new_data, format='json')

        # fetch the request from the database after the update attempt
        request_after_update = Request.objects.get(pk=self.request_five.pk)
        request_data_after_update = RequestUpdateSerializer(request_after_update).data

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(request_data_after_update, request_data_before_update)

    def test_update_request_detail_as_requester_decline_request(self):
        # authenticated user is the requester of request_five but NOT the owner of the associated project
        request_data_before_update = RequestUpdateSerializer(self.request_five).data

        new_data = {
            'status': 'DCN'
        }
        
        # authenticated user attempts to decline their own request
        url = reverse('request-detail', kwargs={'request_pk': self.request_five.pk})
        response = self.client.put(url, new_data, format='json')

        # fetch the request from the database after the update attempt
        request_after_update = Request.objects.get(pk=self.request_five.pk)
        request_data_after_update = RequestUpdateSerializer(request_after_update).data

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(request_data_after_update, request_data_before_update)

    def test_update_request_detail_as_requester_cancel_request(self):
        # authenticated user is the requester of request_five but NOT the owner of the associated project
        request_data_before_update = RequestUpdateSerializer(self.request_five).data

        new_data = {
            'status': 'CNL'
        }
        
        # authenticated user attempts to cancel their own request
        url = reverse('request-detail', kwargs={'request_pk': self.request_five.pk})
        response = self.client.put(url, new_data, format='json')

        # fetch the request from the database after the update attempt
        request_after_update = Request.objects.get(pk=self.request_five.pk)
        request_data_after_update = RequestUpdateSerializer(request_after_update).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # the request should now be made inactive
        self.assertEqual(request_after_update.is_active, False)
        self.assertNotEqual(request_data_after_update, request_data_before_update)
        # make sure a membership for the project was not created
        self.assertRaises(Membership.DoesNotExist, Membership.objects.get, role=self.request_five.role, project=self.request_five.project, user=self.request_five.requester)

    def test_update_request_detail_as_requestee_accept_request(self):
        # authenticated user is the requestee of request_two but NOT the owner of the associated project
        request_data_before_update = RequestUpdateSerializer(self.request_two).data

        new_data = {
            'status': 'ACP'
        }
        
        # authenticated user attempts to accept the request sent from another user to join project_four
        url = reverse('request-detail', kwargs={'request_pk': self.request_two.pk})
        response = self.client.put(url, new_data, format='json')

        # fetch the request from the database after the update attempt
        request_after_update = Request.objects.get(pk=self.request_two.pk)
        request_data_after_update = RequestUpdateSerializer(request_after_update).data

        try:
            Membership.objects.get(role=self.request_two.role, project=self.request_two.project, user=self.request_two.requestee)
        except Membership.DoesNotExist:
            self.fail('Membership was not created')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # the request should now be made inactive
        self.assertEqual(request_after_update.is_active, False)
        self.assertNotEqual(request_data_after_update, request_data_before_update)

    def test_update_request_detail_as_requestee_decline_request(self):
        # authenticated user is the requestee of request_two but NOT the owner of the associated project
        request_data_before_update = RequestUpdateSerializer(self.request_two).data

        new_data = {
            'status': 'DCN'
        }
        
        # authenticated user attempts to decline the request sent from another user to join project_four
        url = reverse('request-detail', kwargs={'request_pk': self.request_two.pk})
        response = self.client.put(url, new_data, format='json')

        # fetch the request from the database after the update attempt
        request_after_update = Request.objects.get(pk=self.request_two.pk)
        request_data_after_update = RequestUpdateSerializer(request_after_update).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # the request should now be made inactive
        self.assertEqual(request_after_update.is_active, False)
        self.assertNotEqual(request_data_after_update, request_data_before_update)
        # make sure a membership for the project was not created
        self.assertRaises(Membership.DoesNotExist, Membership.objects.get, role=self.request_two.role, project=self.request_two.project, user=self.request_two.requestee)

    def test_update_request_detail_as_requestee_cancel_request(self):
        # authenticated user is the requestee of request_two but NOT the owner of the associated project
        request_data_before_update = RequestUpdateSerializer(self.request_two).data

        new_data = {
            'status': 'CNL'
        }
        
        # authenticated user attempts to cancel the request sent from another user to join project_four
        url = reverse('request-detail', kwargs={'request_pk': self.request_two.pk})
        response = self.client.put(url, new_data, format='json')

        # fetch the request from the database after the update attempt
        request_after_update = Request.objects.get(pk=self.request_two.pk)
        request_data_after_update = RequestUpdateSerializer(request_after_update).data

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # data should be unchaged as a requestee cannot cancel a request
        self.assertEqual(request_data_after_update, request_data_before_update)



