from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import serializers

from .models import (Follow, Membership, PrivateMessage, Profile, Project,
                     PublicMessage, Request)


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serialize/deserialize student profiles.
    """

    class Meta:
        model = Profile
        fields = (
            'programme', 'about', 'roles', 
        )

class AccountSerializer(serializers.ModelSerializer):
    """
    Serialize/deserialize student accounts.
    """

    # nested serializer
    profile = ProfileSerializer()

    readonly_fields = (
        'id', 'username', 'email', 'first_name', 'last_name'
    )

    class Meta:
        model = get_user_model()  # a way of getting the default user model without coupling
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'profile',
        )
        read_only_fields = (
            'id', 'username', 'email', 'first_name', 'last_name'
        )

    def update(self, instance, validated_data):
        """
        Updates the profile of a given student account.
        """

        if 'profile' in validated_data:
            new_profile_data = validated_data.pop('profile')

            # get the profile for the instance passed in
            # each student account has an associated profile
            account_profile = instance.profile

            # update with new values if provided, otherwise keep existing values
            account_profile.set_programme(new_profile_data.get('programme', account_profile.programme))
            account_profile.set_about(new_profile_data.get('about', account_profile.about)) 
            account_profile.set_roles(new_profile_data.get('roles', account_profile.roles))

            # save changes to database
            account_profile.save()

        # return the user account instance
        return instance


class MembershipSerializer(serializers.ModelSerializer):
    """
    Serializer for the Membership model.
    """

    user_first_name = serializers.ReadOnlyField(source='user.first_name')
    user_last_name = serializers.ReadOnlyField(source='user.last_name')
    project_title = serializers.ReadOnlyField(source='project.title')

    class Meta:
        model = Membership
        fields = (
            'id', 'role', 'project', 'project_title', 'user', 'user_first_name', 'user_last_name',
        )
        read_only_fields = (
            'id', 'project', 'user', 'user_first_name', 'user_last_name',
        )


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for the Project model.
    Can be used for fetching, creating, and updating Project objects.

    It includes project team members as read-only fields.
    """

    # Returns the human readable version of the category field value
    def get_category_name(self, obj):
        return obj.get_category_display()
    
    # The purpose of this field is to show a human readable version of the category
    category_name = serializers.SerializerMethodField(source='get_category_name')

    # Added to enable viewing of the list of team members when fetching projects
    team_members = MembershipSerializer(many=True, read_only=True)

    owner_first_name = serializers.ReadOnlyField(source='owner.first_name')
    owner_last_name = serializers.ReadOnlyField(source='owner.last_name')

    class Meta:
        model = Project
        fields = (
            'id', 'title', 'description', 'category_name', 'category', 'owner', 'owner_first_name', 'owner_last_name', 'owner_role', 'desired_roles', 'date_created', 'team_members'
        )
        read_only_fields = (
            'id', 'owner', 'owner_first_name', 'owner_last_name', 'date_created', 'category_name'
        )
    
    def create(self, validated_data):
        user = self.context.get('request').user

        project = Project.objects.create(owner=user, **validated_data)
        
        return project


class FollowSerializer(serializers.ModelSerializer):
    """
    Serializer for fetching and creating user follow instances for projects
    """

    user_first_name = serializers.ReadOnlyField(source='user.first_name')
    user_last_name = serializers.ReadOnlyField(source='user.last_name')
    project_title = serializers.ReadOnlyField(source='project.title')

    class Meta:
        model = Follow
        fields = (
            'id', 'user', 'user_first_name', 'user_last_name', 'project', 'project_title'
        )
        read_only_fields = (
            'id', 'user',
        )
    
    def validate(self, data):
        user = self.context['request'].user

        # raise error if the requesting user already follows the project
        follows = Follow.objects.filter(Q(user=user) & Q(project=data['project']))
        if follows.count() > 0:
            raise serializers.ValidationError('You are already following this project')
        
        return data

    def create(self, validated_data):
        user = self.context['request'].user

        follow = Follow.objects.create(user=user, **validated_data)
        
        return follow


class RequestSerializer(serializers.ModelSerializer):
    """
    Serializer for fetching and creating project requests.
    """
    # Returns the human readable version of the status field value
    def get_status_name(self, obj):
        return obj.get_status_display()
    
    # The purpose of this field is to show a human readable version of the category
    status_name = serializers.SerializerMethodField(source='get_status_name')

    requester_first_name = serializers.ReadOnlyField(source='requester.first_name')
    requester_last_name = serializers.ReadOnlyField(source='requester.last_name')
    requestee_first_name = serializers.ReadOnlyField(source='requestee.first_name')
    requestee_last_name = serializers.ReadOnlyField(source='requestee.last_name')
    project_title = serializers.ReadOnlyField(source='project.title')

    class Meta:
        model = Request
        fields = (
            'id', 'requester', 'requester_first_name', 'requester_last_name', 'requestee', 'requestee_first_name','requestee_last_name',
            'project', 'project_title', 'role', 'status_name', 'status', 'is_active', 'date_created',
        )
        read_only_fields = (
            'id', 'requester', 'status_name', 'status', 'is_active', 'date_created',
        )
    
    def validate(self, data):
        # We know that the data passed into this method has gone through individual field validation
        requester = self.context['request'].user
        requestee = data['requestee']
        project = data['project']

        # raise error if there is already an active Request between the requester and requestee for the specified project
        requests = Request.objects.filter(
            (Q(requester=requester) & Q(requestee=requestee) & Q(project=project) & Q(is_active=True)) |
            (Q(requester=requestee) & Q(requestee=requester) & Q(project=project) & Q(is_active=True))
        )
        if requests.count() > 0:
            raise serializers.ValidationError('There is already an active request to or from the requestee for this project')

        # raise error if neither the requester nor the requestee are the project owner
        if not project.is_owner(requester) and not project.is_owner(requestee):
            raise serializers.ValidationError('Requests must be made to or by the project owner')

        # raise error if requester and requestee are the same user
        if requester == requestee:
            raise serializers.ValidationError('You cannot send a request to yourself')

        # raise error if the requester or requestee are a member of the project (project owners cannot be members)
        members = project.team_members.filter(Q(user=requester) | Q(user=requestee))
        if members.count() > 0:
            raise serializers.ValidationError('Member already exists')

        return data
    
    def create(self, validated_data):
        requester = self.context['request'].user

        request = Request.objects.create(requester=requester, **validated_data)
        
        return request


class RequestUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer used specificly for updating project requests.
    """

    # Returns the human readable version of the status field value
    def get_status_name(self, obj):
        return obj.get_status_display()
    
    # The purpose of this field is to show a human readable version of the category
    status_name = serializers.SerializerMethodField(source='get_status_name')

    class Meta:
        model = Request
        fields = (
            'id', 'requester', 'requestee', 'project', 'role', 'status_name', 'status', 'is_active', 'date_created',
        )
        read_only_fields = (
            'id', 'requester', 'requestee', 'project', 'role', 'status_name', 'is_active', 'date_created',
        )

    def validate(self, data):
        # We know that the data passed into this method has gone through individual field validation
        requesting_user = self.context['request'].user
        request_pk = self.context['request_pk']
        project_request = Request.objects.get(pk=request_pk)
        requester = project_request.requester
        requestee = project_request.requestee

        if requesting_user == requester and data['status'] == Request.Status.ACCEPTED:
            raise serializers.ValidationError('You cannot accept your own request')

        if requesting_user == requester and data['status'] == Request.Status.DECLINED:
            raise serializers.ValidationError('You cannot decline your own request')

        if requesting_user == requestee and data['status'] == Request.Status.CANCELLED:
            raise serializers.ValidationError('You cannot cancel another person\'s request')

        return data
    
    def update(self, instance, validated_data):
        new_status = validated_data.get('status')
        instance.status = new_status

        if new_status == Request.Status.ACCEPTED:
            instance.accept()
        elif new_status == Request.Status.DECLINED:
            instance.decline()
        elif new_status == Request.Status.CANCELLED:
            instance.cancel()

        return instance


class PrivateMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for fetching and creating private messages for a particular project.
    """

    user_first_name = serializers.ReadOnlyField(source='user.first_name')
    user_last_name = serializers.ReadOnlyField(source='user.last_name')
    project_title = serializers.ReadOnlyField(source='project.title')

    class Meta:
        model = PrivateMessage
        fields = (
            'id', 'user', 'project', 'project_title', 'date_created', 'user_first_name', 'user_last_name', 'message',
        )
        read_only_fields = (
            'id', 'user', 'project', 'date_created', 'user_first_name', 'user_last_name',
        )

    def create(self, validated_data):
        user = self.context['request'].user
        project = self.context['project']

        private_message = PrivateMessage.objects.create(user=user, project=project, **validated_data)
        
        return private_message

class PublicMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for fetching and creating public messages for a particular project.
    """

    user_first_name = serializers.ReadOnlyField(source='user.first_name')
    user_last_name = serializers.ReadOnlyField(source='user.last_name')
    project_title = serializers.ReadOnlyField(source='project.title')

    class Meta:
        model = PublicMessage
        fields = (
            'id', 'user', 'project', 'project_title', 'date_created', 'user_first_name', 'user_last_name', 'message',
        )
        read_only_fields = (
            'id', 'user', 'project', 'date_created', 'user_first_name', 'user_last_name',
        )

    def create(self, validated_data):
        user = self.context['request'].user
        project = self.context['project']

        public_message = PublicMessage.objects.create(user=user, project=project, **validated_data)
        
        return public_message
