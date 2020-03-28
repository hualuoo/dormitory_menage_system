from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from .models import SystemSetting
from .serializers import SystemSettingSerializer, SystemSettingUpdateSerializer
from utils.permission import UserIsSuperUser


# Create your views here.
class SystemSettingViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = SystemSettingSerializer
    queryset = SystemSetting.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return SystemSettingSerializer
        if self.action == "system_setting_update":
            return SystemSettingUpdateSerializer
        return SystemSettingSerializer

    def get_permissions(self):
        # if self.action == "get_setting_all":
        #    return [IsAuthenticated(), UserIsSuperUser()]
        return []

    @action(methods=['POST'], detail=False)
    def system_setting_update(self, request, *args, **kwargs):
        """
            系统 设置修改
            url: '/system_setting/system_setting_update/'
            type: 'post'
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        water_fees = SystemSetting.objects.filter(code="water_fees").first()
        water_fees.content = serializer.validated_data["water_fees"]
        water_fees.save()

        electricity_fees = SystemSetting.objects.filter(code="electricity_fees").first()
        electricity_fees.content = serializer.validated_data["electricity_fees"]
        electricity_fees.save()

        return Response({
            "msg": "保存成功！"
        }, status=status.HTTP_200_OK)
