from django.urls import path
from rest_framework.documentation import include_docs_urls

from .views import (AccountDetail, AccountList, FollowDetail, FollowList,
                    MembershipDetail, MembershipList, PrivateMessageDetail,
                    PrivateMessageList, ProjectDetail, ProjectList,
                    PublicMessageDetail, PublicMessageList, RequestDetail,
                    RequestList)

urlpatterns = [
    path('', include_docs_urls(
        title='Student Project Team Builder API',
        description='Welcome to the Student Project Team Builder API. You must be registered on the system and acquire a JWT access token with your credentials. The token must be included in the authorization header with the type "Bearer" when you make a request.',
        public=False
    )),

    path('accounts/', AccountList.as_view(), name='account-list'),
    path('accounts/<int:pk>/', AccountDetail.as_view(), name='account-detail'),

    path('projects/', ProjectList.as_view(), name='project-list'),
    path('projects/<int:project_pk>/', ProjectDetail.as_view(), name='project-detail'),

    path('projects/<int:project_pk>/private-messages/', PrivateMessageList.as_view(), name='project-private-messages-list'),
    path('projects/<int:project_pk>/private-messages/<int:message_pk>/', PrivateMessageDetail.as_view(), name='project-private-messages-detail'),

    path('projects/<int:project_pk>/public-messages/', PublicMessageList.as_view(), name='project-public-messages-list'),
    path('projects/<int:project_pk>/public-messages/<int:message_pk>/', PublicMessageDetail.as_view(), name='project-public-messages-detail'),

    path('memberships/', MembershipList.as_view(), name='membership-list'),
    path('memberships/<int:membership_pk>/', MembershipDetail.as_view(), name='membership-detail'),

    path('requests/', RequestList.as_view(), name='request-list'),
    path('requests/<int:request_pk>/', RequestDetail.as_view(), name='request-detail'),

    path('follows/', FollowList.as_view(), name='follow-list'),
    path('follows/<int:follow_pk>/', FollowDetail.as_view(), name='follow-detail'),
]

