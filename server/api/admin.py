from django.contrib import admin

from .models import Profile, Project, Follow, Membership, Request, PrivateMessage, PublicMessage


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    This class adds the Profile model to the admin panel
    """

    search_fields = ('account', 'programme', 'roles')
    list_filter = ('account', 'programme', 'roles')
    list_display = ('account', 'programme', 'roles')
    
    fieldsets = (
        (None, {
            'fields': (
                'account', 'programme', 'about', 'roles'
            ),
        }),
    )

    add_fieldsets = (
        (None, {
            'fields': ('account', 'programme', 'about', 'roles')
        })
    )


@admin.register(Membership)
class TeamMemberAdmin(admin.ModelAdmin):
    """
    Add the Membership model to the admin panel
    """

    search_fields = ('role', 'project', 'user')
    list_filter = ('role', 'project', 'user')
    list_display = ('id', 'role', 'project', 'user')
    readonly_fields = ('id',)

    fieldsets = (
        (None, {
            'fields': (
                'id', 'role', 'project', 'user'
            ),
        }),
    )

    add_fieldsets = (
        (None, {
            'fields': (
                'role', 'project', 'user'
            ),
        }),
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """
    Add the Project model to the admin panel
    """

    search_fields = ('title', 'category', 'owner')
    list_filter = ('title', 'category', 'owner')
    list_display = ('id', 'title', 'category', 'desired_roles', 'owner')
    readonly_fields = ('id', 'date_created')

    fieldsets = (
        (None, {
            'fields': (
                'id', 'title', 'description','category', 'owner', 'owner_role', 'desired_roles', 'date_created'
            ),
        }),
    )

    add_fieldsets = (
        (None, {
            'fields': (
                'title', 'description','category', 'owner', 'owner_role', 'desired_roles'
            ),
        }),
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """
    Add project followers to the admin panel
    """

    search_fields = ('user', 'project')
    list_filter = ('user', 'project')
    list_display = ('id', 'user', 'project')
    readonly_fields = ('id',)

    fieldsets = (
        (None, {
            'fields': (
                'id', 'user', 'project'
            ),
        }),
    )

    add_fieldsets = (
        (None, {
            'fields': (
                'user', 'project'
            ),
        }),
    )


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    """
    Add the Request model to the admin panel
    """

    search_fields = ('requester', 'requestee', 'project', 'status', 'is_active')
    list_filter = ('requester', 'requestee', 'project', 'status', 'is_active')
    list_display = ('id', 'requester', 'requestee', 'project', 'role', 'status', 'is_active')
    readonly_fields = ('id', 'date_created')

    fieldsets = (
        (None, {
            'fields': (
                'id', 'requester', 'requestee', 'project', 'role', 'status', 'is_active', 'date_created'
            ),
        }),
    )

    add_fieldsets = (
        (None, {
            'fields': (
                'requester', 'requestee', 'project', 'role'
            ),
        }),
    )

@admin.register(PrivateMessage)
class PrivateMessageAdmin(admin.ModelAdmin):
    """
    Add the PrivateMessage model to the admin panel
    """

    search_fields = ('user', 'project', 'message', 'date_created')
    list_filter = ('user', 'project', 'message', 'date_created')
    list_display = ('id', 'user', 'project', 'message', 'date_created')
    readonly_fields = ('id', 'user', 'project', 'date_created')

    fieldsets = (
        (None, {
            'fields': (
                'id', 'user', 'project', 'date_created', 'message',
            ),
        }),
    )

    add_fieldsets = (
        (None, {
            'fields': (
                'message', 'user', 'project',
            ),
        }),
    )

@admin.register(PublicMessage)
class PublicMessageAdmin(admin.ModelAdmin):
    """
    Add the PublicMessage model to the admin panel
    """

    search_fields = ('user', 'project', 'message', 'date_created')
    list_filter = ('user', 'project', 'message', 'date_created')
    list_display = ('id', 'user', 'project', 'message', 'date_created')
    readonly_fields = ('id', 'user', 'project', 'date_created')

    fieldsets = (
        (None, {
            'fields': (
                'id', 'user', 'project', 'date_created', 'message',
            ),
        }),
    )

    add_fieldsets = (
        (None, {
            'fields': (
                'message', 'user', 'project',
            ),
        }),
    )
