from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import UserModel


class UsersSerializer(serializers.ModelSerializer):
    """
    用户详情序列化类
    """
    class Meta:
        model = UserModel
        fields = ("username", "gender", "birthday", "email", "mobile")


class UserLoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True,
                                     error_messages={
                                         "blank": "请输入验证码",
                                         "required": "请输入验证码",
                                         "max_length": "验证码格式错误",
                                         "min_length": "验证码格式错误"
                                     },
                                     help_text="验证码")


class UserRegSerializer(serializers.ModelSerializer):
    """
    用户详情序列化类
    """
    username = serializers.CharField(label="用户名", help_text="用户名", required=True, allow_blank=False,
                                     validators=[UniqueValidator(queryset=UserModel.objects.all(), message="用户已经存在")])
    password = serializers.CharField(
        style={'input_type': 'password'}, help_text="密码", label="密码", write_only=True,
    )

    def create(self, validated_data):
        user = super(UserRegSerializer, self).create(validated_data=validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user

    class Meta:
        model = UserModel
        fields = ("username", "password")
