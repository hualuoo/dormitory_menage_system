from rest_framework import mixins
from random import choice
from .models import UserModel, UserInfo, VerifyCodeModel
from utils import smtp
from .serializers import UserInfoSerializer, UserRegSerializer, VerifyCodeSerializer, ChangeEmailSerializer, ChangePasswordSerializer
from .serializers import getUserFuzzyMailSerializer, checkUserMailSerializer, sendOldEmailCaptchaSerializer, confirmOldEmailCaptchaSerializer

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
        code_record = VerifyCodeModel(email=email, code=code)
        code_record.save()
        return Response({
            "msg": "发送成功"
        }, status=status.HTTP_201_CREATED)


class getUserFuzzyMailViewset(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    获取模糊用户邮箱
    """
    permission_classes = (IsAuthenticated, UserIsOwner,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = getUserFuzzyMailSerializer
    queryset = UserModel.objects.all()


class checkUserMailViewset(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    检查用户邮箱
    """
    permission_classes = (IsAuthenticated, UserIsOwner,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = checkUserMailSerializer
    queryset = UserModel.objects.all()


class sendOldEmailCaptchaViewset(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    向旧邮箱发送验证码
    """
    permission_classes = (IsAuthenticated, UserIsOwner,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = sendOldEmailCaptchaSerializer
    queryset = UserModel.objects.all()


class confirmOldEmailCaptchaViewset(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    确认旧邮箱验证码
    """
    permission_classes = (IsAuthenticated, UserIsOwner,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = confirmOldEmailCaptchaSerializer
    queryset = UserModel.objects.all()
