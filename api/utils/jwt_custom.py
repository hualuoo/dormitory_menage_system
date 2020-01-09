from users.models import UserModel

from rest_framework import serializers
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from utils.smtp import login_smtp


class CustomBackend(ModelBackend):
    """
    用户自定义用户验证
    """
    def authenticate(self, request, username=None, password=None, **kwargs):# 重写这个函数
        user = UserModel.objects.filter(Q(username=username) | Q(email=username))
        if user.count() == 0:
            raise serializers.ValidationError({'username_error_field': '用户名不存在'})
            return None
        if user[0].is_active == 0:
            raise serializers.ValidationError({'user_error_field': '用户已被禁用'})
            return None
        if user[0].check_password(password):
            if user[0].email is not None:
                # login_smtp(user)
                return user[0]
            return user[0]
        else:
            raise serializers.ValidationError({'password_error_field': '密码错误'})
            return None


def jwt_response_payload_handler(token, user=None, request=None):
    """
        登录成功后自定义返回
    """
    return {
        "username": user.username,
        "is_superuser": user.is_superuser,
        "token": token
    }