from rest_framework.permissions import BasePermission


class UserIsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj == request.user


class UserInfoIsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        print(obj.user == request.user)
        return obj.user == request.user
