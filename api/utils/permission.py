from rest_framework.permissions import BasePermission


class UserIsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser


class UserIsSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj == request.user


class DormitoriesIsSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj == request.user.lived_dormitory


class WaterFeesIsSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj == request.user.lived_dormitory.water_fees


class ElectricityFeesIsSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj == request.user.lived_dormitory.electricity_fees


class FeesLogIsSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj.dormitory == request.user.lived_dormitory


class RepairIsSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj.dormitory == request.user.lived_dormitory


class RepairLogIsSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj.main_repair.dormitory == request.user.lived_dormitory


class AccessControlIsSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj.person == request.user
