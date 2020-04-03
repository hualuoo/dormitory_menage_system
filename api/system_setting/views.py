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

from dormitories.models import WaterFees, ElectricityFees
from user_operation.models import Repair
from access_control.models import AccessControl, AccessControlAbnormalApplication

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

        todo_list = SystemSetting.objects.filter(code="todo_list").first()
        todo_list.content = serializer.validated_data["todo_list"]
        todo_list.save()

        return Response({
            "detail": "系统设定已保存！"
        }, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def get_todo_list(self, request, *args, **kwargs):
        """
            系统 获取代办事项
            url: '/system_setting/get_todo_list/'
            type: 'post'
        """
        from django.db.models import Q

        todo_list_str = SystemSetting.objects.filter(code="todo_list").first().content
        todo_list = todo_list_str.split(',')

        todo_list_json = {}
        for todo in todo_list:
            if todo == "todo[water_fees]":
                todo_list_json['water_fees'] = WaterFees.objects.filter(have_water_fees__lte=0).count()
            if todo == "todo[electricity_fees]":
                todo_list_json['electricity_fees'] = ElectricityFees.objects.filter(have_electricity_fees__lte=0).count()
            if todo == "todo[repair]":
                todo_list_json['repair'] = Repair.objects.filter(~Q(status="complete")).count()
            if todo == "todo[access_control_later]":
                todo_list_json['access_control_later'] = AccessControl.objects.filter(Q(status="later")).count()
            if todo == "todo[access_control_application]":
                todo_list_json['access_control_application'] = AccessControlAbnormalApplication.objects.filter(Q(result="pending")).count()

        return Response(todo_list_json, status=status.HTTP_200_OK)
