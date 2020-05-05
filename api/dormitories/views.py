from datetime import datetime

from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import Dormitory, WaterFees, ElectricityFees
from .serializers import DormitorySerializer, DormitoryCreateSerializer, DormitoryOnChangeTransferSerializer, DormitoryChangeAllowLiveNumberSerializer, DormitoryChangeNoteSerializer
from .serializers import WaterFeesSerializer, WaterFeesRechargeAdminSerializer, WaterFeesChangeNoteSerializer
from .serializers import ElectricityFeesSerializer, ElectricityFeesRechargeAdminSerializer, ElectricityFeesChangeNoteSerializer
from users.models import User
from user_operation.models import WaterFeesLog, ElectricityFeesLog
from system_setting.models import SystemSetting, SystemLog
from utils.permission import UserIsSuperUser, DormitoriesIsSelf, WaterFeesIsSelf, ElectricityFeesIsSelf
# Create your views here.


class DormitoryViewset(mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    宿舍 视图类
    """
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = DormitorySerializer
    queryset = Dormitory.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return DormitorySerializer
        if self.action == "list":
            return DormitorySerializer
        if self.action == "create":
            return DormitoryCreateSerializer
        if self.action == "destroy":
            return
        if self.action == "get_transfer_data":
            return
        if self.action == "get_transfer_value":
            return
        if self.action == "onchange_transfer":
            return DormitoryOnChangeTransferSerializer
        if self.action == "change_allow_live_number":
            return DormitoryChangeAllowLiveNumberSerializer
        if self.action == "change_note":
            return DormitoryChangeNoteSerializer
        return DormitorySerializer

    def get_permissions(self):
        if self.action == "retrieve":
            return [IsAuthenticated(), DormitoriesIsSelf()]
        if self.action == "list":
            return [IsAuthenticated()]
        if self.action == "create":
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "destroy":
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "get_transfer_data":
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "get_transfer_value":
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "onchange_transfer":
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "change_allow_live_number":
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "change_note":
            return [IsAuthenticated(), UserIsSuperUser()]
        return []

    """
    def retrieve(self, request, *args, **kwargs):
        显示单个宿舍信息
        url: '/dormitories/<pk>/'
        type: 'get'
    """

    def list(self, request, *args, **kwargs):
        """
            显示宿舍信息列表
            url: '/dormitories/'
            type: 'get'
        """
        from django.db.models import Q, F

        # 获取全部数据
        all_result = self.filter_queryset(self.get_queryset())

        # 如果非管理员，仅搜索该用户
        if request.user.is_superuser is False:
            all_result = all_result.filter(Q(number=request.user.lived_dormitory))

        # 分页页数
        page = int(request.GET.get('page', '1'))
        # 每页条数
        limit = int(request.GET.get('limit', '10'))

        # 是否只显示为满人宿舍
        is_empty = request.GET.get('is_empty', '')

        # 排序列名
        field = request.GET.get('field', '')
        # 排序类型，升序降序
        order = request.GET.get('order', '')
        # 模糊搜索关键词
        search_number = request.GET.get('search_number', '')
        search_area = request.GET.get('search_area', '')
        search_build = request.GET.get('search_build', '')
        search_floor = request.GET.get('search_floor', '')
        search_room = request.GET.get('search_room', '')

        # 是否为满人宿舍
        if is_empty == 'true':
            all_result = all_result.filter(~Q(allow_live_number__icontains=F("now_live_number")))
        if is_empty == 'false':
            all_result = all_result.filter(Q(allow_live_number__icontains=F("now_live_number")))

        # 排序
        if field:
            if order == "asc":
                all_result = all_result.order_by(F(field).asc(nulls_last=True))
            elif order == "desc":
                all_result = all_result.order_by(F(field).desc(nulls_last=True))

        # 搜索
        if search_number:
            all_result = all_result.filter(Q(number__icontains=search_number))
        if search_area:
            all_result = all_result.filter(Q(area__icontains=search_area))
        if search_build:
            all_result = all_result.filter(Q(build__icontains=search_build))
        if search_floor:
            all_result = all_result.filter(Q(floor__icontains=search_floor))
        if search_room:
            all_result = all_result.filter(Q(room__icontains=search_room))

        # 数据条数
        recordsTotal = all_result.count()

        # 获取首页的数据
        if (page != 0) and (limit != 0):
            all_result = all_result[(page * limit - limit):(page * limit)]

        queryset = self.filter_queryset(all_result)
        serializer = self.get_serializer(queryset, many=True)

        return Response(
            {
                'code': 0,
                'msg': '',
                'count': recordsTotal,
                'data': serializer.data
            })

    def create(self, request, *args, **kwargs):
        """
            创建宿舍
            url: '/dormitories/'
            type: 'post'
            dataType: 'json'
            data: {
                'number': '<number>',
                'area': '<area>',
                'build': '<build>',
                'floor': '<floor>',
                'room': '<room>',
                'allow_live_number': '<allow_live_number>'
            }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        dormitory = Dormitory.objects.create(number=serializer.validated_data["number"],
                                             area=serializer.validated_data["area"],
                                             build=serializer.validated_data["build"],
                                             floor=serializer.validated_data["floor"],
                                             room=serializer.validated_data["room"],
                                             allow_live_number=serializer.validated_data["allow_live_number"],
                                             add_time=datetime.now())
        dormitory.save()
        water_fees = WaterFees.objects.create(dormitory=dormitory)
        electricity_fees = ElectricityFees.objects.create(dormitory=dormitory)
        water_fees.save()
        electricity_fees.save()

        system_log = SystemLog.objects.create(content='创建宿舍（编号：' + serializer.validated_data["number"] + '）',
                                              category="宿舍管理",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """
            创建宿舍
            url: '/dormitories/<pk>/'
            type: 'delete'
        """
        instance = self.get_object()

        system_log = SystemLog.objects.create(content='删除宿舍（编号：' + instance.number + '）',
                                              category="宿舍管理",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['GET'], detail=True)
    def get_transfer_data(self, request, *args, **kwargs):
        """
            获取 未居住的用户 和 当前宿舍已居住的用户
            url: '/dormitories/<pk>/get_transfer_data/'
            type: 'get'
        """
        from django.db.models import Q

        users_list = []
        user_dict = {}
        all_users = User.objects.all()
        not_lived_users = all_users.filter(Q(lived_dormitory__isnull=True) & Q(is_active=True))
        for user in not_lived_users:
            user_dict["value"] = str(user.id)
            user_dict["title"] = user.username + "(" + user.first_name + " " + user.last_name + ")"
            if user.is_staff is True:
                user_dict["title"] += " ★"
            if user.is_active is False:
                user_dict["title"] += " ▲"
            users_list.append(user_dict.copy())

        dormitory = self.get_object()
        lived_users = dormitory.lived_users.all()
        for user in lived_users:
            user_dict["value"] = str(user.id)
            user_dict["title"] = user.username + "(" + user.first_name + " " + user.last_name + ")"
            if user.is_staff is True:
                user_dict["title"] += " ★"
            if user.is_active is False:
                user_dict["title"] += " ▲"
            users_list.append(user_dict.copy())

        return Response({
            "data": users_list
        }, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=True)
    def get_transfer_value(self, request, *args, **kwargs):
        """
            获取 当前宿舍已居住的用户 的 ID
            url: '/dormitories/get_transfer_value/'
            type: 'get'
        """
        users_id_list = []

        dormitory = self.get_object()
        lived_users = dormitory.lived_users.all()
        for user in lived_users:
            users_id_list.append(str(user.id))

        return Response({
            "value": users_id_list
        }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    def onchange_transfer(self, request, *args, **kwargs):
        """
            调整 宿舍 住户
            url: '/dormitories/<pk>/onchange_transfer/'
            type: 'post'
            dataType: 'json'
            data: {
                'ids': '<ids>',
                'index': '<index>'
            }
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        ids = serializer.validated_data["ids"].split(',')

        if serializer.validated_data["index"] == 0:
            if len(ids) + len(instance.lived_users.all()) > instance.allow_live_number:
                return Response({
                    "detail": "居住的人数不能超过允许居住的人数！"
                }, status=status.HTTP_400_BAD_REQUEST)

            for i in ids:
                user = User.objects.filter(id=i).first()
                if user.lived_dormitory_id is not None:
                    return Response({
                        "detail": "ID为' + i + '的用户已居住在' + user.lived_dormitory.number + '内！"
                    }, status=status.HTTP_400_BAD_REQUEST)
                user.lived_dormitory_id = instance
                user.save()
                system_log = SystemLog.objects.create(content='安排用户入住（编号：' + instance.number + '，用户名：' + user.username + '）',
                                                      category="宿舍管理",
                                                      operator=request.user,
                                                      ip=request.META.get("REMOTE_ADDR"))
                system_log.save()

            instance.now_live_number += len(ids)
            instance.save()

            return Response({
                "detail": "操作成功：安排入住成功！"
            }, status=status.HTTP_200_OK)

        if serializer.validated_data["index"] == 1:
            for i in ids:
                user = User.objects.filter(id=i).first()
                if user.lived_dormitory_id != instance.id:
                    return Response({
                        "detail": "ID为" + i + "的用户未居住在" + instance.number + "内！"
                    }, status=status.HTTP_400_BAD_REQUEST)
                user.lived_dormitory_id = None
                user.save()
                system_log = SystemLog.objects.create(content='安排用户退宿（编号：' + instance.number + '，用户名：' + user.username + '）',
                                                      category="宿舍管理",
                                                      operator=request.user,
                                                      ip=request.META.get("REMOTE_ADDR"))
                system_log.save()

            instance.now_live_number -= len(ids)
            instance.save()

            return Response({
                "detail": "操作成功：安排退宿成功！"
            }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    def change_allow_live_number(self, request, *args, **kwargs):
        """
            宿舍 允许居住人数 修改
            url: '/dormitories/<pk>/change_allow_live_number/'
            type: 'post'
            dataType: 'json'
            data: {
                'allow_live_number': '<allow_live_number>'
            }
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        instance.allow_live_number = serializer.validated_data["allow_live_number"]
        instance.save()

        system_log = SystemLog.objects.create(content='修改宿舍的允许居住人数（编号：' + instance.number + '）',
                                              category="宿舍管理",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        return Response({
            "detail": "操作成功：修改允许居住的人数成功！"
        }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    def change_note(self, request, *args, **kwargs):
        """
            宿舍 备注 修改
            url: '/dormitories/<pk>/change_note/'
            type: 'post'
            dataType: 'json'
            data: {
                'note': '<note>'
            }
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        instance.note = serializer.validated_data["note"]
        instance.save()

        system_log = SystemLog.objects.create(content='修改宿舍的备注（编号：' + instance.number + '）',
                                              category="宿舍管理",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        return Response({
            "detail": "操作成功：修改备注成功！"
        }, status=status.HTTP_200_OK)


class WaterFeesViewset(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    宿舍水费 视图类
    """
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = WaterFeesSerializer
    queryset = WaterFees.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return WaterFeesSerializer
        if self.action == "list":
            return WaterFeesSerializer
        if self.action == "recharge_admin":
            return WaterFeesRechargeAdminSerializer
        if self.action == "change_note":
            return WaterFeesChangeNoteSerializer
        return WaterFeesSerializer

    def get_permissions(self):
        if self.action == "retrieve":
            return [IsAuthenticated(), WaterFeesIsSelf()]
        if self.action == "list":
            return [IsAuthenticated()]
        if self.action == "recharge_admin":
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "change_note":
            return [IsAuthenticated(), UserIsSuperUser()]
        return []

    """
    def retrieve(self, request, *args, **kwargs):
        显示单个水费信息
        url: '/water_fees/<pk>/'
        type: 'get'
    """

    def list(self, request, *args, **kwargs):
        """
            宿舍水费 列表
            url: '/water_fees/'
            type: 'get'
        """
        from django.db.models import Q, F

        # 获取全部数据
        all_result = self.filter_queryset(self.get_queryset())

        # 如果非管理员，仅搜索该用户
        if request.user.is_superuser is False:
            all_result = all_result.filter(Q(dormitory=request.user.lived_dormitory))

        # 分页页数
        page = int(request.GET.get('page', '1'))
        # 每页条数
        limit = int(request.GET.get('limit', '10'))

        # 是否只显示为水费用尽宿舍
        is_use_up = request.GET.get('is_use_up', '')

        # 排序列名
        field = request.GET.get('field', '')
        # 排序类型，升序降序
        order = request.GET.get('order', '')
        # 模糊搜索关键词
        search_dormitory_number = request.GET.get('search_dormitory_number', '')

        # 是否只显示为水量用尽宿舍
        if is_use_up == 'true':
            all_result = all_result.filter(Q(have_water_fees__lte=0))

        # 排序
        if field:
            if order == "asc":
                all_result = all_result.order_by(F(field).asc(nulls_last=True))
            elif order == "desc":
                all_result = all_result.order_by(F(field).desc(nulls_last=True))

        # 搜索
        if search_dormitory_number:
            all_result = all_result.filter(Q(dormitory__number__icontains=search_dormitory_number))

        # 数据条数
        recordsTotal = all_result.count()

        # 获取首页的数据
        if (page != 0) and (limit != 0):
            all_result = all_result[(page * limit - limit):(page * limit)]

        queryset = self.filter_queryset(all_result)
        serializer = self.get_serializer(queryset, many=True)

        return Response(
            {
                'code': 0,
                'msg': '',
                'count': recordsTotal,
                'data': serializer.data
            })

    @action(methods=['POST'], detail=True)
    def recharge_admin(self, request, *args, **kwargs):
        """
            宿舍水费 管理员充值
            url: '/water_fees/<pk>/recharge_admin/'
            type: 'post'
            dataType: 'json'
            data: {
                'money': '<money>'
            }
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        instance.have_water_fees += serializer.validated_data["money"]
        instance.save()

        note = "管理员" + self.request.user.username + "代充(" + str(round(float(serializer.validated_data["money"])/float(SystemSetting.objects.filter(code='water_fees').first().content), 2)) +"吨," + str(serializer.validated_data["money"]) +"元" + ")"
        water_fees_log = WaterFeesLog.objects.create(dormitory=instance.dormitory,
                                                     mode="add",
                                                     change_money=serializer.validated_data["money"],
                                                     operator=self.request.user,
                                                     note=note)
        water_fees_log.save()

        system_log = SystemLog.objects.create(content='管理员代充水费（宿舍编号：' + instance.dormitory.number + '，充值金额：' + str(serializer.validated_data["money"]) + '）',
                                              category="水费管理",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        return Response({
            "detail": "操作成功：充值成功！"
        }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    def change_note(self, request, *args, **kwargs):
        """
            宿舍水费 修改备注
            url: '/water_fees/<pk>/change_note/'
            type: 'post'
            dataType: 'json'
            data: {
                'note': '<note>'
            }
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        instance.note = serializer.validated_data["note"]
        instance.save()

        system_log = SystemLog.objects.create(content='修改宿舍水费备注（宿舍编号：' + instance.dormitory.number + '）',
                                              category="水费管理",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        return Response({
            "detail": "操作成功：编辑成功！"
        }, status=status.HTTP_200_OK)


class ElectricityFeesViewset(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    宿舍电费 视图类
    """
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = ElectricityFeesSerializer
    queryset = ElectricityFees.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ElectricityFeesSerializer
        if self.action == "list":
            return ElectricityFeesSerializer
        if self.action == "recharge_admin":
            return ElectricityFeesRechargeAdminSerializer
        if self.action == "change_note":
            return ElectricityFeesChangeNoteSerializer
        return ElectricityFeesSerializer

    def get_permissions(self):
        if self.action == "retrieve":
            return [IsAuthenticated(), ElectricityFeesIsSelf()]
        if self.action == "list":
            return [IsAuthenticated()]
        if self.action == "recharge_admin":
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "change_note":
            return [IsAuthenticated(), UserIsSuperUser()]
        return []

    """
    def retrieve(self, request, *args, **kwargs):
        显示单个水费信息
        url: '/electricity_fees/<pk>/'
        type: 'get'
    """

    def list(self, request, *args, **kwargs):
        """
            显示电费列表
            url: '/electricity_fees/'
            type: 'get'
        """
        from django.db.models import Q, F

        # 获取全部数据
        all_result = self.filter_queryset(self.get_queryset())

        # 如果非管理员，仅搜索该用户
        if request.user.is_superuser is False:
            all_result = all_result.filter(Q(dormitory=request.user.lived_dormitory))

        # 分页页数
        page = int(request.GET.get('page', '1'))
        # 每页条数
        limit = int(request.GET.get('limit', '10'))

        # 是否只显示为电量用尽宿舍
        is_use_up = request.GET.get('is_use_up', '')

        # 排序列名
        field = request.GET.get('field', '')
        # 排序类型，升序降序
        order = request.GET.get('order', '')
        # 模糊搜索关键词
        search_dormitory_number = request.GET.get('search_dormitory_number', '')

        # 是否只显示为水量用尽宿舍
        if is_use_up == 'true':
            all_result = all_result.filter(Q(have_electricity_fees__lte=0))

        # 排序
        if field:
            if order == "asc":
                all_result = all_result.order_by(F(field).asc(nulls_last=True))
            elif order == "desc":
                all_result = all_result.order_by(F(field).desc(nulls_last=True))

        # 搜索
        if search_dormitory_number:
            all_result = all_result.filter(Q(dormitory__number__icontains=search_dormitory_number))

        # 数据条数
        recordsTotal = all_result.count()

        # 获取首页的数据
        if (page != 0) and (limit != 0):
            all_result = all_result[(page * limit - limit):(page * limit)]

        queryset = self.filter_queryset(all_result)
        serializer = self.get_serializer(queryset, many=True)

        return Response(
            {
                'code': 0,
                'msg': '',
                'count': recordsTotal,
                'data': serializer.data
            })

    @action(methods=['POST'], detail=True)
    def recharge_admin(self, request, *args, **kwargs):
        """
            宿舍电费 管理员充值
            url: '/electricity_fees/<pk>/recharge_admin/'
            type: 'post'
            dataType: 'json'
            data: {
                'money': '<money>'
            }
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        instance.have_electricity_fees += serializer.validated_data["money"]
        instance.save()

        note = "管理员" + self.request.user.username + "代充(" + str(round(float(serializer.validated_data["money"])/float(SystemSetting.objects.filter(code='electricity_fees').first().content), 2)) +"千瓦时," + str(serializer.validated_data["money"]) +"元" + ")"
        electricity_fees_log = ElectricityFeesLog.objects.create(dormitory=instance.dormitory,
                                                                 mode="add",
                                                                 change_money=serializer.validated_data["money"],
                                                                 operator=self.request.user,
                                                                 note=note)
        electricity_fees_log.save()

        system_log = SystemLog.objects.create(content='管理员代充水费（宿舍编号：' + instance.dormitory.number + '，充值金额：' + str(serializer.validated_data["money"]) + '）',
                                              category="电费管理",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        return Response({
            "detail": "操作成功：充值成功！"
        }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    def change_note(self, request, *args, **kwargs):
        """
            宿舍电费 修改备注
            url: '/electricity_fees/<pk>/change_note/'
            type: 'post'
            dataType: 'json'
            data: {
                'note': '<note>'
            }
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        instance.note = serializer.validated_data["note"]
        instance.save()

        system_log = SystemLog.objects.create(content='修改宿舍电费备注（宿舍编号：' + instance.dormitory.number + '）',
                                              category="电费管理",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        return Response({
            "detail": "操作成功：编辑成功！"
        }, status=status.HTTP_200_OK)