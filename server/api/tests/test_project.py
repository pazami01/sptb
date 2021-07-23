import json
import time

from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from ..models import Project, Follow, Membership
from ..serializers import ProjectSerializer, FollowSerializer

USER_MODEL = get_user_model()
PASS = 'password123!'

def create_user(username, email, first_name, last_name, password):
    try:
        user = USER_MODEL.objects.create_user(username, email, first_name, last_name, password)
    except IntegrityError:
        user = USER_MODEL.objects.get(username=username)
    
    return user


class ProjectListViewTest(APITestCase):
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

        # delay to make sure test_project_two is created after test_project_one
        time.sleep(2)

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
    
    def test_get_project_list_unauthenticated(self):
        # forcefully unauthenticate the requesting user
        self.client.force_authenticate(user=None)

        url = reverse('project-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_project_list(self):
        # get all projects from the database
        projects = Project.objects.all()
        # serialize the projects data
        projects_data = ProjectSerializer(projects, many=True).data

        url = reverse('project-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, projects_data)

    def test_get_project_list_with_search_query(self):
        # get a list of projects that have an 'engineer' substring in their desired roles
        url = f'{reverse("project-list")}?search=engineer'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.test_project_one.title)

    def test_get_project_list_with_relation_is_active_query(self):
        # create another project not owned by authenticated user
        test_project_three = Project.objects.create(
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

        # add the authenticated user as a member of the project
        membership_one = Membership.objects.create(
            role = 'Test Role',
            project = test_project_three,
            user = self.user
        )

        # get a list of projects that the authenticated user either owns or is a member of
        url = f'{reverse("project-list")}?relation=active'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['title'], self.test_project_one.title)
        self.assertEqual(response.data[1]['title'], test_project_three.title)

    def test_get_project_list_with_relation_is_owned_query(self):
        # get a list of projects that the authenticated user owns
        url = f'{reverse("project-list")}?relation=owned'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.test_project_one.title)

    def test_get_project_list_with_relation_is_followed_query(self):
        # authenticated user follows test_project_two
        follow_one = Follow.objects.create(
            user = self.user,
            project = self.test_project_two
        )

        # get a list of projects that the authenticated user follows
        url = f'{reverse("project-list")}?relation=followed'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.test_project_two.title)

    def test_get_project_list_with_order_is_ascending_query(self):
        # get a list of projects in ascending order by date created
        url = f'{reverse("project-list")}?order=ascending'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['title'], self.test_project_one.title)
        self.assertEqual(response.data[1]['title'], self.test_project_two.title)

    def test_get_project_list_with_order_is_descending_query(self):
        # get a list of projects in descending order by date created
        url = f'{reverse("project-list")}?order=descending'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['title'], self.test_project_two.title)
        self.assertEqual(response.data[1]['title'], self.test_project_one.title)

    def test_get_project_list_with_order_is_popularity_query(self):
        # create another user
        other_user_two = create_user(
            username = 'janedoe',
            email = 'janedoe@fakeuniversity.com',
            first_name = 'Jane',
            last_name = 'Doe',
            password = PASS,
        )

        # other_user follows test_project_two
        follow_one = Follow.objects.create(
            user = self.other_user,
            project = self.test_project_two
        )
        # other_user_two follows test_project_two
        follow_one = Follow.objects.create(
            user = other_user_two,
            project = self.test_project_two
        )

        # get a list of projects ordered by most followers in descending order
        url = f'{reverse("project-list")}?order=popularity'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        # test_project_two should be the most popular (first on the list)
        self.assertEqual(response.data[0]['title'], self.test_project_two.title)

    def test_get_project_list_with_limit_query(self):
        # get a list of projects limited to 1
        url = f'{reverse("project-list")}?limit=1'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], self.test_project_one.title)

    def test_create_project_unauthenticated(self):
        # forcefully unauthenticate the requesting user
        self.client.force_authenticate(user=None)
        # initial project count in the database
        initial_projects_count = Project.objects.count()

        project_data = {
            'title': 'Test Title',
            'description': 'Test description',
            'category': 'ART',
            'owner_role': 'Test Role',
            'desired_roles': [
                'Test Role 1',
                'Test Role 2',
            ]
        }

        url = reverse('project-list')
        response = self.client.post(url, project_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Project.objects.count(), initial_projects_count)

    def test_create_project_with_invalid_data(self):
        # initial project count in the database
        initial_projects_count = Project.objects.count()

        project_data = {
            'title': 'Test Title',
            'description': 'Test description',
            'category': 'WRONG_CATEGORY',  # invalid category
            'owner_role': 'Test Role',
            'desired_roles': [
                'Test Role 1',
                'Test Role 2',
            ]
        }

        url = reverse('project-list')
        response = self.client.post(url, project_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Project.objects.count(), initial_projects_count)

    def test_create_project_with_valid_data(self):
        # initial project count in the database
        initial_projects_count = Project.objects.count()

        project_data = {
            'title': 'Test Title',
            'description': 'Test description',
            'category': 'ART',
            'owner_role': 'Test Role',
            'desired_roles': [
                'Test Role 1',
                'Test Role 2',
            ]
        }

        url = reverse('project-list')
        response = self.client.post(url, project_data, format='json')

        # make sure the project was created in the database
        try:
            new_project = Project.objects.get(pk=response.data['id'])
        except Project.DoesNotExist:
            self.fail('Project was not created')

        new_project_data = ProjectSerializer(new_project).data

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), initial_projects_count + 1)
        # check the returned data is equal to what is saved in the database
        self.assertEqual(response.data, new_project_data)
        # check the returned data equals the data given to create the project
        self.assertEqual(response.data['title'], project_data['title'])
        self.assertEqual(response.data['description'], project_data['description'])
        self.assertEqual(response.data['category'], project_data['category'])
        self.assertEqual(response.data['owner_role'], project_data['owner_role'])
        self.assertEqual(response.data['desired_roles'], project_data['desired_roles'])

class ProjectDetailViewTest(APITestCase):
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
    
    def test_get_project_detail_unauthenticated(self):
        # forcefully unauthenticate the requesting user
        self.client.force_authenticate(user=None)

        # attempt to retrieve data for a project
        url = reverse('project-detail', kwargs={'project_pk': self.project_one.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_project_detail_with_invalid_pk(self):
        # an invalid primary key
        INVALID_PK = 2500

        # attempt to retrieve data for a non-existant project
        url = reverse('project-detail', kwargs={'project_pk': INVALID_PK})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_project_detail_as_project_owner(self):
        project_data = ProjectSerializer(self.project_one).data

        # the authenticated user is the owner of project_one
        url = reverse('project-detail', kwargs={'project_pk': self.project_one.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, project_data)

    def test_get_project_detail_as_not_the_owner(self):
        project_data = ProjectSerializer(self.project_two).data

        # the authenticated user is NOT the owner of project_two
        url = reverse('project-detail', kwargs={'project_pk': self.project_two.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, project_data)

    def test_update_project_detail_unauthenticated(self):
        # forcefully unauthenticate the user
        self.client.force_authenticate(user=None)

        new_data = {
            'title': 'New Title',
            'description': 'New description',
            'category': 'ART',
            'owner_role': 'New Role',
            'desired_roles': [
                'New Role 1',
                'New Role 2',
            ]
        }

        url = reverse('project-detail', kwargs={'project_pk': self.project_one.pk})
        response = self.client.put(url, new_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_project_detail_with_invalid_pk(self):
        INVALID_PK = 2500
        new_data = {
            'title': 1234,  # invalid value
            'description': 'New description',
            'category': 'ART',
            'owner_role': 'New Role',
            'desired_roles': [
                'New Role 1',
                'New Role 2',
            ]
        }

        url = reverse('project-detail', kwargs={'project_pk': INVALID_PK})
        response = self.client.put(url, new_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_project_detail_unauthorized(self):
        # the authenticated user is NOT the owner of project_two (i.e. not authorized to update)
        project_data_before_update = ProjectSerializer(self.project_two).data

        new_data = {
            'title': 1234,  # invalid value
            'description': 'New description',
            'category': 'ART',
            'owner_role': 'New Role',
            'desired_roles': [
                'New Role 1',
                'New Role 2',
            ]
        }

        url = reverse('project-detail', kwargs={'project_pk': self.project_two.pk})
        response = self.client.put(url, new_data, format='json')

        # fetch the project from the database after the update
        project_after_update = Project.objects.get(pk=self.project_two.pk)
        project_data_after_update = ProjectSerializer(project_after_update).data

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(project_data_after_update, project_data_before_update)

    def test_update_project_detail_with_invalid_data(self):
        # the authenticated user is the owner of project_one and therefore authorized to update
        project_data_before_update = ProjectSerializer(self.project_one).data

        new_data = {
            'title': 'New Title',
            'description': 'New description',
            'category': 'WRONG_VALUE',  # invalid value
            'owner_role': 'New Role',
            'desired_roles': [
                'New Role 1',
                'New Role 2',
            ]
        }

        url = reverse('project-detail', kwargs={'project_pk': self.project_one.pk})
        response = self.client.put(url, new_data, format='json')

        # fetch the project from the database after the update
        project_after_update = Project.objects.get(pk=self.project_one.pk)
        project_data_after_update = ProjectSerializer(project_after_update).data

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(project_data_after_update, project_data_before_update)

    def test_update_project_detail_with_valid_data(self):
        # the authenticated user is the owner of project_one and therefore authorized to update
        project_data_before_update = ProjectSerializer(self.project_one).data

        new_data = {
            'title': 'New Title',
            'description': 'New description',
            'category': 'ART',
            'owner_role': 'New Role',
            'desired_roles': [
                'New Role 1',
                'New Role 2',
            ]
        }

        url = reverse('project-detail', kwargs={'project_pk': self.project_one.pk})
        response = self.client.put(url, new_data, format='json')

        # fetch the project from the database after the update
        project_after_update = Project.objects.get(pk=self.project_one.pk)
        project_data_after_update = ProjectSerializer(project_after_update).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, project_data_after_update)
        self.assertNotEqual(project_data_after_update, project_data_before_update)

    def test_delete_project_detail_unauthenticated(self):
        # forcefully unauthenticate the requesting user
        self.client.force_authenticate(user=None)

        url = reverse('project-detail', kwargs={'project_pk': self.project_one.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_project_detail_with_invalid_pk(self):
        INVALID_PK = 2500
        url = reverse('project-detail', kwargs={'project_pk': INVALID_PK})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_project_detail_unauthorized(self):
        # the authenticated user is NOT the owner of project_two (i.e. not authorized to delete)

        # attempt to delete another user's project
        url = reverse('project-detail', kwargs={'project_pk': self.project_two.pk})
        response = self.client.delete(url)

        # make sure the project was not deleted
        try:
            Project.objects.get(pk=self.project_two.pk)
        except Project.DoesNotExist:
            self.fail('Project was deleted by an unauthorized user')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_project_detail(self):
        # the authenticated user is the owner of project_one

        # user attempt to delete their own project
        url = reverse('project-detail', kwargs={'project_pk': self.project_one.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # make sure the project has been deleted from the database
        self.assertRaises(Project.DoesNotExist, Project.objects.get, pk=self.project_one.pk)


class FollowListViewTest(APITestCase):
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
            owner = self.user,
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
            owner = self.other_user,
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
            owner = self.other_user,
            owner_role = 'Test Owner Role',
            desired_roles = [
                'Test Role 1',
                'Test Role 2'
            ]
        )
        # requesting user follows two projects
        self.follow_one = Follow.objects.create(
            user = self.user,
            project = self.project_two
        )
        self.follow_two = Follow.objects.create(
            user = self.user,
            project = self.project_four
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

    def test_get_follow_list_unauthenticated(self):
        # forcefully unauthenticate the requesting user
        self.client.force_authenticate(user=None)

        url = reverse('follow-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_follow_list(self):
        # get all project follow instances of the authenticated user
        follows = Follow.objects.filter(Q(user=self.user))
        # serialize the follow instances data
        follows_data = FollowSerializer(follows, many=True).data

        url = reverse('follow-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, follows_data)
    
    def test_create_follow_unauthenticated(self):
        # initial follow count of the authenticated user
        initial_follow_count = Follow.objects.filter(Q(user=self.user)).count()
        # forcefully unauthenticate the requesting user
        self.client.force_authenticate(user=None)

        follow_data = {
            'project': self.project_five.pk
        }

        url = reverse('follow-list')
        response = self.client.post(url, follow_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Follow.objects.filter(Q(user=self.user)).count(), initial_follow_count)

    def test_create_follow_with_invalid_data(self):
        INVALID_PK = 2500
        # initial follow count of the authenticated user
        initial_follow_count = Follow.objects.filter(Q(user=self.user)).count()

        follow_data = {
            'project': INVALID_PK
        }

        url = reverse('follow-list')
        response = self.client.post(url, follow_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Follow.objects.filter(Q(user=self.user)).count(), initial_follow_count)

    def test_create_follow_with_valid_data(self):
        # initial follow count of the authenticated user
        initial_follow_count = Follow.objects.filter(Q(user=self.user)).count()

        follow_data = {
            'project': self.project_five.pk
        }

        url = reverse('follow-list')
        response = self.client.post(url, follow_data, format='json')

        # make sure the project was followed (i.e. follow instance was created)
        try:
            Follow.objects.get(Q(user=self.user) & Q(project=self.project_five))
        except Follow.DoesNotExist:
            self.fail('Follow instance was not created')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Follow.objects.filter(Q(user=self.user)).count(), initial_follow_count + 1)

class FollowDetailViewTest(APITestCase):
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
            owner = self.user,
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
            owner = self.other_user,
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
            owner = self.other_user,
            owner_role = 'Test Owner Role',
            desired_roles = [
                'Test Role 1',
                'Test Role 2'
            ]
        )
        # requesting user follows two projects
        self.follow_one = Follow.objects.create(
            user = self.user,
            project = self.project_two
        )
        self.follow_two = Follow.objects.create(
            user = self.user,
            project = self.project_four
        )
        # other user follows two projects
        self.other_follow_one = Follow.objects.create(
            user = self.other_user,
            project = self.project_one
        )
        self.other_follow_two = Follow.objects.create(
            user = self.other_user,
            project = self.project_three
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

    def test_get_follow_detail_unauthenticated(self):
        # forcefully unauthenticate the requesting user
        self.client.force_authenticate(user=None)

        url = reverse('follow-detail', kwargs={'follow_pk': self.follow_one.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_follow_detail_with_invalid_pk(self):
        INVALID_PK = 2500
        url = reverse('follow-detail', kwargs={'follow_pk': INVALID_PK})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_follow_detail_unauthorized(self):
        # other_follow_one does not belong to the authenticated user
        url = reverse('follow-detail', kwargs={'follow_pk': self.other_follow_one.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_follow_detail(self):
        follow_data = FollowSerializer(self.follow_one).data

        # follow_one belongs to the authenticated user
        url = reverse('follow-detail', kwargs={'follow_pk': self.follow_one.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, follow_data)

    def test_delete_follow_detail_unauthenticated(self):
        # forcefully unauthenticate the requesting user
        self.client.force_authenticate(user=None)

        url = reverse('follow-detail', kwargs={'follow_pk': self.follow_one.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_follow_detail_with_invalid_pk(self):
        INVALID_PK = 2500
        url = reverse('follow-detail', kwargs={'follow_pk': INVALID_PK})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_follow_detail_unauthorized(self):
        # other_follow_one does not belong to the authenticated user

        url = reverse('follow-detail', kwargs={'follow_pk': self.other_follow_one.pk})
        response = self.client.delete(url)

        # make sure the follow instance was not deleted
        try:
            Follow.objects.get(pk=self.other_follow_one.pk)
        except Follow.DoesNotExist:
            self.fail('Follow instance was deleted by an unauthorized user')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_follow_detail(self):
        # follow_one belongs to the authenticated user

        url = reverse('follow-detail', kwargs={'follow_pk': self.follow_one.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # make sure the follow instance has been deleted from the database
        self.assertRaises(Follow.DoesNotExist, Follow.objects.get, pk=self.follow_one.pk)


