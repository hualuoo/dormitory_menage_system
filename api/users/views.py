from rest_framework import mixins
from random import choice
from .models import UserModel, UserInfo, VerifyCodeModel
from utils import smtp
from .serializers import UserInfoSerializer, UserRegSerializer, VerifyCodeSerializer, UserEmailUpdateSerializer

from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from utils.permission import UserIsOwner, UserInfoIsOwner

# Create your views here.


class UserInfoViewset(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
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


class UserViewset(mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    用戶
    """
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = UserRegSerializer
    queryset = UserModel.objects.all()

    def get_permissions(self):
        if self.action == "create":
            return []
        elif self.action == "update":
            return [IsAuthenticated(), UserIsOwner(), ]

        return []

    def get_serializer_class(self):
        if self.action == "create":
            return UserRegSerializer
        elif self.action == "update":
            return UserEmailUpdateSerializer
        return UserRegSerializer

    def put(self, request, pk, *args, **kwargs):
        return self.update(request, *args, **kwargs)


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
        :return:
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
