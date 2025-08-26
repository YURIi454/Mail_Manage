from django.contrib import admin

from users.models import CustomUser


@admin.register(CustomUser)
class UsersAdmin(admin.ModelAdmin):

    list_display = ('id', 'email','created_at',)
    list_filter = ('email',)
    search_fields = ('email', 'user_status',)