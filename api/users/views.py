from random import choice
from datetime import datetime,timedelta

from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import User, UserInfo, UserFace, CaptchaModel, QQLoginTokenModel
from .serializers import UserSerializer, UserCreateSerializer, UserCreateMultipleSerializer, UserUpdateSerializer
from .serializers import UserResetPasswordSerializer, UserResetPasswordMultipleSerializer, UserCheckIdsSerializer
from .serializers import UserFaceListSerializer
from .serializers import UserChangePasswordAdminSerializer
from .serializers import SecurityCheckOldEmailSerializer, SecurityConfirmOldEmailSerializer, SecurityChangeMobileSerializer, SecuritySendNewEmailCaptchaSerializer
from .serializers import SecurityChangeEmailSerializer, SecurityChangePasswordSerializer
from .serializers import SecurityCheckAccountPasswordSerializer, SecuritySendBindEmailCaptchaSerializer, SecurityBindEmailSerializer
from system_setting.models import SystemLog
from utils import smtp
from utils.permission import UserIsSuperUser, UserIsSelf
# Create your views here.


class UserViewset(mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.UpdateModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    用户 视图类
    """
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return UserSerializer
        if self.action == "retrieve":
            return UserSerializer
        if self.action == "update":
            return UserUpdateSerializer
        if self.action == "create":
            return UserCreateSerializer
        if self.action == "create_multiple":
            return UserCreateMultipleSerializer
        if self.action == "reset_password":
            return UserResetPasswordSerializer
        if self.action == "reset_password_multiple":
            return UserResetPasswordMultipleSerializer
        if self.action == "set_inactive":
            return
        if self.action == "set_inactive_multiple":
            return UserCheckIdsSerializer
        if self.action == "set_active":
            return
        if self.action == "set_active_multiple":
            return UserCheckIdsSerializer
        if self.action == "set_avatar":
            return
        if self.action == "remove_avatar":
            return
        if self.action == "get_face_list":
            return UserFaceListSerializer
        if self.action == "set_face":
            return
        if self.action == "get_info_self":
            return UserSerializer
        if self.action == "change_password_admin":
            return UserChangePasswordAdminSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == "list":
            return [IsAuthenticated()]
        if self.action == "retrieve":
            return [IsAuthenticated(), UserIsSelf()]
        if self.action == "update":
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "create":
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "create_multiple":
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "reset_password":
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "reset_password_multiple":
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "set_inactive":
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "set_inactive_multiple":
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "set_active":
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "set_active_multiple":
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "set_avatar":
            return [IsAuthenticated(), UserIsSelf()]
        if self.action == "remove_avatar":
            return [IsAuthenticated(), UserIsSelf()]
        if self.action == "get_face_list":
            return [IsAuthenticated()]
        if self.action == "set_face":
            return [IsAuthenticated(), UserIsSelf()]
        if self.action == "get_info_self":
            return [IsAuthenticated()]
        if self.action == "change_password_admin":
            return [IsAuthenticated(), UserIsSuperUser()]
        return []
    """
    def retrieve(self, request, *args, **kwargs):
        显示单个用户信息
        url: '/users/<pk>/'
        type: 'get'
    """

    def list(self, request, *args, **kwargs):
        """
            显示用户信息列表
            url: '/users/<pk>/'
            type: 'get'
        """
        """
        ##############################
        # 此处适配DataTable服务端模式
        ##############################
        from django.db.models import Q, F

        # 获取全部数据
        all_result = self.filter_queryset(self.get_queryset())

        # 数据条数
        recordsTotal = all_result.count()
        recordsFiltered = recordsTotal

        # 第一条数据的起始位置
        start = int(request.GET['start'])
        # 每页显示的长度，默认为10
        length = int(request.GET['length'])
        # 计数器，确保ajax从服务器返回是对应的
        draw = int(request.GET['draw'])
        # 全局收索条件
        new_search = request.GET['search[value]']
        # 排序列的序号
        new_order = request.GET['order[0][column]']
        # 排序列名
        by_name = request.GET['columns[{0}][data]'.format(new_order)]
        # 排序类型，升序降序
        fun_order = request.GET['order[0][dir]']

        # 替换字符串进行外链查询
        new_search = new_search.replace(".", "__")
        by_name = by_name.replace(".", "__")

        # 排序开启，匹配表格列，空值排最后
        if by_name:
            if fun_order == "asc":
                all_result = all_result.order_by(F(by_name).asc(nulls_last=True))
            else:
                all_result = all_result.order_by(F(by_name).desc(nulls_last=True))

        # 模糊查询，包含内容就查询
        if new_search:
            all_result = all_result.filter(Q(id__contains=new_search) | Q(username__contains=new_search) |
                                           Q(last_login__contains=new_search) | Q(date_joined__contains=new_search) |
                                           Q(email__contains=new_search) | Q(userinfo__realname__contains=new_search) |
                                           Q(userinfo__birthday__contains=new_search) | Q(userinfo__gender__contains=new_search) |
                                           Q(userinfo__mobile__contains=new_search))

        # 获取首页的数据
        datas = all_result[start:(start + length)]

        queryset = self.filter_queryset(datas)
        serializer = self.get_serializer(queryset, many=True)

        return Response(
            {
                'draw': draw,
                'recordsTotal': recordsTotal,
                'recordsFiltered': recordsFiltered,
                'data': serializer.data
            })
        """
        ##############################
        # 此处适配LayUI Table服务端模式
        ##############################
        from django.db.models import Q, F

        # 获取全部数据
        all_result = self.filter_queryset(self.get_queryset())

        # 如果非管理员，仅搜索该用户
        if request.user.is_superuser is False:
            all_result = all_result.filter(Q(username=request.user))

        # 分页页数
        page = int(request.GET.get('page', '1'))
        # 每页条数
        limit = int(request.GET.get('limit', '10'))

        # 是否为非冻结用户
        is_active = request.GET.get('is_active', '')
        # 是否为教师
        is_staff = request.GET.get('is_staff', '')

        # 排序列名
        field = request.GET.get('field', '')
        # 排序类型，升序降序
        order = request.GET.get('order', '')
        # 模糊搜索关键词
        search_firstname = request.GET.get('search_firstname', '')
        search_lastname = request.GET.get('search_lastname', '')
        search_username = request.GET.get('search_username', '')
        search_mobile = request.GET.get('search_mobile', '')
        search_email = request.GET.get('search_email', '')

        # 是否为非冻结用户
        if is_active == 'true':
            all_result = all_result.filter(Q(is_active=True))
        if is_active == 'false':
            all_result = all_result.filter(Q(is_active=False))

        # 是否为教师
        if is_staff == 'true':
            all_result = all_result.filter(Q(is_staff=True))
        if is_staff == 'false':
            all_result = all_result.filter(Q(is_staff=False))

        # 排序
        if field:
            if order == "asc":
                all_result = all_result.order_by(F(field).asc(nulls_last=True))
            elif order == "desc":
                all_result = all_result.order_by(F(field).desc(nulls_last=True))

        # 搜索
        if search_username:
            all_result = all_result.filter(Q(username__icontains=search_username))
        if search_firstname:
            all_result = all_result.filter(Q(first_name__icontains=search_firstname))
        if search_lastname:
            all_result = all_result.filter(Q(last_name__icontains=search_lastname))
        if search_email:
            all_result = all_result.filter(Q(email__icontains=search_email))
        if search_mobile:
            all_result = all_result.filter(Q(userinfo__mobile__icontains=search_mobile))

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
            用户 修改
            url: '/users/<pk>/'
            type: 'put'
            dataType: 'json'
            data: {
                'email': '<email>',
                'info__mobile': '<info__mobile>',
                'first_name': '<first_name>',
                'last_name': '<last_name>',
                'info__birthday': '<info__birthday>',
                'info__gender': '<info__gender>'
            }
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        system_log = SystemLog.objects.create(content='修改用户信息（用户名：' + instance.username + '）',
                                              category="用户管理",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
            管理员创建单个用户
            url: '/users/'
            type: 'post'
            dataType: 'json'
            data: {
                'username': '<username>',
                'password': '<password>'
            }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.create(username=serializer.validated_data["username"],
                                   date_joined=datetime.now(),
                                   is_staff=serializer.validated_data["is_staff"])
        user.set_password(serializer.validated_data["password"])
        user.save()
        info = UserInfo.objects.create(user=user)
        info.save()

        system_log = SystemLog.objects.create(content='创建单个用户（用户名：' + serializer.validated_data["username"] + '）',
                                              category="用户管理",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=False)
    def create_multiple(self, request, *args, **kwargs):
        """
            管理员创建批量用户
            url: '/users/create_multiple/'
            type: 'post'
            dataType: 'json'
            data: {
                'first_username': '<first_username>',
                'create_number': '<create_number>',
                'password': '<password>'
            }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        first_username = serializer.validated_data["first_username"]
        create_number = serializer.validated_data["create_number"]
        for username in range(first_username, first_username + create_number):
            user = User.objects.create(username=username)
            user.set_password(serializer.validated_data["password"])
            user.save()
            info = UserInfo.objects.create(user=user)
            info.save()

        system_log = SystemLog.objects.create(content='创建批量用户（首用户名：' + str(serializer.validated_data["first_username"]) + '，创建数量：' + str(serializer.validated_data["create_number"]) + '）',
                                              category="用户管理",
                                              operator=request.user,
                                              ip=request.META.get('REMOTE_ADDR'))
        system_log.save()

        return Response({
            "detail": "操作成功：" + str(first_username) + "-" + str(username) + "账户已被创建！"
        }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    def reset_password(self, request, *args, **kwargs):
        """
            管理员重置单个用户密码
            url: '/users/<pk>/reset_password/'
            type: 'post'
            dataType: 'json'
            data: {
                'password': '<password>'
            }
        """
        if request.user == self.get_object():
            return Response({
                "detail": "操作失败：您无法操作自己！"
            }, status=status.HTTP_400_BAD_REQUEST)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        instance.set_password(serializer.validated_data["password"])
        instance.save()
        system_log = SystemLog.objects.create(content='重置单个用户密码（用户名：' + instance.username + '）',
                                              category="用户管理",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()
        return Response({
            "detail": "操作成功：用户" + instance.username + "的密码修改成功！"
        }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def reset_password_multiple(self, request, *args, **kwargs):
        """
            管理员批量重置用户密码
            url: '/users/reset_password_multiple/'
            type: 'post'
            dataType: 'json'
            data: {
                'ids': '<pk1>,<pk2>,<pk3>',
                'password': '<password>'
            }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ids = serializer.validated_data["ids"].split(',')
        for i in ids:
            user = User.objects.filter(id=i).first()
            user.set_password(serializer.validated_data["password"])
            user.save()

        system_log = SystemLog.objects.create(content='批量重置用户密码（用户名组：' + serializer.validated_data["ids"] + '）',
                                              category="用户管理",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        return Response({
            "detail": "操作成功：所选用户账户密码已重置！"
        }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    def set_inactive(self, request, *args, **kwargs):
        """
            禁用用户
            url: '/users/<pk>/set_inactive/'
            type: 'post'
            data: None
        """
        if request.user == self.get_object():
            return Response({
                "detail": "操作失败：您无法操作自己！"
            }, status=status.HTTP_400_BAD_REQUEST)
        user = self.get_object()
        user.is_active = False
        user.save()

        system_log = SystemLog.objects.create(content='禁用单个用户（用户名：' + user.username + '）',
                                              category="用户管理",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        return Response({
            "detail": "操作成功：用户" + user.username + "已被禁用！"
        }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def set_inactive_multiple(self, request, *args, **kwargs):
        """
            批量禁用用户
            url: '/users/set_inactive_multiple/'
            type: 'post'
            dataType: 'json'
            data: {
                'ids': '<pk1>,<pk2>,<pk3>'
            }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ids = serializer.validated_data["ids"].split(',')
        for i in ids:
            user = User.objects.filter(id=i).first()
            user.is_active = False
            user.save()

        system_log = SystemLog.objects.create(content='批量禁用用户（用户名组：' + serializer.validated_data["ids"] + '）',
                                              category="用户管理",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        return Response({
            "detail": "操作成功：所选用户账户已被禁用！"
        }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    def set_active(self, request, *args, **kwargs):
        """
            启用用户
            url: '/users/<pk>/set_active/'
            type: 'post'
            data: None
        """
        if request.user == self.get_object():
            return Response({
                "detail": "操作失败：您无法操作自己！"
            }, status=status.HTTP_400_BAD_REQUEST)

        user = self.get_object()
        user.is_active = True
        user.save()

        system_log = SystemLog.objects.create(content='启用单个用户（用户名：' + user.username + '）',
                                              category="用户管理",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        return Response({
            "detail": "用户" + user.username + "已被启用！"
        }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def set_active_multiple(self, request, *args, **kwargs):
        """
            批量启用用户
            url: '/users/set_active_multiple/'
            type: 'post'
            dataType: 'json'
            data: {
                'ids': '<pk1>,<pk2>,<pk3>'
            }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ids = serializer.validated_data["ids"].split(',')
        for i in ids:
            user = User.objects.filter(id=i).first()
            user.is_active = True
            user.save()

        system_log = SystemLog.objects.create(content='批量启用用户（用户名组：' + serializer.validated_data["ids"] + '）',
                                              category="用户管理",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        return Response({
            "detail": "操作成功：所选用户账户已被启用！"
        }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    def set_avatar(self, request, *args, **kwargs):
        """
            上传头像
            url: '/users/<pk>/set_avatar/'
            type: 'post'
            data: None
        """
        from utils.save_file import save_img_and_crop_1_1

        avatar = request.FILES.get("file")

        flag = save_img_and_crop_1_1(avatar, "users/avatar")
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

        instance = self.get_object()
        instance.info.avatar = flag
        instance.info.save()

        system_log = SystemLog.objects.create(content='设置头像（用户名：' + instance.username + '）',
                                              category="用户管理",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        return Response({
            "code": 0,
            "msg": "操作成功：头像上传成功",
            "data": {
                "src": "http://" + request.META['HTTP_HOST'] + "/media/" + flag
            }
        }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    def remove_avatar(self, request, *args, **kwargs):
        """
            清除头像
            url: '/users/<pk>/remove_avatar/'
            type: 'post'
            data: None
        """
        instance = self.get_object()
        instance.info.avatar = ""
        instance.info.save()

        system_log = SystemLog.objects.create(content='清除头像（用户名：' + instance.username + '）',
                                              category="用户管理",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        return Response({
            "detail": "操作成功：已清理 " + instance.username + " 账户的头像！"
        }, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def get_face_list(self, request, *args, **kwargs):
        """
            获取人脸列表
            url: '/users/get_face_list/'
            type: 'get'
        """
        from django.db.models import Q

        # 获取全部非冻结用户数据
        all_result = self.filter_queryset(self.get_queryset())
        all_result = all_result.filter(Q(is_active=True))

        # 如果非管理员，仅搜索该用户
        if request.user.is_superuser is False:
            all_result = all_result.filter(Q(username=request.user))

        # 根据状态查询
        is_set = request.GET.get('is_set', '')
        if is_set and is_set == "false":
            all_result = all_result.filter(Q(face__isnull=True))
        if is_set and is_set == "true":
            all_result = all_result.filter(Q(face__isnull=False))

        # 分页页数
        page = int(request.GET.get('page', '1'))
        # 每页条数
        limit = int(request.GET.get('limit', '10'))

        # 模糊搜索关键词
        search_firstname = request.GET.get('search_firstname', '')
        search_lastname = request.GET.get('search_lastname', '')
        search_username = request.GET.get('search_username', '')
        search_mobile = request.GET.get('search_mobile', '')
        search_email = request.GET.get('search_email', '')

        # 搜索
        if search_username:
            all_result = all_result.filter(Q(username__icontains=search_username))
        if search_firstname:
            all_result = all_result.filter(Q(first_name__icontains=search_firstname))
        if search_lastname:
            all_result = all_result.filter(Q(last_name__icontains=search_lastname))
        if search_email:
            all_result = all_result.filter(Q(email__icontains=search_email))
        if search_mobile:
            all_result = all_result.filter(Q(info__mobile__icontains=search_mobile))

        # 数据条数
        recordsTotal = all_result.count()
        # 总页数
        pages = int(recordsTotal/limit)+1

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

    @action(methods=['POST'], detail=True)
    def set_face(self, request, *args, **kwargs):
        """
            上传人脸
            url: '/users/<pk>/set_face/'
            type: 'post'
            data: file
        """
        from utils.save_file import save_img_and_crop_1_1
        from utils import face_recognition
        from attendance_system import settings
        import json

        image = request.FILES.get("file")
        flag = save_img_and_crop_1_1(image, "users/face_photo")
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

        image_path = settings.MEDIA_ROOT.replace("\\", "/") + "/" + flag
        face_128d_features = face_recognition.return_face_128d_features(image_path)

        if face_128d_features == 0:
            return Response({
                "detail": "操作失败：未检测到人脸，请尝试将人脸置于正中！"
            }, status=status.HTTP_400_BAD_REQUEST)
        if face_128d_features == 1:
            return Response({
                "detail": "操作失败：检测到多张人脸，请保证图片中只保留一人！"
            }, status=status.HTTP_400_BAD_REQUEST)

        face_128d_features_list = []
        for i in face_128d_features:
            face_128d_features_list.append(i)

        instance = self.get_object()
        if hasattr(instance, 'face'):
            instance.face.photo = flag
            instance.face.features = json.dumps(face_128d_features_list)
            instance.face.add_time = datetime.now()
            instance.face.save()
        else:
            face = UserFace.objects.create(photo=flag,
                                           features=json.dumps(face_128d_features_list),
                                           user=instance)
            face.save()

        system_log = SystemLog.objects.create(content='设置人脸（用户名：' + instance.username + '）',
                                              category="用户管理",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        return Response({
            "code": 0,
            "msg": "操作成功：人脸数据设置成功！",
            "data": {
                "src": "http://" + request.META['HTTP_HOST'] + "/media/" + flag
            }
        }, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def get_info_self(self, request, *args, **kwargs):
        """
            获取自己的信息
            url: '/users/get_info_self/'
            type: 'get'
        """
        instance = request.user
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(methods=['POST'], detail=False)
    def change_password_admin(self, request, *args, **kwargs):
        """
            修改密码 - 管理员
            url: '/users/change_password_admin/'
            type: 'post'
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = request.user
        instance.set_password(serializer.validated_data["new_password"])
        instance.save()

        system_log = SystemLog.objects.create(content='修改密码（用户名：' + instance.username + '）',
                                              category="用户管理",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        return Response(serializer.data)


class SecurityViewset(viewsets.GenericViewSet):
    """
    安全系统 视图类
    """
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == "check_old_email":
            return SecurityCheckOldEmailSerializer
        if self.action == "send_old_email_captcha":
            return SecurityCheckOldEmailSerializer
        if self.action == "confirm_old_email_captcha":
            return SecurityConfirmOldEmailSerializer
        if self.action == "change_mobile":
            return SecurityChangeMobileSerializer
        if self.action == "change_password":
            return SecurityChangePasswordSerializer
        if self.action == "send_new_email_captcha":
            return SecuritySendNewEmailCaptchaSerializer
        if self.action == "change_email":
            return SecurityChangeEmailSerializer
        if self.action == "check_account_password":
            return SecurityCheckAccountPasswordSerializer
        if self.action == "send_bind_email_captcha":
            return SecuritySendBindEmailCaptchaSerializer
        if self.action == "bind_email":
            return SecurityBindEmailSerializer
        return UserSerializer
    def get_permissions(self):
        if self.action == "check_old_email":
            return [IsAuthenticated()]
        if self.action == "send_old_email_captcha":
            return [IsAuthenticated()]
        if self.action == "confirm_old_email_captcha":
            return [IsAuthenticated()]
        if self.action == "change_mobile":
            return [IsAuthenticated()]
        if self.action == "change_password":
            return [IsAuthenticated()]
        if self.action == "send_new_email_captcha":
            return [IsAuthenticated()]
        if self.action == "change_email":
            return [IsAuthenticated()]
        if self.action == "check_account_password":
            return [IsAuthenticated()]
        if self.action == "send_bind_email_captcha":
            return [IsAuthenticated()]
        if self.action == "bind_email":
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    @action(methods=['POST'], detail=False)
    def check_old_email(self, request, *args, **kwargs):
        """
            验证旧邮箱
            url: '/member/security/check_old_email/'
            type: 'post'
            dataType: 'json'
            data: {
                'old_email': '<old_email>'
            }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response({
            "detail": "校验成功：邮箱输入正确！"
        }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def send_old_email_captcha(self, request, *args, **kwargs):
        """
            向旧邮箱发送验证码
            url: '/member/security/send_old_email_captcha/'
            type: 'post'
            dataType: 'json'
            data: {
                'old_email': '<old_email>'
            }
        """
        def generate_code():
            """
            生成六位数字的验证码
            """
            seeds = "1234567890"
            random_str = []
            for i in range(6):
                random_str.append(choice(seeds))
            return "".join(random_str)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        captcha_list = CaptchaModel.objects.filter(email=serializer.validated_data['old_email']).order_by("-create_time")
        if captcha_list:
            if captcha_list[0].create_time >= datetime.now() - timedelta(hours=0, minutes=1, seconds=0):
                return Response({
                    "detail": "发送失败：一分钟内只能发送一次验证码！"
                }, status=status.HTTP_400_BAD_REQUEST)

        code = generate_code()
        smtp.code_smtp(serializer.validated_data['old_email'], code)
        captcha = CaptchaModel(email=request.user.email, code=code)
        captcha.save()
        return Response({
            "detail": "验证码发送成功，请查收！"
        }, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=False)
    def confirm_old_email_captcha(self, request, *args, **kwargs):
        """
            校验旧邮箱 验证码
            url: '/member/security/send_old_email_captcha/'
            type: 'post'
            dataType: 'json'
            data: {
                'old_captcha': '<old_captcha>'
            }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({
            "detail": "校验成功：验证码正确！"
        }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def change_mobile(self, request, *args, **kwargs):
        """
            修改手机
            url: '/member/security/change_mobile/'
            type: 'post'
            dataType: 'json'
            data: {
                'old_captcha': '<old_captcha>',
                'new_mobile': '<new_mobile>'
            }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.info.mobile = serializer.validated_data['new_mobile']
        request.user.info.save()

        system_log = SystemLog.objects.create(content='修改手机（用户名：' + request.user.username + '，新手机：' + serializer.validated_data["new_mobile"] + '）',
                                              category="用户管理",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        return Response({
            "detail": "操作成功：手机修改成功！",
            "mobile": serializer.validated_data['new_mobile']
        }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def change_password(self, request, *args, **kwargs):
        """
            修改密码
            url: '/member/security/change_password/'
            type: 'post'
            dataType: 'json'
            data: {
                'old_captcha': '<old_captcha>',
                'new_password': '<new_password>'
            }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()

        system_log = SystemLog.objects.create(content='修改密码（用户名：' + request.user.username + '）',
                                              category="用户管理",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        return Response({
            "detail": "操作成功：账户密码修改成功！"
        }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def send_new_email_captcha(self, request, *args, **kwargs):
        """
            向新邮箱发送验证码
            url: '/member/security/send_new_email_captcha/'
            type: 'post'
            dataType: 'json'
            data: {
                'old_captcha': '<old_captcha>',
                'new_email': '<new_email>'
            }
        """
        def generate_code():
            """
            生成六位数字的验证码
            """
            seeds = "1234567890"
            random_str = []
            for i in range(6):
                random_str.append(choice(seeds))
            return "".join(random_str)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        captcha_list = CaptchaModel.objects.filter(email=serializer.validated_data['new_email']).order_by("-create_time")
        if captcha_list:
            if captcha_list[0].create_time >= datetime.now() - timedelta(hours=0, minutes=1, seconds=0):
                return Response({
                    "detail": "发送失败：一分钟内只能发送一次验证码！"
                }, status=status.HTTP_400_BAD_REQUEST)

        code = generate_code()
        smtp.code_smtp(serializer.validated_data['new_email'], code)
        captcha = CaptchaModel(email=serializer.validated_data['new_email'], code=code)
        captcha.save()
        return Response({
            "detail": "发送成功！"
        }, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=False)
    def change_email(self, request, *args, **kwargs):
        """
            修改邮箱
            url: '/member/security/change_email/'
            type: 'post'
            dataType: 'json'
            data: {
                'new_email': '<new_email>',
                'new_captcha': '<new_captcha>'
            }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.email = serializer.validated_data['new_email']
        request.user.save()

        system_log = SystemLog.objects.create(content='修改邮箱（用户名：' + request.user.username + '，新邮箱：' + serializer.validated_data['new_email'] + '）',
                                              category="用户管理",
                                              operator=request.user,
                                              ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        return Response({
            "detail": "操作成功：邮箱修改成功！",
            "email": serializer.validated_data['new_email']
        }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def check_account_password(self, request, *args, **kwargs):
        """
            验证账户密码
            url: '/member/security/check_account_password/'
            type: 'post'
            dataType: 'json'
            data: {
                'password': '<password>'
            }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({
            "detail": "账户密码验证成功！"
        }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def send_bind_email_captcha(self, request, *args, **kwargs):
        """
            向绑定邮箱发送验证码
            url: '/member/security/send_bind_email_captcha/'
            type: 'post'
            dataType: 'json'
            data: {
                'password': '<password>',
                'bind_email' : '<bind_email>'
            }
        """
        def generate_code():
            """
            生成六位数字的验证码
            """
            seeds = "1234567890"
            random_str = []
            for i in range(6):
                random_str.append(choice(seeds))
            return "".join(random_str)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        captcha_list = CaptchaModel.objects.filter(email=serializer.validated_data['bind_email']).order_by("-create_time")
        if captcha_list:
            if captcha_list[0].create_time >= datetime.now() - timedelta(hours=0, minutes=1, seconds=0):
                return Response({
                    "detail": "发送失败：一分钟内只能发送一次验证码！"
                }, status=status.HTTP_400_BAD_REQUEST)

        code = generate_code()
        smtp.code_smtp(serializer.validated_data['bind_email'], code)
        captcha = CaptchaModel(email=serializer.validated_data['bind_email'], code=code)
        captcha.save()
        return Response({
            "detail": "发送成功！"
        }, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=False)
    def bind_email(self, request, *args, **kwargs):
        """
            绑定邮箱
            url: '/member/security/bind_email/'
            type: 'post'
            dataType: 'json'
            data: {
                'bind_email' : '<bind_email>',
                'bind_captcha': '<bind_captcha>',
            }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.email = serializer.validated_data['bind_email']
        request.user.save()

        system_log = SystemLog.objects.create(
            content='绑定邮箱（用户名：' + request.user.username + '，新邮箱：' + serializer.validated_data['bind_email'] + '）',
            category="用户管理",
            operator=request.user,
            ip=request.META.get("REMOTE_ADDR"))
        system_log.save()

        return Response({
            "detail": "操作成功：邮箱绑定成功！",
            "email": serializer.validated_data['bind_email']
        }, status=status.HTTP_200_OK)


class QQLoginViewset(viewsets.GenericViewSet):
    serializer_class = UserSerializer

    @action(methods=['GET'], detail=False)
    def login(self, request, *args, **kwargs):
        import requests, json
        from django.conf import settings
        from rest_framework_jwt.settings import api_settings
        from django.shortcuts import redirect

        code = request.GET.get('code', '')
        state = request.GET.get('state', '')
        if code == '' or state == '':
            return redirect('http://s1.mc.fyi:11455/views/qqlogin.html?error_code=99999')
        if state == 'bind':
            return redirect('http://s1.mc.fyi:11455/views/qqlogin.html?code='+code)

        token_result = requests.get(url='https://graph.qq.com/oauth2.0/token?grant_type=authorization_code&client_id=' + settings.QQCONNECT_ID + '&client_secret=' + settings.QQCONNECT_KEY + '&code=' + code + '&redirect_uri=http://hl.acgxt.com:11453/user/login_qq/login?code=' + code + '&state=' + state)
        if 'callback' in token_result.text:
            token_result_json = json.loads(token_result.text.replace('callback( ', '').replace(' );', ''))
            return redirect('http://s1.mc.fyi:11455/views/qqlogin.html?error_code=' + token_result_json['error'])
        else:
            token_result_json = {}
            token_result_list = token_result.text.split('&')
            for i in token_result_list:
                temp = i.split('=')
                token_result_json[temp[0]] = temp[1]

        me_result = requests.get(url='https://graph.qq.com/oauth2.0/me?access_token=' + token_result_json['access_token'])
        me_result_json = json.loads(me_result.text.replace('callback( ', '').replace(' );', ''))
        if me_result_json['client_id'] != settings.QQCONNECT_ID:
            return redirect('http://s1.mc.fyi:11455/views/qqlogin.html?error_code=99998')

        if state == 'login':
            if QQLoginTokenModel.objects.filter(openid=me_result_json['openid']):
                qq_login_token = QQLoginTokenModel.objects.filter(openid=me_result_json['openid']).first()
                jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
                jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
                payload = jwt_payload_handler(qq_login_token.user)
                token = jwt_encode_handler(payload)
                return redirect('http://s1.mc.fyi:11455/views/qqlogin.html?token=' + token)
            else:
                return redirect('http://s1.mc.fyi:11455/views/qqlogin.html?error_code=99997')

    @action(methods=['POST'], detail=False)
    def bind(self, request, *args, **kwargs):
        import requests, json
        from django.conf import settings

        code = request.GET.get('code', '')
        if code == '':
            return Response({
                "error_code": "99999"
            }, status=status.HTTP_400_BAD_REQUEST)

        token_result = requests.get(url='https://graph.qq.com/oauth2.0/token?grant_type=authorization_code&client_id=' + settings.QQCONNECT_ID + '&client_secret=' + settings.QQCONNECT_KEY + '&code=' + code + '&redirect_uri=http://hl.acgxt.com:11453/user/login_qq/login?code=' + code + '&state=bind')
        if 'callback' in token_result.text:
            token_result_json = json.loads(token_result.text.replace('callback( ', '').replace(' );', ''))
            return Response({
                "error_code": token_result_json['error']
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            token_result_json = {}
            token_result_list = token_result.text.split('&')
            for i in token_result_list:
                temp = i.split('=')
                token_result_json[temp[0]] = temp[1]

        me_result = requests.get(url='https://graph.qq.com/oauth2.0/me?access_token=' + token_result_json['access_token'])
        me_result_json = json.loads(me_result.text.replace('callback( ', '').replace(' );', ''))
        if me_result_json['client_id'] != settings.QQCONNECT_ID:
            return Response({
                "error_code": "99998"
            }, status=status.HTTP_400_BAD_REQUEST)

        if QQLoginTokenModel.objects.filter(openid=me_result_json['openid']):
            return Response({
                "error_code": "99996"
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            qq_login_token = QQLoginTokenModel.objects.create(access_token=token_result_json['access_token'],
                                                              expires_in=token_result_json['expires_in'],
                                                              refresh_token=token_result_json['refresh_token'],
                                                              user=request.user,
                                                              openid=me_result_json['openid'])
            qq_login_token.save()
            return Response({
                "detail": "绑定成功！"
            }, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def get_bind_info(self, request, *args, **kwargs):
        import requests, json
        from django.conf import settings

        if QQLoginTokenModel.objects.filter(user=request.user):
            qq_login_token = QQLoginTokenModel.objects.filter(user=request.user).first()
            get_user_info_result = requests.get(url='https://graph.qq.com/user/get_user_info?access_token=' + qq_login_token.access_token + '&oauth_consumer_key=' + settings.QQCONNECT_ID + '&openid=' + qq_login_token.openid)
            get_user_info_result_json = json.loads(get_user_info_result.text)
            return Response({
                'nickname': get_user_info_result_json['nickname'],
                'figureurl_qq': get_user_info_result_json['figureurl_qq']
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'detail': '该账户未绑定QQ账户！'
            }, status=status.HTTP_400_BAD_REQUEST)