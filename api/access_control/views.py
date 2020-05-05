import os
from datetime import datetime, timedelta

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
from system_setting.models import SystemLog
from utils.permission import UserIsSuperUser, AccessControlIsSelf
# Create your views here.


class AccessControlViewset(mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.UpdateModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    门禁记录 视图类
    """
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = AccessControlSerializer
    queryset = AccessControl.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AccessControlSerializer
        if self.action == "list":
            return AccessControlSerializer
        if self.action == "update":
            return AccessControlUpdateSerializer
        if self.action == "create":
            return
        if self.action == "get_abnormal_application_list":
            return AccessControlAbnormalApplicationSerializer
        if self.action == "abnormal_application":
            return AccessControlAbnormalApplicationSerializer
        if self.action == "abnormal_application_create":
            return AccessControlAbnormalApplicationUpdateSerializer
        if self.action == "abnormal_application_update":
            return AccessControlAbnormalApplicationUpdateSerializer
        if self.action == "abnormal_application_reply":
            return AccessControlAbnormalApplicationReplySerializer
        return AccessControlSerializer

    def get_permissions(self):
        if self.action == "retrieve":
            return [IsAuthenticated(), AccessControlIsSelf()]
        if self.action == "list":
            return [IsAuthenticated()]
        if self.action == "update":
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "create":
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "get_abnormal_application_list":
            return [IsAuthenticated()]
        if self.action == "abnormal_application":
            return [IsAuthenticated()]
        if self.action == "abnormal_application_create":
            return [IsAuthenticated(), AccessControlIsSelf()]
        if self.action == "abnormal_application_update":
            return [IsAuthenticated(), AccessControlIsSelf()]
        if self.action == "abnormal_application_reply":
            return [IsAuthenticated(), UserIsSuperUser()]
        return []

    """
    def retrieve(self, request, *args, **kwargs):
        显示单个门禁记录
        url: '/access_control/<pk>/'
        type: 'get'
    """

    def list(self, request, *args, **kwargs):
        """
            显示单个门禁记录
            url: '/access_control/'
            type: 'get'
        """
        from django.db.models import Q,F
        import math

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
        # 总页数（向上取整）
        pages = math.ceil(recordsTotal / limit)

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
            dataType: 'json'
            data: {
                'status': '<status>',
                'note': '<note>'
            }
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        instance.status = serializer.validated_data["status"]
        instance.note = serializer.validated_data["note"]
        instance.save()

        system_log = SystemLog.objects.create(content='修改门禁记录（编号：' + str(instance.id) + '）',
                                              category="门禁管理",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        return Response({
            "detail": "操作成功：门禁记录修改成功！"
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
            门禁记录 创建
            url: '/access_control/?user_id=<user_id>&euclidean_distance=<euclidean_distance>'
            type: 'post'
            dataType: 'json'
            data: file
        """
        from utils.save_file import save_img_and_crop_1_1
        image = request.FILES.get("file")
        flag = save_img_and_crop_1_1(image, "users/access_control")
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

        if float(request.GET.get('euclidean_distance', '')) < 0.2:
            accuracy = 100
        else:
            accuracy = (1.2 - float(request.GET.get('euclidean_distance', ''))) * 100

        access_control_list = AccessControl.objects.filter(person_id=request.GET.get('user_id', '')).order_by("-add_time")
        if access_control_list:
            last_access_control = access_control_list[0]
            five_minutes_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
            if five_minutes_ago < last_access_control.add_time:
                os.remove('media/' + flag)
                return Response({
                    "detail": "操作成功：五分钟内此人已通过门禁，已自动放行。"
                }, status=status.HTTP_200_OK)

        access_control = AccessControl.objects.create(photo=flag,
                                                      accuracy=accuracy,
                                                      add_time=datetime.now(),
                                                      person_id=request.GET.get('user_id', ''),
                                                      status="normal")
        access_control.save()

        return Response({
            "detail": "操作成功：门禁记录已上传！"
        }, status=status.HTTP_201_CREATED)

    @action(methods=['GET'], detail=False)
    def get_abnormal_application_list(self, request, *args, **kwargs):
        """
            门禁记录 识别异常申请 列表
            url: '/access_control/get_abnormal_application_list/'
            type: 'get'
        """
        from django.db.models import Q, F
        import math

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
        pages = math.ceil(recordsTotal / limit)

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
        if hasattr(self.get_object(), "abnormal_application"):
            instance = self.get_object().abnormal_application
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        else:
            return Response({
                "id": "0"
            }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    def abnormal_application_create(self, request, *args, **kwargs):
        """
            门禁记录 识别异常申请 创建
            url: '/access_control/<pk>/abnormal_application_create/'
            type: 'post'
            dataType: 'json'
            data: {
                'content': '<content>'
            }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        access_control_abnormal_application = AccessControlAbnormalApplication.objects.create(result="pending",
                                                                                              add_time=datetime.now(),
                                                                                              main_record_id=self.get_object().id,
                                                                                              reply="",
                                                                                              content=serializer.validated_data['content'])
        access_control_abnormal_application.save()

        system_log = SystemLog.objects.create(content='创建门禁异常申请（申请编号：' + str(access_control_abnormal_application.id) + '）',
                                              category="门禁管理",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        return Response({
            "detail": "操作成功：门禁记录异常申请已提交！"
        }, status=status.HTTP_200_OK)


    @action(methods=['POST'], detail=True)
    def abnormal_application_update(self, request, *args, **kwargs):
        """
            门禁记录 识别异常申请 修改
            url: '/access_control/<pk>/abnormal_application_update/'
            type: 'post'
            dataType: 'json'
            data: {
                'content': '<content>'
            }
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

        system_log = SystemLog.objects.create(content='创建门禁异常申请（申请编号：' + str(instance.abnormal_application.id) + '）',
                                              category="门禁管理",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        return Response(serializer.data)

    @action(methods=['POST'], detail=True)
    def abnormal_application_reply(self, request, *args, **kwargs):
        """
            门禁记录 识别异常申请 回复
            url: '/access_control/<pk>/abnormal_application_reply/'
            type: 'post'
            dataType: 'json'
            data: {
                'result': '<result>',
                'reply': '<reply>'
            }
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

        system_log = SystemLog.objects.create(content='门禁异常申请回复（申请编号：' + str(instance.abnormal_application.id) + '）',
                                              category="门禁管理",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        return Response(serializer.data)
