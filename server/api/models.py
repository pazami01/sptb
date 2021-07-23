from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """
    The profile for a student account.
    """

    # Each profile is associated with a single account and vice versa
    account = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile', on_delete=models.CASCADE)
    # Optional fields
    programme = models.CharField(max_length=150, blank=True)
    about = models.TextField(max_length=1000, blank=True)
    roles = ArrayField(models.CharField(max_length=40, blank=True), size=3, default=list, blank=True)

    def __str__(self):
        return self.account.username
    
    def set_programme(self, programme):
        self.programme = programme

    def set_about(self, about):
        self.about = about

    def set_roles(self, roles):
        self.roles = roles


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_account_profile(sender, instance, created, **kwargs):
    """
    Each time a student account is created, a profile is also created and associated with that account.
    """
    if created:
        Profile.objects.create(account=instance)


class Project(models.Model):
    """
    Model for projects.
    """

    class Category(models.TextChoices):
        """
        Represents the categories a project can have, a long with their code
        and a human readable representation.
        """
        ARTS = ('ART', 'Arts')
        EDUCATION = ('EDN', 'Education')
        FASHION = ('FSN', 'Fashion')
        FILM = ('FLM', 'Film')
        FINANCE = ('FNC', 'Finance')
        MEDICINE = ('MCN', 'Medicine')
        SOFTWARE = ('SFW', 'Software')
        SPORT = ('SPT', 'Sport')
        TECHNOLOGY = ('TEC', 'Technology')

    title = models.CharField(max_length=150)
    description = models.TextField(max_length=3000, blank=True)
    category = models.CharField(max_length=3, choices=Category.choices)
    # A project has a single user as the owner, but a user may be the owner of many projects
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='owned_projects', on_delete=models.CASCADE)
    owner_role = models.CharField(max_length=40)
    desired_roles = ArrayField(models.CharField(max_length=40, blank=True), size=10, default=list, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    def is_owner(self, user):
        return user and user == self.owner


class Follow(models.Model):
    """
    Model for users following projects.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='project_follows', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, related_name='followers', on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Membership(models.Model):
    """
    Model for team members within projects.
    """

    role = models.CharField(max_length=40)
    # A project team member must be assigned to a single project, but a project may have many project team members
    project = models.ForeignKey(Project, related_name='team_members', on_delete=models.CASCADE)
    # A project team member must be linked to a single user, but a user may be a team member of many projects
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='project_teams', on_delete=models.CASCADE)

    def __str__(self):
        return self.role
    

class Request(models.Model):
    """
    Model for inviting/requesting users to join projects as team members.
    """

    class Status(models.TextChoices):
        """
        Represents the states a project request can have, a long with their code
        and a human readable representation.
        """
        PENDING = ('PND', 'Pending')
        ACCEPTED = ('ACP', 'Accepted')
        DECLINED = ('DCN', 'Declined')
        CANCELLED = ('CNL', 'Cancelled')

    # Each request is sent by a single user, but a user may send many requests
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_project_requests')
    # Each request is received by a single user, but a user may receive many requests
    requestee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_project_requests')
    # Each request is for joining a single project, but a project may have many join requests
    project = models.ForeignKey(Project, related_name='requests', on_delete=models.CASCADE)
    # The role the user will take in the project
    role = models.CharField(max_length=40)
    status = models.CharField(max_length=3, choices=Status.choices, default=Status.PENDING)
    # inactive requests should not be manipulated
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.requester.first_name} {self.requester.last_name}'

    def cancel(self):
        """
        Cancels the project request and makes it inactive
        """

        self.status = self.Status.CANCELLED
        self.is_active = False
        self.save()
    
    def decline(self):
        """
        Declines the project request and makes it inactive.
        """

        self.status = self.Status.DECLINED
        self.is_active = False
        self.save()
        
    def accept(self):
        """
        Accepts the project request.
        Creates a new member and adds it to the project.
        Makes the request inactive.
        """

        # The new member to be added is the one that is not the owner of the project
        new_member = self.requestee if self.project.is_owner(self.requester) else self.requester

        # Add the new member to the project
        Membership.objects.create(
            role=self.role,
            project=self.project,
            user=new_member
        )

        self.status = self.Status.ACCEPTED
        self.is_active = False
        self.save()


class PrivateMessage(models.Model):
    """
    Model for private messages associated with a specific project
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='private_messages', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, related_name='private_messages', on_delete=models.CASCADE)
    message = models.CharField(max_length=1000)
    date_created = models.DateTimeField(auto_now_add=True)


class PublicMessage(models.Model):
    """
    Model for public messages associated with a specific project
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='public_messages', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, related_name='public_messages', on_delete=models.CASCADE)
    message = models.CharField(max_length=1000)
    date_created = models.DateTimeField(auto_now_add=True)

