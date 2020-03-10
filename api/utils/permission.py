from rest_framework.permissions import BasePermission

from users.models import User


class UserIsOwner(BasePermission):
    '''
    def has_permission(self, request, view):
        user = UserModel.objects.filter(id=request.data["user_id"])
        return user[0] == request.user
    '''

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj == request.user


class UserIsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser


class UserIsSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj == request.user