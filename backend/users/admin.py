from django.contrib import admin

from .models import Follow, User


class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'email', 'username',
                    'password', 'first_name', 'last_name',
                    'is_staff')
    search_fields = ('email', 'name')
    list_filter = ('first_name', )
    empty_value_display = '-empty-'


class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    search_fields = ('user',)
    list_filter = ('user', )
    empty_value_display = '-empty-'


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
