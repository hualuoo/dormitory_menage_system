from datetime import datetime

from users.models import User

from rest_framework import serializers
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from utils.smtp import login_smtp


class CustomBackend(ModelBackend):
    """
    用户自定义用户验证
    """
    def authenticate(self, request, username=None, password=None, **kwargs):# 重写这个函数
        user = User.objects.filter(Q(username=username) | Q(email=username))
        if user.count() == 0:
            raise serializers.ValidationError({'detail': '用户名不存在'})
            return None
        last_user = user[0]
        if last_user.is_active == 0:
            raise serializers.ValidationError({'detail': '用户已被禁用'})
            return None
        if last_user.check_password(password):
            last_user.last_login = datetime.now()
            last_user.save()
            if last_user.email is not None:
                # login_smtp(user)
                return last_user
            return last_user
        else:
            raise serializers.ValidationError({'detail': '密码错误'})
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