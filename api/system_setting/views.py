from datetime import datetime, timedelta

from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from .models import SystemSetting, SystemLog
from .serializers import SystemSettingSerializer, SystemSettingUpdateSerializer
from dormitories.models import Dormitory, WaterFees, ElectricityFees
from user_operation.models import Repair
from access_control.models import AccessControl, AccessControlAbnormalApplication
from users.models import User
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
        if self.action == "get_todo_list":
            return
        if self.action == "get_overview_info":
            return
        if self.action == "get_backend_server_info":
            return
        if self.action == "data_overview_date":
            return
        if self.action == "data_overview_data":
            return
        if self.action == "get_banner":
            return SystemSettingSerializer
        if self.action == "upload_banner":
            return
        if self.action == "get_fees":
            return SystemSettingSerializer
        return SystemSettingSerializer

    def get_permissions(self):
        if self.action == "list":
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "system_setting_update":
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "get_todo_list":
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "get_overview_info":
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "get_backend_server_info":
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "data_overview_date":
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "data_overview_data":
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "get_banner":
            return []
        if self.action == "upload_banner":
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "get_fees":
            return [IsAuthenticated()]
        return []

    """
    def list(self, request, *args, **kwargs):
        系统设置 列表
        url: '/system_setting/'
        type: 'get'
    """

    @action(methods=['POST'], detail=False)
    def system_setting_update(self, request, *args, **kwargs):
        """
            系统 设置修改
            url: '/system_setting/system_setting_update/'
            type: 'post'
            dataType: 'json'
            data: {
                'water_fees': '<water_fees>',
                'electricity_fees': '<electricity_fees>',
                'todo_list': '<todo_list>',
                'overview_info': '<overview_info>',
                'data_overview_start_date': '<data_overview_start_date>',
                'notice_title': '<notice_title>',
                'notice_content': '<notice_content>'
            }
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

        overview_info = SystemSetting.objects.filter(code="overview_info").first()
        overview_info.content = serializer.validated_data["overview_info"]
        overview_info.save()

        data_overview_start_date = SystemSetting.objects.filter(code="data_overview_start_date").first()
        data_overview_start_date.content = serializer.validated_data["data_overview_start_date"]
        data_overview_start_date.save()

        notice_title = SystemSetting.objects.filter(code="notice_title").first()
        notice_title.content = serializer.validated_data["notice_title"]
        notice_title.save()

        notice_content = SystemSetting.objects.filter(code="notice_content").first()
        notice_content.content = serializer.validated_data["notice_content"]
        notice_content.save()

        system_log = SystemLog.objects.create(content='管理员修改了系统设置',
                                              category="系统设置",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        return Response({
            "detail": "操作成功：系统设定已保存！"
        }, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def get_todo_list(self, request, *args, **kwargs):
        """
            系统 获取代办事项
            url: '/system_setting/get_todo_list/'
            type: 'get'
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

    @action(methods=['GET'], detail=False)
    def get_overview_info(self, request, *args, **kwargs):
        """
            系统 获取系统概略信息
            url: '/system_setting/get_overview_info/'
            type: 'get'
        """
        from django.db.models import Q,F

        overview_info_str = SystemSetting.objects.filter(code="overview_info").first().content
        overview_info = overview_info_str.split(',')

        overview_info_json = {}
        for info in overview_info:
            if info == "info[student]":
                overview_info_json['student_count_active'] = User.objects.filter(Q(is_staff=False) & Q(is_active=True)).count()
                overview_info_json['student_count_total'] = User.objects.filter(Q(is_staff=False)).count()
            if info == "info[staff]":
                overview_info_json['staff_count_active'] = User.objects.filter(Q(is_staff=True) & Q(is_active=True)).count()
                overview_info_json['staff_count_total'] = User.objects.filter(Q(is_staff=True)).count()
            if info == "info[dormitory]":
                overview_info_json['dormitory_count_total'] = Dormitory.objects.filter().count()
                overview_info_json['dormitory_count_empty'] = Dormitory.objects.filter(~Q(allow_live_number__icontains=F("now_live_number"))).count()
            if info == "info[access_control_day]":
                overview_info_json['access_control_day'] = AccessControl.objects.filter(Q(add_time__gte=datetime.now().date())).count()
                overview_info_json['access_control_total'] = AccessControl.objects.filter().count()
            if info == "info[access_control_week]":
                # 当前天 显示当前日期是本周第几天
                day_num = datetime.now().isoweekday()
                # 计算当前日期所在周一零点零分零秒
                # monday = datetime.now() - timedelta(days=day_num) - timedelta(hours=datetime.now().hour, minutes=datetime.now().minute, seconds=datetime.now().second, microseconds=datetime.now().microsecond)
                monday = datetime.strptime(datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d")
                overview_info_json['access_control_week'] = AccessControl.objects.filter(Q(add_time__range=(monday, datetime.now()))).count()
                overview_info_json['access_control_total'] = AccessControl.objects.filter().count()
            if info == "info[access_control_month]":
                overview_info_json['access_control_month'] = AccessControl.objects.filter(Q(add_time__month=datetime.now().month)).count()
                overview_info_json['access_control_total'] = AccessControl.objects.filter().count()

        return Response(overview_info_json, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def get_backend_server_info(self, request, *args, **kwargs):
        """
            系统 获取后端服务器情况
            url: '/system_setting/get_backend_server_info/'
            type: 'get'
        """
        import psutil

        server_info_json = {'cpu_count': psutil.cpu_count(),
                            'cpu_percent': psutil.cpu_percent(),
                            'memory_total': round(psutil.virtual_memory().total/1024/1024),
                            'memory_used': round(psutil.virtual_memory().used/1024/1024),
                            'memory_percent': psutil.virtual_memory().percent,
                            'disk_total': round(psutil.disk_usage("C:\\").total/1024/1024/1024, 2),
                            'disk_used': round(psutil.disk_usage("C:\\").used/1024/1024/1024, 2),
                            'disk_percent': psutil.disk_usage("C:\\").percent}
        return Response(server_info_json, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def data_overview_date(self, request, *args, **kwargs):
        """
            系统 获取后端服务器情况
            url: '/system_setting/data_overview_date/'
            type: 'get'
        """

        data_overview_start_date = SystemSetting.objects.filter(code="data_overview_start_date").first().content
        start_date = datetime.strptime(data_overview_start_date, "%Y-%m-%d")

        date = []
        while start_date.__le__(datetime.strptime(datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d")):
            date.append(start_date.strftime("%Y-%m-%d"))
            start_date += timedelta(days=1)

        return Response({
            "date": date
        }, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def data_overview_data(self, request, *args, **kwargs):
        """
            系统 获取后端服务器情况
            url: '/system_setting/data_overview_data/'
            type: 'get'
        """
        data_overview_start_date = SystemSetting.objects.filter(code="data_overview_start_date").first().content
        start_date = datetime.strptime(data_overview_start_date, "%Y-%m-%d")

        data = []
        while start_date.__le__(datetime.strptime(datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d")):
            data.append(AccessControl.objects.filter(add_time__range=(start_date.date(), (start_date + timedelta(days=1)))).count())
            start_date += timedelta(days=1)

        return Response({
            "data": data
        }, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def get_banner(self, request, *args, **kwargs):
        """
        系统 获取前端Banner
            url: '/system_setting/get_index_data/'
            type: 'get'
        """
        from django.db.models import Q
        all_result = self.filter_queryset(self.get_queryset())
        all_result = all_result.filter(Q(code__icontains="banner") | Q(code__icontains="notice_"))
        queryset = self.filter_queryset(all_result)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['POST'], detail=False)
    def upload_banner(self, request, *args, **kwargs):
        """
            系统 更新前台首页Banner
            url: '/system_setting/upload_banner/'
            type: 'post'
            dateType: 'json'
            data: file
        """
        from utils.save_file import save_img

        avatar = request.FILES.get("file")

        flag = save_img(avatar, "system/banner")
        if flag == 0:
            return Response({
                "detail": "操作失败：未选择上传的文件！"
            }, status=status.HTTP_400_BAD_REQUEST)
        if flag == 1:
            return Response({
                "detail": "操作失败：上传的文件超过2Mb！"
            }, status=status.HTTP_400_BAD_REQUEST)
        if flag == 2:
            return Response({
                "detail": "操作失败：上传的文件不属于图片！"
            }, status=status.HTTP_400_BAD_REQUEST)

        code = request.GET.get('code', '')
        instance = SystemSetting.objects.filter(code=code).first()
        instance.url = flag
        instance.save()

        system_log = SystemLog.objects.create(content='管理员修改了前台' + code,
                                              category="系统设置",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        return Response({
            "code": 0,
            "msg": "操作成功：" + code + "上传成功",
            "data": {
                "src": "http://" + request.META['HTTP_HOST'] + "/media/" + flag
            }
        }, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def get_fees(self, request, *args, **kwargs):
        """
            系统 获取水电费价格
            url: '/system_setting/get_fees/'
            type: 'get'
        """
        all_result = self.filter_queryset(self.get_queryset())
        all_result = all_result.filter(code__icontains="_fees")
        queryset = self.filter_queryset(all_result)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
