import requests
import json
from datetime import datetime

from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from .models import WaterFeesLog, ElectricityFeesLog
from .serializers import WaterFeesLogSerializer, ElectricityFeesLogSerializer
from .models import Repair, RepairLog
from .serializers import RepairSerializer, RepairCreateSerializer, RepairLogSerializer, RepairLogCreateSerializer
from .models import FeesRechargeOrder
from .serializers import FeesRechargeOrderCreateSerializer
from users.models import User
from system_setting.models import SystemSetting, SystemLog
from utils.permission import UserIsSuperUser, FeesLogIsSelf, RepairIsSelf, RepairLogIsSelf
from django.conf import settings
# Create your views here.


class WaterFeesLogViewset(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    水费使用记录 视图类
    """
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = WaterFeesLogSerializer
    queryset = WaterFeesLog.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return WaterFeesLogSerializer
        if self.action == "list":
            return WaterFeesLogSerializer
        return WaterFeesLogSerializer

    def get_permissions(self):
        if self.action == "retrieve":
            return [IsAuthenticated(), FeesLogIsSelf()]
        if self.action == "list":
            return [IsAuthenticated()]
        return []

    """
    def retrieve(self, request, *args, **kwargs):
        显示单个水费使用记录
        url: '/water_fees_log/<pk>/'
        type: 'get'
    """

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


class ElectricityFeesLogViewset(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    宿舍电费 视图类
    """
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = ElectricityFeesLogSerializer
    queryset = ElectricityFeesLog.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ElectricityFeesLogSerializer
        if self.action == "list":
            return ElectricityFeesLogSerializer
        return ElectricityFeesLogSerializer

    def get_permissions(self):
        if self.action == "retrieve":
            return [IsAuthenticated(), FeesLogIsSelf()]
        if self.action == "list":
            return [IsAuthenticated()]
        return []

    """
    def retrieve(self, request, *args, **kwargs):
        显示单个电费使用记录
        url: '/electricity_fees_log/<pk>/'
        type: 'get'
    """

    def list(self, request, *args, **kwargs):
        """
            电费使用记录 列表
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


class RepairViewset(mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.UpdateModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    宿舍报修单 视图类
    """
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = RepairSerializer
    queryset = Repair.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return RepairSerializer
        if self.action == "list":
            return RepairSerializer
        if self.action == "update":
            return RepairSerializer
        if self.action == "create":
            return RepairCreateSerializer
        return RepairSerializer

    def get_permissions(self):
        if self.action == "retrieve":
            return [IsAuthenticated(), RepairIsSelf()]
        if self.action == "list":
            return [IsAuthenticated()]
        if self.action == "update":
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "create":
            return [IsAuthenticated()]
        return []

    """
    def retrieve(self, request, *args, **kwargs):
        显示单个宿舍报修单
        url: '/repair/<pk>/'
        type: 'get'
    """

    def list(self, request, *args, **kwargs):
        """
            宿舍报修单 列表
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

    def update(self, request, *args, **kwargs):
        """
            报修单 修改
            url: '/repair/<pk>/'
            type: 'put'
            dataType: 'json'
            data: {
                'title': '<title>',
                'content': '<content>',
                'status': '<status>'
            }
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        system_log = SystemLog.objects.create(content='修改报修单（编号：' + str(instance.id) + '，标题：' + instance.title + '）',
                                              category="报修单管理",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
            报修单 创建
            url: '/repair/'
            type: 'post'
            dataType: 'json'
            data: {
                'title': '<title>',
                'content': '<content>'
            }
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

        system_log = SystemLog.objects.create(content='创建报修单（编号：' + str(repair.id) + '，标题：' + serializer.validated_data["title"] + '）',
                                              category="报修单管理",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        return Response({
            "detail": "创建报修单成功！"
        }, status=status.HTTP_200_OK)

class RepairLogViewset(mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.UpdateModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
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

    """
    def retrieve(self, request, *args, **kwargs):
        显示单个宿舍报修单回复
        url: '/repair_log/<pk>/'
        type: 'get'
    """

    def list(self, request, *args, **kwargs):
        """
            宿舍报修单回复 列表
            url: '/repair_log/<pk>/?search_repair_id=<repair_id>'
            type: 'get'
        """
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

    def update(self, request, *args, **kwargs):
        """
            报修单 修改
            url: '/repair_log/<pk>/'
            type: 'put'
            dataType: 'json'
            data: {
                'reply': '<reply>',
                'reply_type': '<reply_type>'
            }
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        system_log = SystemLog.objects.create(content='修改报修单回复（回复编号：' + str(instance.id) + '）',
                                              category="报修单管理",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
            报修单回复 创建
            url: '/repair_log/'
            type: 'post'
            dataType: 'json'
            data: {
                'main_repair__id': '<main_repair__id>',
                'reply': '<reply>',
                'reply_type': '<reply_type>'
            }
        """
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

        system_log = SystemLog.objects.create(content='创建报修单回复（回复编号：' + str(repair_log.id) + '）',
                                              category="报修单管理",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        return Response({
            "detail": "回复成功！"
        }, status=status.HTTP_200_OK)


class FeesRechargeOrderViewset(viewsets.GenericViewSet):
    """
    充值 订单
    """
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = FeesRechargeOrderCreateSerializer
    queryset = FeesRechargeOrder.objects.all()

    def get_serializer_class(self):
        if self.action == "create_order":
            return FeesRechargeOrderCreateSerializer
        if self.action == "check_order_water":
            return
        if self.action == "check_order_electricity":
            return
        return

    def get_permissions(self):
        if self.action == "create_order":
            return [IsAuthenticated()]
        if self.action == "check_order_water":
            return []
        if self.action == "check_order_electricity":
            return []
        return []

    @action(methods=['POST'], detail=False)
    def create_order(self, request, *args, **kwargs):
        """
            充值订单 创建
            url: '/fees_recharge_order/create_order/'
            type: 'post'
            dataType: 'json'
            data: {
                'price': '<price>',
                'type': '<type>',
                'object': '<object>'
            }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data['object'] == "water":
            return Response({
                'url': 'https://api.xiuxiu888.com/creat_order/?id=' + settings.CODEPAY_ID + '&token=' + settings.CODEPAY_TOKEN + '&price=' + str(
                    serializer.validated_data['price']) + '&pay_id=' + self.request.user.username + '&type=' +
                       serializer.validated_data[
                           'type'] + '&page=1&return_url=http://s1.mc.fyi:11453/fees_recharge_order/check_order_water/'
            }, status=status.HTTP_200_OK)
        if serializer.validated_data['object'] == "electricity":
            return Response({
                'url': 'https://api.xiuxiu888.com/creat_order/?id=' + settings.CODEPAY_ID + '&token=' + settings.CODEPAY_TOKEN + '&price=' + str(
                    serializer.validated_data['price']) + '&pay_id=' + self.request.user.username + '&type=' +
                       serializer.validated_data[
                           'type'] + '&page=1&return_url=http://s1.mc.fyi:11453/fees_recharge_order/check_order_electricity/'
            }, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def check_order_water(self, request, *args, **kwargs):
        """
            302重定向 水费订单检测
        """
        from django.shortcuts import redirect

        order_id = request.GET.get('id', '')
        if order_id == '':
            return Response({
                "detail": "错误代码01：订单号为空，请提交给管理员！"
            }, status=status.HTTP_400_BAD_REQUEST)

        if request.GET.get('userID', '') != settings.CODEPAY_ID:
            return Response({
                "detail": "错误代码02：平台ID为空，请提交给管理员！"
            }, status=status.HTTP_400_BAD_REQUEST)

        pay_no = request.GET.get('pay_no', '')
        if pay_no == '':
            return Response({
                "detail": "错误代码03：流水号为空，请提交给管理员！"
            }, status=status.HTTP_400_BAD_REQUEST)

        price = request.GET.get('price', '')
        if price == '':
            return Response({
                "detail": "错误代码04：金额为空，请提交给管理员！"
            }, status=status.HTTP_400_BAD_REQUEST)

        type = request.GET.get('type', '')
        if type == '':
            return Response({
                "detail": "错误代码05：支付方式为空，请提交给管理员！"
            }, status=status.HTTP_400_BAD_REQUEST)
        if type == '1':
            recharge_type = "alipay"
        if type == '2':
            recharge_type = "qqpay"
        if type == '3':
            recharge_type = "wechar"

        pay_id = request.GET.get('pay_id', '')
        if pay_id == '':
            return Response({
                "detail": "错误代码06-0：充值人为空，请提交给管理员！"
            }, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(username=pay_id).first()
        if user is None:
            return Response({
                "detail": "错误代码06-1：充值人不存在，请提交给管理员！"
            }, status=status.HTTP_400_BAD_REQUEST)
        if user.lived_dormitory is None:
            return Response({
                "detail": "错误代码06-2：充值宿舍不存在，请提交给管理员！"
            }, status=status.HTTP_400_BAD_REQUEST)

        # 判断是否已提交
        if FeesRechargeOrder.objects.filter(pay_id=order_id):
            return Response({
                "detail": "错误代码07：重复提交，请提交给管理员！"
            }, status=status.HTTP_400_BAD_REQUEST)

        # 计算充值数量
        recharge_number = round(float(price) / float(SystemSetting.objects.filter(code='water_fees').first().content), 2)

        # 充值订单创建
        fees_recharge_order = FeesRechargeOrder.objects.create(operator=user,
                                                               price=int(float(price)),
                                                               recharge_dormitory=user.lived_dormitory,
                                                               recharge_object="water",
                                                               recharge_number=recharge_number,
                                                               recharge_type=recharge_type,
                                                               recharge_status="paying",
                                                               pay_id=order_id)
        fees_recharge_order.save()

        # POST检查
        is_pay_result = requests.post(url='https://api.xiuxiu888.com/ispay?id=' + settings.CODEPAY_ID + '&token=' + settings.CODEPAY_TOKEN + '&order_id=' + order_id)
        is_pay_result_json = json.loads(is_pay_result.text)
        print(is_pay_result_json)

        # 充值结果
        if is_pay_result_json['status'] == 0:
            fees_recharge_order.recharge_status = "close"
            fees_recharge_order.save()
        elif is_pay_result_json['status'] == 1 or is_pay_result_json['status'] == 2:
            fees_recharge_order.recharge_status = "success"
            fees_recharge_order.pay_no = pay_no
            fees_recharge_order.save()

        # 修改费用
        user.lived_dormitory.water_fees.have_water_fees += int(float(price))
        user.lived_dormitory.water_fees.save()
        note = "用户" + user.username + "充值(" + str(fees_recharge_order.recharge_number) + "吨," + str(fees_recharge_order.price) + "元,订单号" + fees_recharge_order.pay_id + ",流水号" + fees_recharge_order.pay_no + ")"
        water_fees_log = WaterFeesLog.objects.create(dormitory=user.lived_dormitory,
                                                     mode="add",
                                                     change_money=float(price),
                                                     operator=user,
                                                     note=note)
        water_fees_log.save()


        return redirect(request.get_full_path().replace('/fees_recharge_order/check_order_water/', 'https://api.xiuxiu888.com/demo_show.html'))

    @action(methods=['GET'], detail=False)
    def check_order_electricity(self, request, *args, **kwargs):
        """
            302重定向 电费订单检测
        """
        from django.shortcuts import redirect

        order_id = request.GET.get('id', '')
        if order_id == '':
            return Response({
                "detail": "错误代码01：订单号为空，请提交给管理员！"
            }, status=status.HTTP_400_BAD_REQUEST)

        if request.GET.get('userID', '') != settings.CODEPAY_ID:
            return Response({
                "detail": "错误代码02：平台ID为空，请提交给管理员！"
            }, status=status.HTTP_400_BAD_REQUEST)

        pay_no = request.GET.get('pay_no', '')
        if pay_no == '':
            return Response({
                "detail": "错误代码03：流水号为空，请提交给管理员！"
            }, status=status.HTTP_400_BAD_REQUEST)

        price = request.GET.get('price', '')
        if price == '':
            return Response({
                "detail": "错误代码04：金额为空，请提交给管理员！"
            }, status=status.HTTP_400_BAD_REQUEST)

        type = request.GET.get('type', '')
        if type == '':
            return Response({
                "detail": "错误代码05：支付方式为空，请提交给管理员！"
            }, status=status.HTTP_400_BAD_REQUEST)
        if type == '1':
            recharge_type = "alipay"
        if type == '2':
            recharge_type = "qqpay"
        if type == '3':
            recharge_type = "wechar"

        pay_id = request.GET.get('pay_id', '')
        if pay_id == '':
            return Response({
                "detail": "错误代码06-0：充值人为空，请提交给管理员！"
            }, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(username=pay_id).first()
        if user is None:
            return Response({
                "detail": "错误代码06-1：充值人不存在，请提交给管理员！"
            }, status=status.HTTP_400_BAD_REQUEST)
        if user.lived_dormitory is None:
            return Response({
                "detail": "错误代码06-2：充值宿舍不存在，请提交给管理员！"
            }, status=status.HTTP_400_BAD_REQUEST)

        # 判断是否已提交
        if FeesRechargeOrder.objects.filter(pay_id=order_id):
            return Response({
                "detail": "错误代码07：重复提交，请提交给管理员！"
            }, status=status.HTTP_400_BAD_REQUEST)

        # 计算充值数量
        recharge_number = round(float(price) / float(SystemSetting.objects.filter(code='electricity_fees').first().content), 2)

        # 充值订单创建
        fees_recharge_order = FeesRechargeOrder.objects.create(operator=user,
                                                               price=int(float(price)),
                                                               recharge_dormitory=user.lived_dormitory,
                                                               recharge_object="electricity",
                                                               recharge_number=recharge_number,
                                                               recharge_type=recharge_type,
                                                               recharge_status="paying",
                                                               pay_id=order_id)
        fees_recharge_order.save()

        # POST检查
        is_pay_result = requests.post(
            url='https://api.xiuxiu888.com/ispay?id=' + settings.CODEPAY_ID + '&token=' + settings.CODEPAY_TOKEN + '&order_id=' + order_id)
        is_pay_result_json = json.loads(is_pay_result.text)
        print(is_pay_result_json)

        # 充值结果
        if is_pay_result_json['status'] == 0:
            fees_recharge_order.recharge_status = "close"
            fees_recharge_order.save()
        elif is_pay_result_json['status'] == 1 or is_pay_result_json['status'] == 2:
            fees_recharge_order.recharge_status = "success"
            fees_recharge_order.pay_no = pay_no
            fees_recharge_order.save()

        # 修改费用
        user.lived_dormitory.electricity_fees.have_electricity_fees += int(float(price))
        user.lived_dormitory.electricity_fees.save()
        note = "用户" + user.username + "充值(" + str(fees_recharge_order.recharge_number) + "度," + str(fees_recharge_order.price) + "元,订单号" + fees_recharge_order.pay_id + ",流水号" + fees_recharge_order.pay_no + ")"
        electricity_fees_log = ElectricityFeesLog.objects.create(dormitory=user.lived_dormitory,
                                                                 mode="add",
                                                                 change_money=float(price),
                                                                 operator=user,
                                                                 note=note)
        electricity_fees_log.save()

        return redirect(request.get_full_path().replace('/fees_recharge_order/check_order_electricity/', 'https://api.xiuxiu888.com/demo_show.html'))