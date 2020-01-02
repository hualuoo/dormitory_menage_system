from rest_framework import mixins

from .models import UserModel, UserInfo

from .serializers import UserInfoSerializer, UserRegSerializer

from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import CreateModelMixin

from utils.permission import IsOwnerOrReadOnly

# Create your views here.


class UserInfoViewset(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    用户详细信息
    """
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    queryset = UserInfo.objects.all()
    serializer_class = UserInfoSerializer
    # 根据用户ID查询用户详细信息
    lookup_field = "user_id"


class UserViewset(CreateModelMixin, viewsets.GenericViewSet):
    """
    用戶
    """
    serializer_class = UserRegSerializer
    queryset = UserModel.objects.all()

