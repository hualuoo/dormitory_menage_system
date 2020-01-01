from django.shortcuts import render
from rest_framework import mixins
from rest_framework import generics

from .models import UserModel

from .serializers import UsersSerializer, UserRegSerializer

from rest_framework import serializers, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import CreateModelMixin

# Create your views here.
from django.contrib.auth import get_user_model

User = get_user_model()


class UsersListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    queryset = UserModel.objects.all()
    serializer_class = UsersSerializer


class UserViewset(CreateModelMixin, viewsets.GenericViewSet):
    """
    用戶
    """
    serializer_class = UserRegSerializer
    queryset = UserModel.objects.all()

