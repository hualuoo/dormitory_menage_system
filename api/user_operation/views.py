from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import ElectricityFeesLog
from .serializers import ElectricityFeesLogSerializer
from .models import Repair, RepairLog
from .serializers import RepairSerializer, RepairLogSerializer, RepairLogCreateSerializer

# Create your views here.
class ElectricityFeesLogViewset(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    宿舍电费 视图类
    """
    serializer_class = ElectricityFeesLogSerializer
    queryset = ElectricityFeesLog.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return ElectricityFeesLogSerializer
        if self.action == "retrieve":
            return ElectricityFeesLogSerializer
        return ElectricityFeesLogSerializer

    def list(self, request, *args, **kwargs):
        """
            显示 电费使用记录 列表
            url: '/electricity_fees_log/'
            type: 'get'
        """
        from django.db.models import Q, F

        # 获取全部数据
        all_result = self.filter_queryset(self.get_queryset())

        # 分页页数
        page = int(request.GET.get('page', '0'))
        # 每页条数
        limit = int(request.GET.get('limit', '0'))

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


class RepairViewset(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    宿舍报修单 视图类
    """
    serializer_class = RepairSerializer
    queryset = Repair.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return RepairSerializer
        if self.action == "retrieve":
            return RepairSerializer
        if self.action == "update":
            return RepairSerializer
        return RepairSerializer

    def list(self, request, *args, **kwargs):
        """
            显示 宿舍报修单 列表
            url: '/repair/'
            type: 'get'
        """
        from django.db.models import Q, F

        # 获取全部数据
        all_result = self.filter_queryset(self.get_queryset())

        # 分页页数
        page = int(request.GET.get('page', '0'))
        # 每页条数
        limit = int(request.GET.get('limit', '0'))

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


class RepairLogViewset(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    宿舍报修单 回复 视图类
    """
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

    def list(self, request, *args, **kwargs):
        from django.db.models import Q, F

        # 获取全部数据
        all_result = self.filter_queryset(self.get_queryset())

        # 根据报修单编号查询
        search_repair_id = request.GET.get('search_repair_id', '')
        if search_repair_id:
            all_result = all_result.filter(Q(main_repair=search_repair_id))

        # 分页页数
        page = int(request.GET.get('page', '0'))
        # 每页条数
        limit = int(request.GET.get('limit', '0'))

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
            'msg': "操作成功：回复成功！"
        }, status=status.HTTP_200_OK)