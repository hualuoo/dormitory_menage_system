from users.models import UserModel

from rest_framework import serializers
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from django.core.mail import send_mail

import datetime

class CustomBackend(ModelBackend):
    """
    用户自定义用户验证
    """
    def authenticate(self, request, username=None, password=None, **kwargs):# 重写这个函数
        user = UserModel.objects.filter(Q(username=username) | Q(email=username))
        if user.count() == 0:
            raise serializers.ValidationError({'username_error_field': '用户名不存在，请检查是否用户名是否输入正确'})
            return None
        if user[0].is_active == 0:
            raise serializers.ValidationError({'user_error_field': '用户已被禁用'})
            return None
        if user[0].check_password(password):
            """
            subject = '主题'  # 主题
            message = '内容'  # 内容
            sender = 'hualuo<i@hualuoo.com>'  # 发送邮箱，已经在settings.py设置，直接导入
            receiver = ['729355791@qq.com']  # 目标邮箱
            now_time = datetime.datetime.now()
            now_time_str = datetime.datetime.strftime(now_time, '%Y-%m-%d %H:%M:%S')
            html_message = '您的账户' + user[0].username + '在' + now_time_str + '登陆成功'   # 发送html格式
            send_mail(subject, message, sender, receiver, html_message=html_message)
            """
            return user[0]
        else:
            raise serializers.ValidationError({'password_error_field': '密码错误，请检查密码是否是输入正确'})
            return None


def jwt_response_payload_handler(token, user=None, request=None):
    """
        登录成功后自定义返回
    """
    return {
        "id": user.id,
        "username": user.username,
        "is_staff": user.is_staff,
        "token": token
    }