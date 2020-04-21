import re
from datetime import datetime, timedelta
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User, UserInfo, CaptchaModel


class UserSerializer(serializers.ModelSerializer):
    """
    用户 获取 序列化类
    """
    id = serializers.IntegerField(help_text="ID")
    username = serializers.CharField(help_text="用户名")
    email = serializers.SerializerMethodField(help_text="邮箱")
    first_name = serializers.CharField(help_text="姓")
    last_name = serializers.CharField(help_text="名")
    last_login = serializers.DateTimeField(help_text="最后登录时间", format="%Y-%m-%d %H:%M:%S")
    date_joined = serializers.DateTimeField(help_text="账户创建时间", format="%Y-%m-%d %H:%M:%S")
    is_active = serializers.BooleanField(help_text="是否可用")
    is_staff = serializers.BooleanField(help_text="是否为教职工")
    info__birthday = serializers.DateField(source='info.birthday', help_text="出生年月")
    info__gender = serializers.ChoiceField(source='info.gender', help_text="性别",
                                           choices=(("male", "男"), ("female", "女"), ("unknown", "未知")))
    info__mobile = serializers.SerializerMethodField(help_text="电话")
    info__avatar = serializers.ImageField(source='info.avatar', help_text="照片")
    lived_dormitory = serializers.SerializerMethodField()

    def get_lived_dormitory(self, obj):
        if obj.lived_dormitory is not None:
            return obj.lived_dormitory.number
        else:
            return None

    def get_email(self, obj):
        mail = obj.email
        if mail == "":
            return mail
        if self.context['request'].user.is_superuser:
            return mail
        else:
            end = mail.index("@")
            if end % 2 == 1:
                start = int((end - 1) / 2)
            else:
                start = int(end / 2)
            fuzzyMail = mail.replace(mail[start:end], "****")
            return "".join(fuzzyMail)

    def get_info__mobile(self, obj):
        mobile = obj.info.mobile
        if mobile == "":
            return mobile
        if self.context['request'].user.is_superuser:
            return mobile
        else:
            return "".join(mobile[0:3]) + "****" + "".join(mobile[7:11])

    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "last_login", "date_joined", "is_active",
                  "is_staff", "info__birthday", "info__gender", "info__mobile", "info__avatar","lived_dormitory", )


class UserCreateSerializer(serializers.ModelSerializer):
    """
    用户 创建 序列化类
    """
    username = serializers.CharField(help_text="用户名")
    password = serializers.CharField(help_text="密码", write_only=True)
    is_staff = serializers.BooleanField(help_text="是否为教职工")

    def validate_username(self, username):
        flag = re.match(r'^[a-zA-Z0-9_-]{4,16}$', username)
        if flag is None:
            raise serializers.ValidationError('操作失败：用户名须为4~16位，可包含数字、字母、下划线、减号，不可包含中文和空格！')
        if User.objects.filter(username=username):
            raise serializers.ValidationError('操作失败：该用户名已存在！')
        return username

    def validate_password(self, password):
        flag = re.match(r'(?!^[0-9]+$)(?!^[A-z]+$)(?!^[^A-z0-9]+$)^[^\s\u4e00-\u9fa5]{8,20}$', password)
        if flag is None:
            raise serializers.ValidationError('操作失败：密码须为6~20位，数字、字母、字符至少包含两种，且不能包含中文和空格！')
        return password

    def create(self, validated_data):
        user = super(UserCreateSerializer, self).create(validated_data=validated_data)
        user.set_password(validated_data["password"])
        user.save()
        info = UserInfo.objects.create(user=user)
        info.save()
        return user

    class Meta:
        model = User
        fields = ("username", "password", "is_staff", )


class UserCreateMultipleSerializer(serializers.ModelSerializer):
    """
    用户 批量创建 序列类
    """
    first_username = serializers.CharField(help_text="用户名")
    create_number = serializers.IntegerField(help_text="创建数量", min_value=1, max_value=100)
    password = serializers.CharField(help_text="密码", write_only=True)

    def validate_first_username(self, first_username):
        flag = re.match(r'^[0-9]{4,16}$', first_username)
        if flag is None:
            raise serializers.ValidationError('操作失败：首用户名须为4~16位，只可包含数字！')
        if int(first_username) + int(self.initial_data["create_number"]) - 1 > 9999999999999999:
            raise serializers.ValidationError('操作失败：用户名越界！')
        for username in range(int(first_username), int(first_username)+int(self.initial_data["create_number"])):
            if User.objects.filter(username=username):
                raise serializers.ValidationError('操作失败：已存在用户' + str(username) + '！')
        return int(first_username)

    def validate_password(self, password):
        flag = re.match(r'(?!^[0-9]+$)(?!^[A-z]+$)(?!^[^A-z0-9]+$)^[^\s\u4e00-\u9fa5]{8,20}$', password)
        if flag is None:
            raise serializers.ValidationError('操作失败：密码须为8~20位，数字、字母、字符至少包含两种，且不能包含中文和空格！')
        return password

    class Meta:
        model = User
        fields = ("first_username", "create_number", "password", )


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    用户 修改 序列化类
    """
    email = serializers.EmailField(help_text="邮箱", allow_blank=True, required=False, max_length=100)
    first_name = serializers.CharField(help_text="姓", allow_blank=True, max_length=4)
    last_name = serializers.CharField(help_text="名", allow_blank=True, max_length=4)
    info__birthday = serializers.DateField(source='info.birthday', help_text="出生年月", allow_null=True, required=False)
    info__gender = serializers.ChoiceField(source='info.gender', help_text="性别",
                                           choices=(("male", "男"), ("female", "女"), ("unknown", "未知")))
    info__mobile = serializers.CharField(source='info.mobile', help_text="电话", required=False, allow_blank=True, max_length=11)

    def validate_email(self, email):
        if len(email) == 0:
            return email
        flag = re.match(r'(^$)|^([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+$', email)
        if flag is None:
            raise serializers.ValidationError('操作失败：邮箱格式不正确！')
        if User.objects.filter(email=email).count() and self.instance.email != email:
            raise serializers.ValidationError('操作失败：该邮箱已被其他账户使用！')
        return email

    def validate_first_name(self, first_name):
        flag = re.match(r'(^$)|^[\u4E00-\u9FA5]{1,2}$', first_name)
        if flag is None:
            raise serializers.ValidationError('操作失败：姓必须为1到2个中文！')
        return first_name

    def validate_last_name(self, last_name):
        flag = re.match(r'(^$)|^[\u4E00-\u9FA5]{1,2}$', last_name)
        if flag is None:
            raise serializers.ValidationError('操作失败：名必须为1到2个中文！')
        return last_name

    def validate_info__mobile(self, mobile):
        if len(mobile) == 0:
            return mobile
        flag = re.match(r'(^$)|^1(3[0-9]|4[5,7]|5[0,1,2,3,5,6,7,8,9]|6[2,5,6,7]|7[0,1,7,8]|8[0-9]|9[1,8,9])\d{8}$', mobile)
        if flag is None:
            raise serializers.ValidationError('操作失败：请输入正确的手机号！')
        if UserInfo.objects.filter(mobile=mobile).count() and self.instance.info.mobile != mobile:
            raise serializers.ValidationError('操作失败：该手机已被其他账户使用！')
        return mobile

    def update(self, instance, validated_data):
        if self.instance.is_superuser:
            instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()
        if self.initial_data['info__birthday'] == "":
            instance.info.birthday = None
        else:
            instance.info.birthday = self.initial_data['info__birthday']
        instance.info.gender = self.initial_data['info__gender']
        if 'info__mobile' in self.initial_data:
            instance.info.mobile = self.initial_data['info__mobile']
        instance.info.save()
        return instance

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "info__birthday", "info__gender", "info__mobile", )


class UserResetPasswordSerializer(serializers.ModelSerializer):
    """
    用户重置密码 序列类
    """
    password = serializers.CharField(help_text="密码", write_only=True)

    def validate_password(self, password):
        flag = re.match(r'(?!^[0-9]+$)(?!^[A-z]+$)(?!^[^A-z0-9]+$)^[^\s\u4e00-\u9fa5]{8,20}$', password)
        if flag is None:
            raise serializers.ValidationError('操作失败：密码须为8~20位，数字、字母、字符至少包含两种，且不能包含中文和空格！')
        return password

    class Meta:
        model = User
        fields = ("password", )


class UserResetPasswordMultipleSerializer(serializers.ModelSerializer):
    """
    用户密码修改 序列类
    """
    ids = serializers.CharField(help_text="用户队列")
    password = serializers.CharField(help_text="密码", write_only=True)

    def validate_ids(self, ids):
        ids_list = ids.split(',')
        for i in ids_list:
            users = User.objects.filter(id=i)
            if users.count() == 0:
                raise serializers.ValidationError('操作失败：ID为' + i + '的用户不存在！')
            if users.first() == self.context['request'].user:
                raise serializers.ValidationError('操作失败：您无法操作自己！')
        return ids

    def validate_password(self, password):
        flag = re.match(r'(?!^[0-9]+$)(?!^[A-z]+$)(?!^[^A-z0-9]+$)^[^\s\u4e00-\u9fa5]{8,20}$', password)
        if flag is None:
            raise serializers.ValidationError('操作失败：密码须为8~20位，数字、字母、字符至少包含两种，且不能包含中文和空格！')
        return password

    class Meta:
        model = User
        fields = ("ids", "password", )


class UserCheckIdsSerializer(serializers.ModelSerializer):
    """
    用户 队列检查 序列类
    """
    ids = serializers.CharField(help_text="用户队列")

    def validate_ids(self, ids):
        ids_list = ids.split(',')
        for i in ids_list:
            users = User.objects.filter(id=i)
            if users.count() == 0:
                raise serializers.ValidationError('操作失败：ID为' + i + '的用户不存在！')
            if users.first() == self.context['request'].user:
                raise serializers.ValidationError('操作失败：您无法操作自己！')
        return ids

    class Meta:
        model = User
        fields = ("ids", )


class UserFaceListSerializer(serializers.ModelSerializer):
    """
    用户 人脸 序列类
    """
    id = serializers.IntegerField(help_text="ID")
    username = serializers.CharField(help_text="用户名")
    first_name = serializers.CharField(help_text="姓")
    last_name = serializers.CharField(help_text="名")
    face__photo = serializers.ImageField(source='face.photo', help_text="人脸照片地址")
    face__add_time = serializers.DateTimeField(source='face.add_time', help_text="账户创建时间", format="%Y-%m-%d %H:%M")

    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "face__photo", "face__add_time", )


class UserChangePasswordAdminSerializer(serializers.ModelSerializer):
    """
    管理员 修改密码
    """
    old_password = serializers.CharField(help_text="旧密码", write_only=True)
    new_password = serializers.CharField(help_text="新密码", write_only=True)

    def validate_old_password(self, old_password):
        if self.context['request'].user.check_password(old_password):
            return old_password
        else:
            raise serializers.ValidationError('操作失败：旧密码校验错误！')

    def validate_new_password(self, new_password):
        flag = re.match(r'(?!^[0-9]+$)(?!^[A-z]+$)(?!^[^A-z0-9]+$)^[^\s\u4e00-\u9fa5]{8,20}$', new_password)
        if flag is None:
            raise serializers.ValidationError('操作失败：密码须为8~20位，数字、字母、字符至少包含两种，且不能包含中文和空格！')
        return new_password

    def update(self, instance, validated_data):
        user = self.context['request'].user
        user.set_password(validated_data["new_password"])
        user.save()
        return user

    class Meta:
        model = User
        fields = ("old_password", "new_password", )


class SecurityCheckOldEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=100, help_text="邮箱")

    class Meta:
        model = User
        fields = ("email", )


class SecurityConfirmOldEmailSerializer(serializers.ModelSerializer):
    captcha = serializers.CharField(required=True, write_only=True, max_length=6, min_length=6, help_text="验证码")

    def validate_captcha(self, captcha):
        captcha_list = CaptchaModel.objects.filter(email=self.initial_data["email"]).order_by("-create_time")
        if captcha_list:
            last_captcha = captcha_list[0]
            five_mintes_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
            if five_mintes_ago > last_captcha.create_time:
                raise serializers.ValidationError('操作失败：验证码过期！')
            if last_captcha.code != captcha:
                raise serializers.ValidationError('操作失败：验证码错误！')
        else:
            raise serializers.ValidationError('操作失败：验证码错误！')
        return captcha

    class Meta:
        model = User
        fields = ("captcha", )


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
        verify_records = CaptchaModel.objects.filter(email=verify_user.email).order_by("-create_time")
        if verify_records:
            last_record = verify_records[0]
            five_mintes_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
            if five_mintes_ago > last_record.create_time:
                raise serializers.ValidationError('操作失败：验证码过期！')
            if last_record.code != code:
                raise serializers.ValidationError('操作失败：验证码错误！')
        else:
            raise serializers.ValidationError('操作失败：验证码不存在！')
        if not verify_user.check_password(self.initial_data["old_password"]):
            raise serializers.ValidationError('操作失败：旧密码错误！')
        return code

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
        model = User
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
        if User.objects.filter(email=email).count():
            raise serializers.ValidationError('操作失败：该邮箱已被其他账户使用！')
        return email

    def validate_code(self, code):
        verify_records = CaptchaModel.objects.filter(email=self.initial_data["email"]).order_by("-create_time")
        if verify_records:
            last_record = verify_records[0]
            five_mintes_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
            if five_mintes_ago > last_record.create_time:
                raise serializers.ValidationError('操作失败：验证码过期！')
            if last_record.code != code:
                raise serializers.ValidationError('操作失败：验证码错误！')
        else:
            raise serializers.ValidationError('操作失败：验证码错误！')
        return code

    def validate(self, attrs):
        if attrs["email"] is None:
            attrs["email"] = self.initial_data["email"]
        del attrs["code"]
        return attrs

    class Meta:
        model = User
        fields = ("email", "code",)


class VerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, email):
        """
        验证邮箱是否已被使用
        """

        # 邮箱是否注册(因修改密码处发送验证码为同一接口，检测邮箱是否已注册放入修改邮箱处进行判断)
        # if UserModel.objects.filter(email=email).count():
        #     raise serializers.ValidationError('操作失败：该邮箱已被使用！')

        # 验证邮箱是否合法
        # EmailField自带验证，无需另外写

        # 验证码发送频率
        one_mintes_ago = datetime.now() - timedelta(hours=0, minutes=1, seconds=0)
        if CaptchaModel.objects.filter(create_time__gt=one_mintes_ago, email=email).count():
            raise serializers.ValidationError('操作失败：距离上一次发送未超过一分钟！')
        return email


class checkUserMailSerializer(serializers.Serializer):
    """
        检查用户邮箱 序列类
        Used for:
            checkUserMailViewset
    """
    email = serializers.EmailField(max_length=100, help_text="邮箱")

    class Meta:
        model = User
        fields = ("email",)


class sendOldMailCaptchaSerializer(serializers.Serializer):
    """
        向旧邮箱发送验证码 序列类
        Used for:
            sendOldMailCaptchaViewset
    """
    email = serializers.EmailField(max_length=100, help_text="邮箱")

    def validate_email(self, email):
        one_mintes_ago = datetime.now() - timedelta(hours=0, minutes=1, seconds=0)
        if CaptchaModel.objects.filter(create_time__gt=one_mintes_ago, email=email).count():
            raise serializers.ValidationError('操作失败：距离上一次发送未超过一分钟！')
        return email

    class Meta:
        model = User
        fields = ("email",)


class confirmMailCaptchaSerializer(serializers.Serializer):
    """
        确认邮箱验证码是否正确 序列类
        Used for:
            confirmOldMailCaptchaViewset
            confirmNewMailCaptchaViewset
    """
    email = serializers.EmailField(max_length=100, help_text="邮箱")
    code = serializers.CharField(required=True, write_only=True, max_length=6, min_length=6, label="验证码",
                                 error_messages={
                                     "blank": "请输入验证码",
                                     "required": "请输入验证码",
                                     "max_length": "验证码格式错误",
                                     "min_length": "验证码格式错误"
                                 },
                                 help_text="验证码")

    def validate_code(self, code):
        captcha = CaptchaModel.objects.filter(email=self.initial_data["email"]).order_by("-create_time")
        if captcha:
            last_captcha = captcha[0]
            five_mintes_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
            if five_mintes_ago > last_captcha.create_time:
                raise serializers.ValidationError('操作失败：该验证码已过期！')
            if last_captcha.code != code:
                raise serializers.ValidationError('操作失败：该验证码错误！')
        else:
            raise serializers.ValidationError('操作失败：该邮箱的验证码不存在！')
        return code

    class Meta:
        model = User
        fields = ("email", "code")


class sendNewMailCaptchaSerializer(serializers.Serializer):
    """
        向新邮箱发送验证码 序列类
        Used for:
            sendNewMailCaptchaViewset
    """
    email = serializers.EmailField(max_length=100, help_text="新邮箱")

    def validate_email(self, email):
        """
        验证邮箱
        """
        # 邮箱是否被使用
        if User.objects.filter(email=email).count():
            raise serializers.ValidationError('操作失败：该邮箱已被使用！')
        # 验证码发送频率
        one_mintes_ago = datetime.now() - timedelta(hours=0, minutes=1, seconds=0)
        if CaptchaModel.objects.filter(create_time__gt=one_mintes_ago, email=email).count():
            raise serializers.ValidationError('操作失败：距离上一次发送未超过一分钟！')
        return email

    class Meta:
        model = CaptchaModel
        fields = ("email",)
