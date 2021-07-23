from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (Follow, Membership, PrivateMessage, Project,
                     PublicMessage, Request)
from .serializers import (FollowSerializer, MembershipSerializer,
                          PrivateMessageSerializer, AccountSerializer,
                          ProjectSerializer, PublicMessageSerializer,
                          RequestSerializer, RequestUpdateSerializer)


class AccountList(APIView):
    """
    Return a list of all student accounts
    """

    def _search(self, query_param, queryset):
        """
        Helper method for filtering a queryset of accounts
        by a substring in their profile roles.
        
        Returns queryset.
        """
        return queryset.filter(Q(profile__roles__icontains=query_param))

    def _apply_filtering(self, request, queryset):
        """
        Helper method for applying queryset filtering
        as specified in the request's query params.
        
        Available query params:
        
        - search
        
        Returns queryset.
        """

        if 'search' in request.query_params:
            query_param = request.query_params['search']
            queryset = self._search(query_param, queryset)

        return queryset

    def get(self, request, format=None):
        """
        Return a list of all student accounts
        
        ### Response Example
        
        Returns an `"application/json"` encoded list of objects in the following format:

            [
                {
                    "id": 5,
                    "username": "janedoe",
                    "email": "janedoe@fakeuniversity.com",
                    "first_name": "Jane",
                    "last_name": "Doe",
                    "profile": {
                        "programme": "BSc Economics and Business",
                        "about": "Justo laoreet sit amet cursus sit amet.",
                        "roles": [
                            "Financial Planner",
                            "Project Manager"
                        ]
                    }
                },
                {
                    "id": 6,
                    "username": "richardroe",
                    "email": "richardroe@fakeuniversity.com",
                    "first_name": "Richard",
                    "last_name": "Roe",
                    "profile": {
                        "programme": "BA Japanese Studies",
                        "about": "At ultrices mi tempus imperdiet nulla malesuada pellentesque elit eget.",
                        "roles": [
                            "Translator",
                            "Interpreter"
                        ]
                    }
                }
            ]
        
        ### Optional Filters
        
        The list of accounts returned may be filtered by providing query parameters:
        
        1. search
            - a specific substring in the profile roles
        
        **Examples:**
        
        - /api/accounts?search=engineer
        
        ### Response Codes
        
        - 200
            - All accounts returned
        - 401
            - User not authenticated
        """

        accounts = get_user_model().objects.all()

        # check for any query params and filter queryset accordingly
        accounts = self._apply_filtering(request, accounts)

        serializer = AccountSerializer(accounts, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class AccountDetail(APIView):
    """
    Return a specific student account or update a specific profile
    """

    # fetch the user model
    user_account = get_user_model()

    _PROJECT_403_MESSAGE = 'You do not have permission to modify this profile'
    _ACCOUNT_404_MESSAGE = 'No account found with that id'

    def get(self, request, pk, format=None):
        """
        Return a specific student account
        
        ### Response Example
        
        Returns an `"application/json"` encoded object in the following format:

            {
                "id": 5,
                "username": "janedoe",
                "email": "janedoe@fakeuniversity.com",
                "first_name": "Jane",
                "last_name": "Doe",
                "profile": {
                    "programme": "BSc Economics and Business",
                    "about": "Justo laoreet sit amet cursus sit amet.",
                    "roles": [
                        "Financial Planner",
                        "Project Manager"
                    ]
                }
            }
        
        ### Response Codes
        
        - 200
            - Account found and returned
        - 401
            - User not authenticated
        - 404
            - Account not found
        """

        try:
            account = self.user_account.objects.get(pk=pk)
        except self.user_account.DoesNotExist:
            return Response(self._ACCOUNT_404_MESSAGE, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AccountSerializer(account)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, pk, format=None):
        """
        Update and return a specific student profile
        
        Only the profile portion of the student account can be modified
        
        A student can only modify their own profile
        
        ### Request Body
        
        The request body should be a `"application/json"` encoded object in the following format:
        
            {
                "profile": {
                    "programme": "Placeholder Programme",
                    "about": "Placeholder text",
                    "roles": [
                        "Placeholder Role 1",
                        "Placeholder Role 2",
                        "Placeholder Role 3"
                    ]
                }
            }
        
        ### Response Example
        
        Returns an `"application/json"` encoded object in the following format:

            {
                "id": 1,
                "username": "peymanazami",
                "email": "peymanazami@fakeuniversity.com",
                "first_name": "Peyman",
                "last_name": "Azami",
                "profile": {
                    "programme": "BSc Data Science",
                    "about": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                    "roles": [
                        "Software Engineer",
                        "Backend Developer"
                    ]
                }
            }
        
        ### Response Codes
        
        - 200
            - Profile updated
        - 400
            - Invalid field values
        - 401
            - User not authenticated
        - 403
            - User does not have permission
        - 404
            - Account not found
        """

        if (request.user.id != pk):
            return Response(self._PROJECT_403_MESSAGE, status=status.HTTP_403_FORBIDDEN)

        try:
            account = self.user_account.objects.get(pk=pk)
        except self.user_account.DoesNotExist:
            return Response(self._ACCOUNT_404_MESSAGE, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AccountSerializer(account, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()  # save changes to the database

            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProjectList(APIView):
    """
    Return a list of all projects or create and return a new project
    """

    def _search(self, query_param, queryset):
        """
        Helper method for filtering a queryset of projects
        by a substring appearing in the desired roles.

        Returns queryset.
        """
        return queryset.filter(desired_roles__icontains=query_param)

    def _filter_by_relation(self, user, query_param, queryset):
        """
        Helper method for filtering a queryset of projects
        by a specific user's relation to the project.

        Available values:
        - active
        - owned
        - followed

        Returns queryset.
        """
        if query_param == 'active':
            # user is the owner or a member of the project
            queryset = queryset.filter(Q(owner=user) | Q(team_members__user=user)).distinct()
        elif query_param == 'owned':
            # user is the owner of the project
            queryset = queryset.filter(Q(owner=user)).distinct()
        elif query_param == 'followed':
            # user follows the project
            queryset = queryset.filter(Q(followers__user=user)).distinct()
        
        return queryset


    def _order(self, query_param, queryset):
        """
        Helper method for ordering a queryset of projects
        by the date they were created or popularity.

        Available values:
        - ascending
        - descending
        - popularity

        Returns queryset.
        """
        if query_param == 'ascending':
            queryset = queryset.order_by('date_created')
        elif query_param == 'descending':
            queryset = queryset.order_by('-date_created')
        elif query_param == 'popularity':
            # code based on https://docs.djangoproject.com/en/3.1/topics/db/aggregation/#cheat-sheet
            queryset = queryset.annotate(num_followers=Count('followers')).order_by('-num_followers')
        
        return queryset

    def _limit(self, query_param, queryset):
        """
        Helper method for limiting the number of projects
        in a queryset.

        Returns queryset.
        """
        try:
            limit = int(query_param)
        except:
            return queryset
        
        if limit > 0:
            queryset = queryset[:limit]
        
        return queryset

    def _apply_filtering(self, request, queryset):
        """
        Helper method for applying queryset filtering
        as specified in the request's query params.

        Available query params:
        - search
        - relation
        - order
        - limit

        Returns queryset.
        """

        if 'search' in request.query_params:
            query_param = request.query_params['search']
            queryset = self._search(query_param, queryset)

        if 'relation' in request.query_params:
            query_param = request.query_params['relation']
            queryset = self._filter_by_relation(request.user, query_param, queryset)

        if 'order' in request.query_params:
            query_param = request.query_params['order']
            queryset = self._order(query_param, queryset)

        if 'limit' in request.query_params:
            query_param = request.query_params['limit']
            queryset = self._limit(query_param, queryset)

        return queryset
    
    def get(self, request, format=None):
        """
        Return a list of projects

        ### Response Example

        Returns an `"application/json"` encoded list of objects in the following format:

            [
                {
                    "id": 9,
                    "title": "Placeholder Title 1",
                    "description": "Tincidunt lobortis feugiat vivamus at augue.",
                    "category_name": "Film",
                    "category": "FLM",
                    "owner": 10,
                    "owner_first_name": "Jeff",
                    "owner_last_name": "Doe",
                    "owner_role": "Placeholder Role",
                    "desired_roles": [
                        "Placeholder Role 1",
                        "Placeholder Role 2"
                    ],
                    "date_created": "2021-03-11T07:54:39.140852Z",
                    "team_members": []
                },
                {
                    "id": 8,
                    "title": "Placeholder Title 4",
                    "description": "Scelerisque eu ultrices vitae auctor eu augue ut.",
                    "category_name": "Film",
                    "category": "FLM",
                    "owner": 6,
                    "owner_first_name": "Richard",
                    "owner_last_name": "Roe",
                    "owner_role": "Placeholder Role",
                    "desired_roles": [
                        "Placeholder Role 1",
                        "Placeholder Role 2"
                    ],
                    "date_created": "2021-03-11T07:09:13.993362Z",
                    "team_members": [
                        {
                            "id": 17,
                            "role": "Test Role 2",
                            "project": 8,
                            "user": 10,
                            "user_first_name": "Jeff",
                            "user_last_name": "Doe"
                        }
                    ]
                }
            ]
        
        ### Optional Filters

        The list of projects returned may be filtered by providing query parameters:

        1. search
            - a specific substring appearing in the desired roles
        2. relation
            - active - requesting user is the owner or a member
            - owned - requesting user is the owner
            - followed - requesting user is a follower
        3. order
            - ascending - ascending order by date created
            - descending - descending order by date created
            - popularity - descending order by popularity (followers)
        4. limit
            - the max number of projects returned

        **Examples:**

        - /api/projects?search=engineer&order=descending&limit=5
        - /api/projects?search=analyst&order=ascending
        - /api/projects?relation=active
        - /api/projects?order=popular&limit=10

        ### Response Codes

        - 200
            - List of projects returned
        - 401
            - User not authenticated
        """

        projects = Project.objects.all()

        # check for any query params and filter queryset accordingly
        projects = self._apply_filtering(request, projects)
        
        serializer = ProjectSerializer(projects, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        """
        Create and return a new project

        ### Request Body

        The request body should be a `"application/json"` encoded object in the following format:

            {
                "title": "Placeholder Title",
                "description": "Placeholder description",
                "category": "ART",
                "owner_role": "Placeholder Role",
                "desired_roles": [
                    "Placeholder Role 1",
                    "Placeholder Role 2",
                    "..."
                ]
            }

        **Category choices and their codes**

        - Arts = ART
        - Education = EDN
        - Fashion = FSN
        - Film = FLM
        - Finance = FNC
        - Medicine = MCN
        - Software = SFW
        - Sport = SPT
        - Technology = TEC

        ### Response Example

        Returns an `"application/json"` encoded object in the following format:

            {
                "id": 32,
                "title": "Placeholder Title",
                "description": "Placeholder description",
                "category_name": "Arts",
                "category": "ART",
                "owner": 1,
                "owner_first_name": "Peyman",
                "owner_last_name": "Azami",
                "owner_role": "Placeholder Role",
                "desired_roles": [
                    "Placeholder Role 1",
                    "Placeholder Role 2"
                ],
                "date_created": "2021-04-04T10:18:38.123568Z",
                "team_members": []
            }

        ### Response Codes

        - 201
            - New project created and returned
        - 400
            - Invalid field values
        - 401
            - User not authenticated
        """

        serializer = ProjectSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetail(APIView):
    """
    Return, update or delete a specific project
    """

    _PROJECT_404_MESSAGE = 'No project found with that id'
    _PROJECT_403_MESSAGE = 'You do not have permission to modify this project'
    _PROJECT_204_DELETE_SUCCESS_MESSAGE = 'Project successfully deleted'

    def _get_project(self, pk):
        """
        Helper method for fetching a Project object.
        Return object or None.
        """

        try:
            return Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return None
    
    def get(self, request, project_pk, format=None):
        """
        Return a specific project

        ### Response Example

        Returns an `"application/json"` encoded object in the following format:

            {
                "id": 32,
                "title": "Placeholder Title",
                "description": "Placeholder description",
                "category_name": "Arts",
                "category": "ART",
                "owner": 1,
                "owner_first_name": "Peyman",
                "owner_last_name": "Azami",
                "owner_role": "Placeholder Role",
                "desired_roles": [
                    "Placeholder Role 1",
                    "Placeholder Role 2"
                ],
                "date_created": "2021-04-04T10:18:38.123568Z",
                "team_members": []
            }

        ### Response Codes

        - 200
            - Project found and returned
        - 401
            - User not authenticated
        - 404
            - Project not found
        """

        project = self._get_project(pk=project_pk)

        if not project:
            return Response(self._PROJECT_404_MESSAGE, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProjectSerializer(project)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, project_pk, format=None):
        """
        Update and return a specific project

        User must be the owner of the project to update

        ### Request Body

        The request body should be a `"application/json"` encoded object in the following format:

            {
                "title": "Placeholder Title",
                "description": "Placeholder description",
                "category": "ART",
                "owner_role": "Placeholder Role",
                "desired_roles": [
                    "Placeholder Role 1",
                    "Placeholder Role 2",
                    "..."
                ]
            }

        **Category choices and their codes**

        - Arts = ART
        - Education = EDN
        - Fashion = FSN
        - Film = FLM
        - Finance = FNC
        - Medicine = MCN
        - Software = SFW
        - Sport = SPT
        - Technology = TEC


        ### Response Example

        Returns an `"application/json"` encoded object in the following format:

            {
                "id": 31,
                "title": "Placeholder Title",
                "description": "Updated description",
                "category_name": "Arts",
                "category": "ART",
                "owner": 1,
                "owner_first_name": "Peyman",
                "owner_last_name": "Azami",
                "owner_role": "Placeholder Role",
                "desired_roles": [
                    "Placeholder Role 1",
                    "Placeholder Role 2"
                ],
                "date_created": "2021-04-04T08:23:43.639554Z",
                "team_members": []
            }


        ### Response Codes

        - 200
            - Project found, updated, and returned
        - 400
            - Invalid field values
        - 401
            - User not authenticated
        - 403
            - User does not have permission
        - 404
            - Project not found
        """

        project = self._get_project(pk=project_pk)

        if not project:
            return Response(self._PROJECT_404_MESSAGE, status=status.HTTP_404_NOT_FOUND)
        
        if not project.is_owner(request.user):
            return Response(self._PROJECT_403_MESSAGE, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ProjectSerializer(project, data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, project_pk, format=None):
        """
        Delete a specific project

        User must be the owner of the project to delete

        ### Response Codes

        - 204
            - Project deleted
        - 401
            - User not authenticated
        - 403
            - User does not have permission
        - 404
            - Project not found
        """

        project = self._get_project(pk=project_pk)

        if not project:
            return Response(self._PROJECT_404_MESSAGE, status=status.HTTP_404_NOT_FOUND)
        
        if not project.is_owner(request.user):
            return Response(self._PROJECT_403_MESSAGE, status=status.HTTP_403_FORBIDDEN)
        
        project.delete()
        
        return Response(self._PROJECT_204_DELETE_SUCCESS_MESSAGE, status=status.HTTP_204_NO_CONTENT)


class FollowList(APIView):
    """
    Return a list of the authenticated user's current follow instances for projects or create a new instance
    """

    _FOLLOW_200_SUCCESS = 'Project successfully followed'
    
    def get(self, request, format=None):
        """
        Return a list of the authenticated user's current follow instances for projects

        ### Response Example

        Returns an `"application/json"` encoded list of objects in the following format:

            [
                {
                    "id": 42,
                    "user": 1,
                    "user_first_name": "Peyman",
                    "user_last_name": "Azami",
                    "project": 9,
                    "project_title": "Placeholder Title 3"
                },
                {
                    "id": 44,
                    "user": 1,
                    "user_first_name": "Peyman",
                    "user_last_name": "Azami",
                    "project": 8,
                    "project_title": "Placeholder Title 4"
                }
            ]

        ### Response Codes

        - 200
            - All of the user's follow instances are returned
        - 401
            - User not authenticated
        """

        follows = Follow.objects.filter(Q(user=request.user))
        serializer = FollowSerializer(follows, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        """
        Create a new follow instance for a project

        ### Request Body

        The request body should be a `"application/json"` encoded object in the following format:

            {
                "project": 6
            }

        ### Response Example

        Returns an `"application/json"` encoded object in the following format:

            {
                "id": 51,
                "user": 1,
                "user_first_name": "Peyman",
                "user_last_name": "Azami",
                "project": 6,
                "project_title": "Placeholder Title 6"
            }

        ### Response Codes

        - 201
            - New follow instance created
        - 400
            - Invalid field values
        - 401
            - User not authenticated
        """

        serializer = FollowSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FollowDetail(APIView):
    """
    Return or delete a project follow instance

    Each user can only access or delete their own follow instances
    """

    _FOLLOW_204_DELETE_SUCCESS_MESSAGE = 'Project successfully unfollowed'
    _FOLLOW_403_MESSAGE = 'You do not have permission to view or modify this follow instance'
    _FOLLOW_404_MESSAGE = 'No follow instance found with that id'

    def get(self, request, follow_pk, format=None):
        """
        Return a project follow instance

        Each user can only access their own follow instances

        ### Response Example

        Returns an `"application/json"` encoded object in the following format:

            {
                "id": 51,
                "user": 1,
                "user_first_name": "Peyman",
                "user_last_name": "Azami",
                "project": 6,
                "project_title": "Placeholder Title 6"
            }

        ### Response Codes

        - 200
            - Follow instance found and returned
        - 401
            - User not authenticated
        - 403
            - User does not have permission
        """

        try:
            follow = Follow.objects.get(pk=follow_pk)
        except Follow.DoesNotExist:
            return Response(self._FOLLOW_404_MESSAGE, status=status.HTTP_404_NOT_FOUND)

        if request.user != follow.user:
            return Response(self._FOLLOW_403_MESSAGE, status=status.HTTP_403_FORBIDDEN)

        serializer = FollowSerializer(follow)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, follow_pk, format=None):
        """
        Delete a project follow instance

        Each user can only delete their own follow instances

        ### Response Codes

        - 204
            - Follow instance deleted
        - 401
            - User not authenticated
        - 403
            - User does not have permission
        - 404
            - Follow instance not found
        """

        try:
            follow = Follow.objects.get(pk=follow_pk)
        except Follow.DoesNotExist:
            return Response(self._FOLLOW_404_MESSAGE, status=status.HTTP_404_NOT_FOUND)
        
        if request.user != follow.user:
            return Response(self._FOLLOW_403_MESSAGE, status=status.HTTP_403_FORBIDDEN)
        
        follow.delete()

        return Response(self._FOLLOW_204_DELETE_SUCCESS_MESSAGE, status=status.HTTP_204_NO_CONTENT)


class MembershipList(APIView):
    """
    Return a list of the authenticated user's project memberships
    """

    def get(self, request, format=None):
        """
        Return a list of the authenticated user's project memberships

        ### Response Example

        Returns an `"application/json"` encoded list of objects in the following format:

            [
                {
                    "id": 31,
                    "role": "Software Engineer",
                    "project": 29,
                    "project_title": "Placeholder Title 29",
                    "user": 1,
                    "user_first_name": "Peyman",
                    "user_last_name": "Azami"
                },
                {
                    "id": 36,
                    "role": "Frontend Developer",
                    "project": 9,
                    "project_title": "Placeholder Title 36",
                    "user": 1,
                    "user_first_name": "Peyman",
                    "user_last_name": "Azami"
                }
            ]

        ### Response Codes

        - 200
            - All of the user's project memberships returned
        - 401
            - User not authenticated
        """
        memberships = Membership.objects.filter(user=request.user)
        serializer = MembershipSerializer(memberships, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class MembershipDetail(APIView):
    """
    Return, update, or delete a project membership
    """

    _MEMBERSHIP_404_MESSAGE = 'No membership found with that id'
    _MEMBERSHIP_403_MESSAGE = 'You do not have permission to modify this membership'
    _MEMBERSHIP_204_DELETE_SUCCESS_MESSAGE = 'Membership successfully deleted'

    def _get_membership(self, pk):
        """
        Helper method for fetching memberships.
        Return membership object or None.
        """
        try:
            return Membership.objects.get(pk=pk)
        except Membership.DoesNotExist:
            return None

    def get(self, request, membership_pk, format=None):
        """
        Return a project membership

        ### Response Example

        Returns an `"application/json"` encoded object in the following format:

            {
                "id": 31,
                "role": "Software Engineer",
                "project": 29,
                "project_title": "Placeholder Title 29",
                "user": 1,
                "user_first_name": "Peyman",
                "user_last_name": "Azami"
            }

        ### Response Codes

        - 200
            - Membership found and returned
        - 401
            - User not authenticated
        - 404
            - Membership not found
        """

        membership = self._get_membership(pk=membership_pk)

        if not membership:
            return Response(self._MEMBERSHIP_404_MESSAGE, status=status.HTTP_404_NOT_FOUND)
        
        serializer = MembershipSerializer(membership)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, membership_pk, format=None):
        """
        Update a project membership

        The membership may be updated only by the project owner
        
        ### Request Body

        The request body should be a `"application/json"` encoded object in the following format:

            {
                "role": "Placeholder Role"
            }

        ### Response Example

        Returns an `"application/json"` encoded object in the following format:

            {
                "id": 21,
                "role": "Designer",
                "project": 20,
                "project_title": "Placeholder Title 20",
                "user": 9,
                "user_first_name": "Kyle",
                "user_last_name": "Doe"
            }

        ### Response Codes

        - 200
            - Membership updated and returned
        - 400
            - Invalid field values
        - 401
            - User not authenticated
        - 403
            - User does not have permission
        - 404
            - Membership not found
        """

        membership = self._get_membership(pk=membership_pk)

        if not membership:
            return Response(self._MEMBERSHIP_404_MESSAGE, status=status.HTTP_404_NOT_FOUND)

        # only the project owner may modify member details
        if not membership.project.is_owner(request.user):
            return Response(self._MEMBERSHIP_403_MESSAGE, status=status.HTTP_403_FORBIDDEN)
        
        serializer = MembershipSerializer(membership, data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request, membership_pk, format=None):
        """
        Delete a project membership

        The membership may be deleted only by the member or the project owner

        ### Response Codes

        - 204
            - Membership deleted
        - 401
            - User not authenticated
        - 403
            - User does not have permission
        - 404
            - Membership not found
        """

        membership = self._get_membership(pk=membership_pk)

        if not membership:
            return Response(self._MEMBERSHIP_404_MESSAGE, status=status.HTTP_404_NOT_FOUND)

        # membership can only be removed if the requester is the project owner or the member being removed
        if not membership.project.is_owner(request.user) and request.user != membership.user:
            return Response(self._MEMBERSHIP_403_MESSAGE, status=status.HTTP_403_FORBIDDEN)
        
        membership.delete()
        
        return Response(self._MEMBERSHIP_204_DELETE_SUCCESS_MESSAGE, status=status.HTTP_204_NO_CONTENT)


class RequestList(APIView):
    """
    Return a list of the authenticated user's active project requests or create a new project request
    """

    def get(self, request, format=None):
        """
        Return a list of the authenticated user's active project requests

        ### Response Example

        Returns an `"application/json"` encoded list of objects in the following format:

            [
                {
                    "id": 18,
                    "requester": 1,
                    "requester_first_name": "Peyman",
                    "requester_last_name": "Azami",
                    "requestee": 5,
                    "requestee_first_name": "Jane",
                    "requestee_last_name": "Doe",
                    "project": 18,
                    "project_title": "Calamity",
                    "role": "Financial Planner",
                    "status_name": "Pending",
                    "status": "PND",
                    "is_active": true,
                    "date_created": "2021-04-03T12:08:00.607192Z"
                },
                {
                    "id": 27,
                    "requester": 1,
                    "requester_first_name": "Peyman",
                    "requester_last_name": "Azami",
                    "requestee": 8,
                    "requestee_first_name": "Jennifer",
                    "requestee_last_name": "Roe",
                    "project": 18,
                    "project_title": "Calamity",
                    "role": "Test Role",
                    "status_name": "Pending",
                    "status": "PND",
                    "is_active": true,
                    "date_created": "2021-04-04T07:44:19.392459Z"
                }
            ]

        ### Response Codes

        - 200
            - All of the user's project requests returned
        - 401
            - User not authenticated
        """

        requests = Request.objects.filter((Q(requester=request.user.id) | Q(requestee=request.user.id)) & Q(is_active=True))

        serializer = RequestSerializer(requests, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, format=None):
        """
        Create and return a new project request

        ### Request Body

        The request body should be a `"application/json"` encoded object in the following format:

            {
                "requestee": 6,
                "project": 32,
                "role": "Placeholder Role"
            }

        ### Response Example

        Returns an `"application/json"` encoded object in the following format:

            {
                "id": 32,
                "requester": 1,
                "requester_first_name": "Peyman",
                "requester_last_name": "Azami",
                "requestee": 6,
                "requestee_first_name": "Richard",
                "requestee_last_name": "Roe",
                "project": 32,
                "project_title": "Placeholder Title",
                "role": "Placeholder Role",
                "status_name": "Pending",
                "status": "PND",
                "is_active": true,
                "date_created": "2021-04-04T13:23:37.907620Z"
            }
        
        ### Response Codes

        - 201
            - New project request created and returned
        - 400
            - Invalid field values
        - 401
            - User not authenticated
        """

        serializer = RequestSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED) 
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RequestDetail(APIView):
    """
    Return or update an active project request of the authenticated user
    """

    _PROJ_REQ_404_MESSAGE = 'A project request does not exist with that id'
    _PROJ_REQ_403_MESSAGE = 'You do not have permission to access this project request'
    _PROJ_REQ_200_SUCCESS = 'Request update was successful'
    
    def get(self, request, request_pk, format=None):
        """
        Return an active project request of the authenticated user

        ### Response Example

        Returns an `"application/json"` encoded object in the following format:

            {
                "id": 32,
                "requester": 1,
                "requester_first_name": "Peyman",
                "requester_last_name": "Azami",
                "requestee": 6,
                "requestee_first_name": "Richard",
                "requestee_last_name": "Roe",
                "project": 32,
                "project_title": "Placeholder Title",
                "role": "Placeholder Role",
                "status_name": "Pending",
                "status": "PND",
                "is_active": true,
                "date_created": "2021-04-04T13:23:37.907620Z"
            }

        ### Response Codes

        - 200
            - Project request found and returned
        - 401
            - User not authenticated
        - 403
            - User does not have permission
        - 404
            - Project request not found or not active
        """

        try:
            proj_request = Request.objects.get(pk=request_pk)
        except Request.DoesNotExist:
            return Response(self._PROJ_REQ_404_MESSAGE, status=status.HTTP_404_NOT_FOUND)
        
        if not proj_request.is_active:
            return Response(self._PROJ_REQ_404_MESSAGE, status=status.HTTP_404_NOT_FOUND)
        
        if request.user != proj_request.requester and request.user != proj_request.requestee:
            return Response(self._PROJ_REQ_403_MESSAGE, status=status.HTTP_403_FORBIDDEN)
        
        serializer = RequestSerializer(proj_request)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, request_pk, format=None):
        """
        Update an active project request of the authenticated user

        Updating a project request consists of accepting, declining, or cancelling

        A user can accept or decline a request sent to them by another user

        A user can cancel a request they sent to another user

        ### Request Body

        The request body should be a `"application/json"` encoded object in the following format:

            {
                "status": "ACP"
            }

        **Status choices and their codes**

        - Pending = PND
        - Accepted = ACP
        - Declined = DCN
        - Cancelled = CNL

        ### Response Codes

        - 200
            - Project request updated
        - 400
            - Invalid field values
        - 401
            - User not authenticated
        - 403
            - User does not have permission
        - 404
            - Project request not found
        """

        try:
            proj_request = Request.objects.get(pk=request_pk)
        except Request.DoesNotExist:
            return Response(self._PROJ_REQ_404_MESSAGE, status=status.HTTP_404_NOT_FOUND)
        
        if not proj_request.is_active:
            return Response(self._PROJ_REQ_404_MESSAGE, status=status.HTTP_404_NOT_FOUND)
        
        if request.user != proj_request.requester and request.user != proj_request.requestee:
            return Response(self._PROJ_REQ_403_MESSAGE, status=status.HTTP_403_FORBIDDEN)
        
        serializer = RequestUpdateSerializer(proj_request, data=request.data, context={'request': request, 'request_pk': request_pk})

        if serializer.is_valid():
            serializer.save()

            return Response(self._PROJ_REQ_200_SUCCESS, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PrivateMessageList(APIView):
    """
    Return a list of the 30 latest private messages for a specific project in ascending order, or create and return a new private message
    """

    _PROJECT_404_MESSAGE = 'A project does not exist with that id'
    _PROJ_MSG_403_MESSAGE = 'You do not have permission to access the private messages for this project'
    
    def get(self, request, project_pk, format=None):
        """
        Return a list of private messages for a particular project in ascending order

        ### Response Example

        Returns an `"application/json"` encoded list of objects in the following format:

            [
                {
                    "id": 1,
                    "user": 1,
                    "project": 20,
                    "project_title": "Placeholder Title 20",
                    "date_created": "2021-04-22T09:08:18.605470+01:00",
                    "user_first_name": "Peyman",
                    "user_last_name": "Azami",
                    "message": "Hello team!"
                },
                {
                    "id": 2,
                    "user": 8,
                    "project": 20,
                    "project_title": "Placeholder Title 20",
                    "date_created": "2021-04-22T09:09:21.473677+01:00",
                    "user_first_name": "Jennifer",
                    "user_last_name": "Roe",
                    "message": "Hi there!"
                }
            ]

        ### Response Codes

        - 200
            - All private messages for the project were returned
        - 401
            - User not authenticated
        - 403
            - User does not have permission
        - 404
            - Project not found
        """

        try:
            project = Project.objects.get(pk=project_pk)
        except Project.DoesNotExist:
            return Response(self._PROJECT_404_MESSAGE, status=status.HTTP_404_NOT_FOUND)
        
        # requesting user is NOT the owner or a member of the project
        if not (project.is_owner(request.user) or project.team_members.filter(user=request.user)):
            return Response(self._PROJ_MSG_403_MESSAGE, status=status.HTTP_403_FORBIDDEN)

        private_messages = PrivateMessage.objects.filter(project=project)

        serializer = PrivateMessageSerializer(private_messages, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, project_pk, format=None):
        """
        Create and return a new private message for a particular project

        ### Request Body

        The request body should be a `"application/json"` encoded object in the following format:

            {
                "message": "Hello team!"
            }

        ### Response Example

        Returns an `"application/json"` encoded object in the following format:

            {
                "id": 3,
                "user": 1,
                "project": 20,
                "project_title": "Placeholder Title 20",
                "date_created": "2021-04-22T09:19:02.660599+01:00",
                "user_first_name": "Peyman",
                "user_last_name": "Azami",
                "message": "Hello team!"
            }

        ### Response Codes

        - 201
            - New public message created and returned
        - 400
            - Invalid field values
        - 401
            - User not authenticated
        - 403
            - User does not have permission
        - 404
            - Project not found
        """

        try:
            project = Project.objects.get(pk=project_pk)
        except Project.DoesNotExist:
            return Response(self._PROJECT_404_MESSAGE, status=status.HTTP_404_NOT_FOUND)
        
        # requesting user is NOT the owner or a member of the project
        if not (project.is_owner(request.user) or project.team_members.filter(user=request.user)):
            return Response(self._PROJ_MSG_403_MESSAGE, status=status.HTTP_403_FORBIDDEN)

        serializer = PrivateMessageSerializer(data=request.data, context={'request': request, 'project': project})

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PrivateMessageDetail(APIView):
    """
    Return a private message for a specific project
    """

    _PROJECT_404_MESSAGE = 'A project does not exist with that id'
    _PROJ_MSG_404_MESSAGE = 'A message does not exist with that id'
    _PROJ_MSG_403_MESSAGE = 'You do not have permission to access this message'
    
    def get(self, request, project_pk, message_pk, format=None):
        """
        Return a private message for a particular project

        ### Response Example

        Returns an `"application/json"` encoded object in the following format:

            {
                "id": 1,
                "user": 1,
                "project": 20,
                "project_title": "Placeholder Title 20",
                "date_created": "2021-04-22T09:08:18.605470+01:00",
                "user_first_name": "Peyman",
                "user_last_name": "Azami",
                "message": "Hello team!"
            }

        ### Response Codes

        - 200
            - Private message found and returned
        - 401
            - User not authenticated
        - 403
            - User does not have permission
        - 404
            - Project or message not found
        """

        try:
            project = Project.objects.get(pk=project_pk)
        except Project.DoesNotExist:
            return Response(self._PROJECT_404_MESSAGE, status=status.HTTP_404_NOT_FOUND)
        
        # requesting user is NOT the owner or a member of the project
        if not (project.is_owner(request.user) or project.team_members.filter(user=request.user)):
            return Response(self._PROJ_MSG_403_MESSAGE, status=status.HTTP_403_FORBIDDEN)

        try:
            message = PrivateMessage.objects.get(pk=message_pk)
        except PrivateMessage.DoesNotExist:
            return Response(self._PROJ_MSG_404_MESSAGE, status=status.HTTP_404_NOT_FOUND)

        serializer = PrivateMessageSerializer(message)

        return Response(serializer.data, status=status.HTTP_200_OK)
  


class PublicMessageList(APIView):
    """
    Return a list of messages for a specific project in ascending order, or create and return a new public message
    """

    _PROJECT_404_MESSAGE = 'A project does not exist with that id'
    
    def get(self, request, project_pk, format=None):
        """
        Return a list of public messages for a particular project in ascending order

        ### Response Example

        Returns an `"application/json"` encoded list of objects in the following format:

            [
                {
                    "id": 1,
                    "user": 8,
                    "project": 20,
                    "project_title": "Placeholder Title 20",
                    "date_created": "2021-04-22T09:10:16.266090+01:00",
                    "user_first_name": "Jennifer",
                    "user_last_name": "Roe",
                    "message": "Hi everyone!"
                },
                {
                    "id": 2,
                    "user": 9,
                    "project": 20,
                    "project_title": "Placeholder Title 20",
                    "date_created": "2021-04-22T09:13:59.375964+01:00",
                    "user_first_name": "Kyle",
                    "user_last_name": "Doe",
                    "message": "Hi there! This project sounds interesting."
                }
            ]

        ### Response Codes

        - 200
            - All public messages for the project were returned
        - 401
            - User not authenticated
        - 404
            - Project not found
        """

        try:
            project = Project.objects.get(pk=project_pk)
        except Project.DoesNotExist:
            return Response(self._PROJECT_404_MESSAGE, status=status.HTTP_404_NOT_FOUND)

        public_messages = PublicMessage.objects.filter(project=project)

        serializer = PublicMessageSerializer(public_messages, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, project_pk, format=None):
        """
        Create and return a new public message for a particular project

        ### Request Body

        The request body should be a `"application/json"` encoded object in the following format:

            {
                "message": "Great project idea!"
            }

        ### Response Example

        Returns an `"application/json"` encoded object in the following format:

            {
                "id": 1,
                "user": 8,
                "project": 20,
                "project_title": "Placeholder Title 20",
                "date_created": "2021-04-22T09:10:16.266090+01:00",
                "user_first_name": "Jennifer",
                "user_last_name": "Roe",
                "message": "Great project idea!"
            }

        ### Response Codes

        - 201
            - New public message created and returned
        - 400
            - Invalid field values
        - 401
            - User not authenticated
        - 404
            - Project not found
        """

        try:
            project = Project.objects.get(pk=project_pk)
        except Project.DoesNotExist:
            return Response(self._PROJECT_404_MESSAGE, status=status.HTTP_404_NOT_FOUND)

        serializer = PublicMessageSerializer(data=request.data, context={'request': request, 'project': project})

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PublicMessageDetail(APIView):
    """
    Return a public message for a specific project
    """

    _PROJECT_404_MESSAGE = 'A project does not exist with that id'
    _PROJ_MSG_404_MESSAGE = 'A message does not exist with that id'
    
    def get(self, request, project_pk, message_pk, format=None):
        """
        Return a public message for a particular project

        ### Response Example

        Returns an `"application/json"` encoded object in the following format:

            {
                "id": 2,
                "user": 9,
                "project": 20,
                "project_title": "Placeholder Title 20",
                "date_created": "2021-04-22T09:13:59.375964+01:00",
                "user_first_name": "Kyle",
                "user_last_name": "Doe",
                "message": "Hi there! This project sounds interesting."
            }

        ### Response Codes

        - 200
            - Public message found and returned
        - 401
            - User not authenticated
        - 404
            - Project or message not found
        """

        try:
            project = Project.objects.get(pk=project_pk)
        except Project.DoesNotExist:
            return Response(self._PROJECT_404_MESSAGE, status=status.HTTP_404_NOT_FOUND)

        try:
            message = PublicMessage.objects.get(pk=message_pk)
        except PublicMessage.DoesNotExist:
            return Response(self._PROJ_MSG_404_MESSAGE, status=status.HTTP_404_NOT_FOUND)

        serializer = PublicMessageSerializer(message)

        return Response(serializer.data, status=status.HTTP_200_OK)
