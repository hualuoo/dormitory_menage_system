from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from rest_framework.decorators import action

from .models import WaterFeesLog, ElectricityFeesLog
from .serializers import WaterFeesLogSerializer, ElectricityFeesLogSerializer
from .models import Repair, RepairLog
from .serializers import RepairSerializer, RepairCreateSerializer, RepairLogSerializer, RepairLogCreateSerializer
from utils.permission import UserIsSuperUser, FeesLogIsSelf, RepairIsSelf, RepairLogIsSelf


# Create your views here.
class WaterFeesLogViewset(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    水费使用记录 视图类
    """
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = WaterFeesLogSerializer
    queryset = WaterFeesLog.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return WaterFeesLogSerializer
        if self.action == "retrieve":
            return WaterFeesLogSerializer
        return WaterFeesLogSerializer

    def get_permissions(self):
        if self.action == "list":
            return [IsAuthenticated()]
        if self.action == "retrieve":
            return [IsAuthenticated(), FeesLogIsSelf()]
        return []

    def list(self, request, *args, **kwargs):
        """
            水费使用记录 列表
            url: '/water_fees_log/'
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

        # 根据宿舍编号查询
        search_dormitory_number = request.GET.get('search_dormitory_number', '')
        if search_dormitory_number:
            all_result = all_result.filter(Q(dormitory__number=search_dormitory_number))

        # 排序列名
        field = request.GET.get('field', '')
        # 排序类型，升序降序
        order = request.GET.get('order', '')

        # 默认按 添加时间 倒叙
        all_result = all_result.order_by(F("add_time").desc(nulls_last=True))

        # 排序
        if field:
            if order == "asc":
                all_result = all_result.order_by(F(field).asc(nulls_last=True))
            elif order == "desc":
                all_result = all_result.order_by(F(field).desc(nulls_last=True))


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


class ElectricityFeesLogViewset(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    宿舍电费 视图类
    """
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = ElectricityFeesLogSerializer
    queryset = ElectricityFeesLog.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return ElectricityFeesLogSerializer
        if self.action == "retrieve":
            return ElectricityFeesLogSerializer
        return ElectricityFeesLogSerializer

    def get_permissions(self):
        if self.action == "list":
            return [IsAuthenticated()]
        if self.action == "retrieve":
            return [IsAuthenticated(), FeesLogIsSelf()]
        return []

    def list(self, request, *args, **kwargs):
        """
            显示 电费使用记录 列表
            url: '/electricity_fees_log/'
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

        # 根据宿舍编号查询
        search_dormitory_number = request.GET.get('search_dormitory_number', '')
        if search_dormitory_number:
            all_result = all_result.filter(Q(dormitory__number=search_dormitory_number))

        # 排序列名
        field = request.GET.get('field', '')
        # 排序类型，升序降序
        order = request.GET.get('order', '')

        # 默认按 添加时间 倒叙
        all_result = all_result.order_by(F("add_time").desc(nulls_last=True))

        # 排序
        if field:
            if order == "asc":
                all_result = all_result.order_by(F(field).asc(nulls_last=True))
            elif order == "desc":
                all_result = all_result.order_by(F(field).desc(nulls_last=True))


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


class RepairViewset(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    宿舍报修单 视图类
    """
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = RepairSerializer
    queryset = Repair.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return RepairSerializer
        if self.action == "retrieve":
            return RepairSerializer
        if self.action == "update":
            return RepairSerializer
        if self.action == "create":
            return RepairCreateSerializer
        return RepairSerializer

    def get_permissions(self):
        if self.action == "list":
            return [IsAuthenticated()]
        if self.action == "retrieve":
            return [IsAuthenticated(), RepairIsSelf()]
        if self.action == "update":
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "create":
            return [IsAuthenticated()]
        return []

    def list(self, request, *args, **kwargs):
        """
            显示 宿舍报修单 列表
            url: '/repair/'
            type: 'get'
        """
        from django.db.models import Q, F

        # 获取全部数据
        all_result = self.filter_queryset(self.get_queryset())

        # 如果非管理员，仅搜索该用户的宿舍
        if request.user.is_superuser is False:
            all_result = all_result.filter(Q(dormitory=request.user.lived_dormitory))

        # 分页页数
        page = int(request.GET.get('page', '1'))
        # 每页条数
        limit = int(request.GET.get('limit', '10'))

        # 根据状态查询
        search_status = request.GET.get('search_status', '')
        if search_status and search_status != "all":
            all_result = all_result.filter(Q(status=search_status))

        # 根据宿舍编号查询
        search_dormitory_number = request.GET.get('search_dormitory_number', '')
        if search_dormitory_number:
            all_result = all_result.filter(Q(dormitory__number__icontains=search_dormitory_number))

        # 排序列名
        field = request.GET.get('field', '')
        # 排序类型，升序降序
        order = request.GET.get('order', '')

        # 默认按 添加时间 倒叙
        all_result = all_result.order_by(F("add_time").desc(nulls_last=True))

        # 排序
        if field:
            if order == "asc":
                all_result = all_result.order_by(F(field).asc(nulls_last=True))
            elif order == "desc":
                all_result = all_result.order_by(F(field).desc(nulls_last=True))


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
            报修单 创建

        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        repair = Repair.objects.create(title=serializer.validated_data["title"],
                                       content=serializer.validated_data["content"],
                                       status="untreated",
                                       add_time=datetime.now(),
                                       applicant_id=self.request.user.id,
                                       dormitory_id=self.request.user.lived_dormitory.id)
        repair.save()

        return Response({
            "detail": "创建报修单成功！"
        }, status=status.HTTP_200_OK)

class RepairLogViewset(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    宿舍报修单 回复 视图类
    """
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = RepairLogSerializer
    queryset = RepairLog.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return RepairLogSerializer
        if self.action == "retrieve":
            return RepairLogSerializer
        if self.action == "update":
            return RepairLogSerializer
        if self.action == "create":
            return RepairLogCreateSerializer
        return RepairLogSerializer

    def get_permissions(self):
        if self.action == "list":
            return [IsAuthenticated()]
        if self.action == "retrieve":
            return [IsAuthenticated(), RepairLogIsSelf()]
        if self.action == "update":
            return [IsAuthenticated(), RepairLogIsSelf()]
        if self.action == "create":
            return [IsAuthenticated(), RepairLogIsSelf()]
        return []

    def list(self, request, *args, **kwargs):
        from django.db.models import Q, F

        # 获取全部数据
        all_result = self.filter_queryset(self.get_queryset())

        # 如果非管理员，仅搜索该用户
        if request.user.is_superuser is False:
            all_result = all_result.filter(Q(main_repair__dormitory=request.user.lived_dormitory))

        # 根据报修单编号查询
        search_repair_id = request.GET.get('search_repair_id', '')
        if search_repair_id:
            all_result = all_result.filter(Q(main_repair=search_repair_id))

        # 分页页数
        page = int(request.GET.get('page', '1'))
        # 每页条数
        limit = int(request.GET.get('limit', '10'))

        # 排序列名
        field = request.GET.get('field', '')
        # 排序类型，升序降序
        order = request.GET.get('order', '')

        # 默认按 添加时间 倒叙
        all_result = all_result.order_by(F("add_time").desc(nulls_last=True))

        # 排序
        if field:
            if order == "asc":
                all_result = all_result.order_by(F(field).asc(nulls_last=True))
            elif order == "desc":
                all_result = all_result.order_by(F(field).desc(nulls_last=True))

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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if Repair.objects.filter(id=serializer.validated_data["main_repair__id"]):
            if Repair.objects.filter(id=serializer.validated_data["main_repair__id"]).first().status == "complete":
                return Response({
                    "detail": "主报修单已完成，无法回复！"
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "detail": "查询不到主报修单！"
            }, status=status.HTTP_400_BAD_REQUEST)

        repair_log = RepairLog.objects.create(main_repair_id=serializer.validated_data["main_repair__id"],
                                              reply=serializer.validated_data["reply"],
                                              reply_type=serializer.validated_data["reply_type"],
                                              reply_person=self.request.user)

        repair_log.save()

        if serializer.validated_data["reply_type"] == "complete":
            main_repair = repair_log.main_repair
            main_repair.status = "complete"
            main_repair.save()

        return Response({
            "detail": "回复成功！"
        }, status=status.HTTP_200_OK)


class FeesRechargeOrderViewset(viewsets.GenericViewSet):
    """
    充值 订单
    """
    @action(methods=['POST'], detail=False)
    def create_order(self, request, *args, **kwargs):
        create_order_result = requests
