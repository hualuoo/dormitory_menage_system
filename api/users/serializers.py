from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import UserModel, UserInfo


class UserRegSerializer(serializers.ModelSerializer):
    """
    用户注册序列化类
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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ("username", "email")


class UserInfoSerializer(serializers.ModelSerializer):
    """
    用户详情序列化类
    """
    user = UserSerializer()

    class Meta:
        model = UserInfo
        fields = "__all__"
        #fields = ("user", "gender", "birthday", "email", "mobile")
