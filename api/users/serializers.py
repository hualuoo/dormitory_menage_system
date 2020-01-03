from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from datetime import datetime, timedelta
from .models import UserModel, UserInfo, VerifyCodeModel


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


class VerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, email):
        """
        验证邮箱是否已被使用
        """

        # 邮箱是否注册
        if UserModel.objects.filter(email=email).count():
            raise serializers.ValidationError("该邮箱已被使用")

        # 验证邮箱是否合法
        # EmailField自带验证，无需另外写

        # 验证码发送频率
        one_mintes_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
        if VerifyCodeModel.objects.filter(create_time__gt=one_mintes_ago, email=email).count():
            raise serializers.ValidationError("距离上一次发送未超过一分钟")
        return email
