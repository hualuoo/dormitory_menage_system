from django.shortcuts import render
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework import status

from .models import AccessControl, AccessControlAbnormalApplication
from .serializers import AccessControlSerializer, AccessControlUpdateSerializer, AccessControlAbnormalApplicationSerializer, AccessControlAbnormalApplicationUpdateSerializer, AccessControlAbnormalApplicationReplySerializer
from utils.permission import UserIsSuperUser, AccessControlIsSelf
# Create your views here.


class AccessControlViewset(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    门禁记录 视图类
    """
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = AccessControlSerializer
    queryset = AccessControl.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return AccessControlSerializer
        if self.action == "retrieve":
            return AccessControlSerializer
        if self.action == "update":
            return AccessControlUpdateSerializer
        if self.action == "get_abnormal_application_list":
            return AccessControlAbnormalApplicationSerializer
        if self.action == "abnormal_application":
            return AccessControlAbnormalApplicationSerializer
        if self.action == "abnormal_application_update":
            return AccessControlAbnormalApplicationUpdateSerializer
        if self.action == "abnormal_application_reply":
            return AccessControlAbnormalApplicationReplySerializer
        return AccessControlSerializer

    def get_permissions(self):
        if self.action == "list":
            return [IsAuthenticated()]
        if self.action == "retrieve":
            return [IsAuthenticated(), AccessControlIsSelf()]
        if self.action == "update":
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "get_abnormal_application_list":
            return [IsAuthenticated()]
        if self.action == "abnormal_application":
            return [IsAuthenticated()]
        if self.action == "abnormal_application_update":
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "abnormal_application_reply":
            return [IsAuthenticated(), UserIsSuperUser()]
        return []

    def list(self, request, *args, **kwargs):
        from django.db.models import Q,F

        # 获取全部门禁通过记录数据
        all_result = self.filter_queryset(self.get_queryset())

        # 如果非管理员，仅搜索该用户
        if request.user.is_superuser is False:
            all_result = all_result.filter(Q(person=request.user))

        # 默认按创建时间倒数排序
        all_result = all_result.order_by(F("add_time").desc())

        # 分页页数
        page = int(request.GET.get('page', '1'))
        # 每页条数
        limit = int(request.GET.get('limit', '10'))

        # 根据状态查询
        search_status = request.GET.get('search_status', '')
        if search_status and search_status != "all":
            all_result = all_result.filter(Q(status=search_status))

        # 模糊搜索关键词
        search_firstname = request.GET.get('search_firstname', '')
        search_lastname = request.GET.get('search_lastname', '')
        search_username = request.GET.get('search_username', '')
        search_mobile = request.GET.get('search_mobile', '')
        search_email = request.GET.get('search_email', '')

        # 搜索
        if search_username:
            all_result = all_result.filter(Q(person__username__icontains=search_username))
        if search_firstname:
            all_result = all_result.filter(Q(person__first_name__icontains=search_firstname))
        if search_lastname:
            all_result = all_result.filter(Q(person__last_name__icontains=search_lastname))
        if search_email:
            all_result = all_result.filter(Q(person__email__icontains=search_email))
        if search_mobile:
            all_result = all_result.filter(Q(person__info__mobile__icontains=search_mobile))

        # 数据条数
        recordsTotal = all_result.count()
        # 总页数
        pages = int(recordsTotal / limit) + 1

        # 获取首页的数据
        if (page != 0) and (limit != 0):
            all_result = all_result[(page * limit - limit):(page * limit)]

        recordsNumber = all_result.count()

        queryset = self.filter_queryset(all_result)
        serializer = self.get_serializer(queryset, many=True)

        return Response(
            {
                'code': 0,
                'msg': '',
                'pages': pages,
                'recordsNumber': recordsNumber,
                'data': serializer.data
            })

    def update(self, request, *args, **kwargs):
        """
            门禁记录 修改
            url: '/access_control/<pk>/'
            type: 'put'
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        instance.status = serializer.validated_data["status"]
        instance.note = serializer.validated_data["note"]
        instance.save()

        return Response({
            'msg': "操作成功：修改成功！"
        }, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def get_abnormal_application_list(self, request, *args, **kwargs):
        """
            门禁记录 识别异常申请 列表
            url: '/access_control/get_abnormal_application_list/'
            type: 'get'
        """
        from django.db.models import Q, F

        # 获取全部门禁通过记录数据
        all_result = AccessControlAbnormalApplication.objects.filter()

        # 如果非管理员，仅搜索该用户
        if request.user.is_superuser is False:
            all_result = all_result.filter(Q(main_record__person=request.user))

        # 默认按创建时间倒数排序
        all_result = all_result.order_by(F("add_time").desc())

        # 分页页数
        page = int(request.GET.get('page', '1'))
        # 每页条数
        limit = int(request.GET.get('limit', '10'))

        # 根据状态查询
        is_pending = request.GET.get('is_pending', '')
        if is_pending == "false":
            all_result = all_result.filter(~Q(result="pending"))
        if is_pending == "true":
            all_result = all_result.filter(Q(result="pending"))

        # 模糊搜索关键词
        search_firstname = request.GET.get('search_firstname', '')
        search_lastname = request.GET.get('search_lastname', '')
        search_username = request.GET.get('search_username', '')
        search_mobile = request.GET.get('search_mobile', '')
        search_email = request.GET.get('search_email', '')

        # 搜索
        if search_username:
            all_result = all_result.filter(Q(main_record__person__username__icontains=search_username))
        if search_firstname:
            all_result = all_result.filter(Q(main_record__person__first_name__icontains=search_firstname))
        if search_lastname:
            all_result = all_result.filter(Q(main_record__person__last_name__icontains=search_lastname))
        if search_email:
            all_result = all_result.filter(Q(main_record__person__email__icontains=search_email))
        if search_mobile:
            all_result = all_result.filter(Q(main_record__person__info__mobile__icontains=search_mobile))

        # 数据条数
        recordsTotal = all_result.count()
        # 总页数
        pages = int(recordsTotal / limit) + 1

        # 获取首页的数据
        if (page != 0) and (limit != 0):
            all_result = all_result[(page * limit - limit):(page * limit)]

        recordsNumber = all_result.count()

        queryset = self.filter_queryset(all_result)
        serializer = self.get_serializer(queryset, many=True)

        return Response(
            {
                'code': 0,
                'msg': '',
                'pages': pages,
                'recordsNumber': recordsNumber,
                'data': serializer.data
            })

    @action(methods=['GET'], detail=True)
    def abnormal_application(self, request, *args, **kwargs):
        """
            门禁记录 识别异常申请
            url: '/access_control/<pk>/abnormal_application/'
            type: 'get'
        """
        instance = self.get_object().abnormal_application
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True)
    def abnormal_application_update(self, request, *args, **kwargs):
        """
            门禁记录 识别异常申请 修改
            url: '/access_control/<pk>/abnormal_application_update/'
            type: 'post'
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object().abnormal_application
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    @action(methods=['POST'], detail=True)
    def abnormal_application_reply(self, request, *args, **kwargs):
        """
            门禁记录 识别异常申请 回复
            url: '/access_control/<pk>/abnormal_application_reply/'
            type: 'post'
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        abnormal_application = instance.abnormal_application
        serializer = self.get_serializer(abnormal_application, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(abnormal_application, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            abnormal_application._prefetched_objects_cache = {}

        if serializer.validated_data["result"] == "pass":
            instance.status = "abnormal"
            instance.save()
        if serializer.validated_data["result"] == "fail":
            instance.status = "normal"
            instance.save()
        if serializer.validated_data["result"] == "pending":
            instance.status = "normal"
            instance.save()

        return Response(serializer.data)

