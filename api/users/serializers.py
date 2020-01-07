from random import choice
from datetime import datetime, timedelta
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from utils import smtp
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


class ChangePasswordSerializer(serializers.ModelSerializer):
    """
    用户密码修改序列类
    """
    username = serializers.CharField(read_only=True)
    code = serializers.CharField(required=True, write_only=True, max_length=6, min_length=6, label="验证码",
                                 error_messages={
                                     "blank": "请输入验证码",
                                     "required": "请输入验证码",
                                     "max_length": "验证码格式错误",
                                     "min_length": "验证码格式错误"
                                 },
                                 help_text="验证码")
    old_password = serializers.CharField(required=True, write_only=True, max_length=16, min_length=6, label="旧密码",
                                         error_messages={
                                             "blank": "请输入旧密码",
                                             "required": "请输入旧密码",
                                             "max_length": "旧密码格式错误",
                                             "min_length": "旧密码格式错误"
                                         },
                                         help_text="旧密码")
    new_password = serializers.CharField(required=True, write_only=True, max_length=16, min_length=6, label="新密码",
                                         error_messages={
                                             "blank": "请输入新密码",
                                             "required": "请输入新密码",
                                             "max_length": "新密码格式错误",
                                             "min_length": "新密码格式错误"
                                         },
                                         help_text="新密码")

    def validate_code(self, code):
        verify_user = self.context['request'].user
        verify_records = VerifyCodeModel.objects.filter(email=verify_user.email).order_by("-create_time")
        if verify_records:
            last_record = verify_records[0]
            five_mintes_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
            if five_mintes_ago > last_record.create_time:
                raise serializers.ValidationError("验证码过期")
            if last_record.code != code:
                raise serializers.ValidationError("验证码错误")
        else:
            raise serializers.ValidationError("验证码不存在")
        if not verify_user.check_password(self.initial_data["old_password"]):
            raise serializers.ValidationError("旧密码错误")

    def update(self, instance, validated_data):
        user = self.context['request'].user
        user.set_password(validated_data["new_password"])
        user.save()
        return user

    def validate(self, attrs):
        attrs['username'] = self.context['request'].user.username
        del attrs["code"]
        return attrs

    class Meta:
        model = UserModel
        fields = ("username", "code", "old_password", "new_password")


class ChangeEmailSerializer(serializers.ModelSerializer):
    """
    用户邮箱修改序列化类
    """
    code = serializers.CharField(required=True, write_only=True, max_length=6, min_length=6, label="验证码",
                                 error_messages={
                                     "blank": "请输入验证码",
                                     "required": "请输入验证码",
                                     "max_length": "验证码格式错误",
                                     "min_length": "验证码格式错误"
                                 },
                                 help_text="验证码")
    email = serializers.EmailField(max_length=100, help_text="邮箱")

    def validate_email(self, email):
        if UserModel.objects.filter(email=email).count():
            raise serializers.ValidationError("该邮箱已被其他账户使用")

    def validate_code(self, code):
        verify_records = VerifyCodeModel.objects.filter(email=self.initial_data["email"]).order_by("-create_time")
        if verify_records:
            last_record = verify_records[0]
            five_mintes_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
            if five_mintes_ago > last_record.create_time:
                raise serializers.ValidationError("验证码过期")
            if last_record.code != code:
                raise serializers.ValidationError("验证码错误")
        else:
            raise serializers.ValidationError("验证码错误")

    def validate(self, attrs):
        if attrs["email"] is None:
            attrs["email"] = self.initial_data["email"]
        del attrs["code"]
        return attrs

    class Meta:
        model = UserModel
        fields = ("email", "code",)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ("username", "email")


class UserInfoSerializer(serializers.ModelSerializer):
    """
    用户详情序列化类
    """
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserInfo
        fields = "__all__"


class VerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, email):
        """
        验证邮箱是否已被使用
        """

        # 邮箱是否注册(因修改密码处发送验证码为同一接口，检测邮箱是否已注册放入修改邮箱处进行判断)
        # if UserModel.objects.filter(email=email).count():
        #     raise serializers.ValidationError("该邮箱已被使用")

        # 验证邮箱是否合法
        # EmailField自带验证，无需另外写

        # 验证码发送频率
        one_mintes_ago = datetime.now() - timedelta(hours=0, minutes=1, seconds=0)
        if VerifyCodeModel.objects.filter(create_time__gt=one_mintes_ago, email=email).count():
            raise serializers.ValidationError("距离上一次发送未超过一分钟")
        return email


class getUserFuzzyMailSerializer(serializers.Serializer):
    """
    获取模糊用户邮箱 序列类
    """
    def to_representation(self, obj):
        email = obj.email
        end = email.index("@")
        if end % 2 == 1:
            start = int((end-1)/2)
        else:
            start = int(end/2)
        fuzzyEmail = email.replace(email[start:end], "****")
        return {
            'email': fuzzyEmail
        }


class checkUserMailSerializer(serializers.Serializer):
    """
        检查用户邮箱 序列类
    """
    def to_representation(self, obj):
        if self.context['view'].request.data["email"] == obj.email:
            return {
                'msg': "邮箱校验正确"
            }
        else:
            raise serializers.ValidationError({'detail': '邮箱校验不正确'})


class sendOldEmailCaptchaSerializer(serializers.Serializer):

    def generate_code(self):
        """
        生成六位数字的验证码
        """
        seeds = "1234567890"
        random_str = []
        for i in range(6):
            random_str.append(choice(seeds))
        return "".join(random_str)

    def to_representation(self, obj):
        code = self.generate_code()
        smtp.code_smtp(obj.email, code)
        code_record = VerifyCodeModel(email=obj.email, code=code)
        code_record.save()
        return {
            "msg": "发送成功"
        }


class confirmOldEmailCaptchaSerializer(serializers.Serializer):
    code = serializers.CharField(required=True, write_only=True, max_length=6, min_length=6, label="验证码",
                                 error_messages={
                                     "blank": "请输入验证码",
                                     "required": "请输入验证码",
                                     "max_length": "验证码格式错误",
                                     "min_length": "验证码格式错误"
                                 },
                                 help_text="验证码")

    def to_representation(self, obj):
        verify_records = VerifyCodeModel.objects.filter(email=obj.email).order_by("-create_time")
        if verify_records:
            last_record = verify_records[0]
            five_mintes_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
            if five_mintes_ago > last_record.create_time:
                raise serializers.ValidationError({'detail': '验证码过期'})
            if last_record.code != self.context['view'].request.data["code"]:
                raise serializers.ValidationError({'detail': '验证码错误'})
        else:
            raise serializers.ValidationError({'detail': '验证码不存在'})
        return {
            "msg": "旧邮箱验证通过"
        }

    class Meta:
        model = UserModel
        fields = ("email", )
