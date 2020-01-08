from rest_framework import mixins
from random import choice
from datetime import datetime, timedelta
from .models import UserModel, UserInfo, CaptchaModel
from utils import smtp
from .serializers import UserInfoSerializer, UserRegSerializer, VerifyCodeSerializer, ChangeEmailSerializer, ChangePasswordSerializer
from .serializers import checkUserMailSerializer, sendOldMailCaptchaSerializer, confirmOldMailCaptchaSerializer, sendNewEmailCaptchaSerializer

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from utils.permission import UserIsOwner, UserInfoIsOwner

# Create your views here.


class UserInfoViewset(mixins.ListModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    用户详细信息
    """
    permission_classes = (IsAuthenticated, UserInfoIsOwner, )
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    queryset = UserInfo.objects.all()
    serializer_class = UserInfoSerializer
    # 根据用户ID查询用户详细信息
    lookup_field = "user_id"

    def get_queryset(self):
        if self.request.user.is_superuser:
            return UserInfo.objects.all()
        return UserInfo.objects.filter(user=self.request.user)


class UsersViewset(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    用戶
    """
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = UserRegSerializer
    queryset = UserModel.objects.all()

    def get_permissions(self):
        if self.action == "create":
            return []
        if self.action == "update":
            return [IsAuthenticated(), UserIsOwner(), ]
        return []

    def get_serializer_class(self):
        if self.action == "create":
            return UserRegSerializer
        if self.action == "update":
            return ChangeEmailSerializer
        return UserRegSerializer

    def put(self, request, pk, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class ChangePasswordViewset(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    修改密码
    """
    permission_classes = (IsAuthenticated, UserIsOwner,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = ChangePasswordSerializer
    queryset = UserModel.objects.all()


class VerifyCodeViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    发送短信验证码
    """
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = VerifyCodeSerializer

    def generate_code(self):
        """
        生成六位数字的验证码
        """
        seeds = "1234567890"
        random_str = []
        for i in range(6):
            random_str.append(choice(seeds))
        return "".join(random_str)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        code = self.generate_code()

        smtp.code_smtp(email, code)
        code_record = CaptchaModel(email=email, code=code)
        code_record.save()
        return Response({
            "msg": "发送成功"
        }, status=status.HTTP_201_CREATED)


class getUserFuzzyMailViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
        获取模糊用户邮箱
        URL:
            /member/security/getUserFuzzyMail/
        TYPE:
            GET
    """
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    queryset = UserModel.objects.all()

    def fuzzy_mail(self, mail):
        end = mail.index("@")
        if end % 2 == 1:
            start = int((end - 1) / 2)
        else:
            start = int(end / 2)
        fuzzyMail = mail.replace(mail[start:end], "****")
        return "".join(fuzzyMail)

    def list(self, request, *args, **kwargs):
        mail = self.request.user.email
        if mail is None:
            return Response({
                'detail': '未绑定邮箱'
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "email": self.fuzzy_mail(mail)
            }, status=status.HTTP_200_OK)


class checkUserMailViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
        检查用户邮箱
        URL:
            /member/security/checkUserMail/
        TYPE:
            POST
        JSON:
            {
                "check_mail": "<check_mail>"
            }
    """
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = checkUserMailSerializer

    def create(self, request, *args, **kwargs):
        user = self.request.user

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if user.email is None:
            return Response({
                'detail': '未绑定邮箱'
            }, status=status.HTTP_400_BAD_REQUEST)
        if user.email == self.request.data["check_mail"]:
            return Response({
                "msg": "邮箱校验正确"
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'detail': '邮箱校验不正确'
            }, status=status.HTTP_400_BAD_REQUEST)


class sendOldMailCaptchaViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
        向旧邮箱发送验证码
        URL:
            /member/security/sendOldMailCaptcha/
        TYPE:
            POST
    """
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = sendOldMailCaptchaSerializer

    def generate_code(self):
        """
        生成六位数字的验证码
        """
        seeds = "1234567890"
        random_str = []
        for i in range(6):
            random_str.append(choice(seeds))
        return "".join(random_str)

    def create(self, request, *args, **kwargs):
        user = self.request.user

        if user.email is None:
            return Response({
                'detail': '未绑定邮箱'
            }, status=status.HTTP_400_BAD_REQUEST)

        data = request.POST.copy()
        data['email'] = user.email

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        code = self.generate_code()

        if smtp.code_smtp(email, code) == 1:
            code_record = CaptchaModel(email=email, code=code)
            code_record.save()
            return Response({
                "msg": "发送成功"
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "detail": "发送失败"
            }, status=status.HTTP_400_BAD_REQUEST)


class confirmOldMailCaptchaViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
        确认旧邮箱验证码
        URL:
            /member/security/confirmOldMailCaptcha/
        TYPE:
            POST
        JSON:
        {
            "captcha_code": "<captcha_code>"
        }
    """
    permission_classes = (IsAuthenticated, UserIsOwner,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = confirmOldMailCaptchaSerializer
    #queryset = UserModel.objects.all()

    def create(self, request, *args, **kwargs):
        user = self.request.user

        if user.email is None:
            return Response({
                'detail': '未绑定邮箱'
            }, status=status.HTTP_400_BAD_REQUEST)

        captcha = CaptchaModel.objects.filter(email=user.email).order_by("-create_time")
        confirm_captcha = request.data["captcha_code"]

        if captcha:
            last_captcha = captcha[0]
            five_mintes_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
            if five_mintes_ago > last_captcha.create_time:
                return Response({
                    'detail': '验证码过期'
                }, status=status.HTTP_400_BAD_REQUEST)
            if last_captcha.code != confirm_captcha:
                return Response({
                    'detail': '验证码错误'
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'msg': '验证码正确'
                }, status=status.HTTP_200_OK)
        else:
            return Response({
                'detail': '验证码不存在'
            }, status=status.HTTP_400_BAD_REQUEST)


class sendNewEmailCaptchaViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    向新邮箱发送验证码
    /member/security/sendNewEmailCaptcha/
    json:{"new_email": "<new_email>"}
    """
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = sendNewEmailCaptchaSerializer

    def create(self, request, *args, **kwargs):
        print("123")