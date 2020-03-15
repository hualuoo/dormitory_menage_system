from random import choice
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import User, UserInfo, UserFace, CaptchaModel
from .serializers import UserSerializer, UserCreateSerializer, UserCreateMultipleSerializer, UserUpdateSerializer
from .serializers import UserResetPasswordSerializer, UserResetPasswordMultipleSerializer, UserCheckIdsSerializer
from .serializers import UserFaceListSerializer
from .serializers import VerifyCodeSerializer, ChangeEmailSerializer, ChangePasswordSerializer
from .serializers import checkUserMailSerializer, sendOldMailCaptchaSerializer, confirmMailCaptchaSerializer, sendNewMailCaptchaSerializer

from datetime import datetime

from utils import smtp
from utils.permission import UserIsSuperUser, UserIsSelf, UserIsOwner

# Create your views here.


class UserViewset(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
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
        if self.action == "create":
            return UserCreateSerializer
        if self.action == "create_multiple":
            return UserCreateMultipleSerializer
        if self.action == "update":
            return UserUpdateSerializer
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
        if self.action == "get_face_list":
            return UserFaceListSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == "list":
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "retrieve":
            return [IsAuthenticated(), UserIsSelf()]
        if self.action == "create":
            return []
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
            return [IsAuthenticated(), UserIsSuperUser()]
        if self.action == "get_face_list":
            return [IsAuthenticated(), UserIsSuperUser()]
        return []

    """
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

        # 分页页数
        page = int(request.GET.get('page', '0'))
        # 每页条数
        limit = int(request.GET.get('limit', '0'))

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

    @action(methods=['POST'], detail=True)
    def reset_password(self, request, *args, **kwargs):
        """
            重置密码
            url: '/users/<pk>/reset_password/'
            type: 'post'
            dataType: 'json'
            data: {
                'password': '<password>'
            }
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        instance.set_password(serializer.validated_data["password"])
        instance.save()
        return Response({
            "msg": "操作成功：用户" + instance.username + "的密码修改成功"
        }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def reset_password_multiple(self, request, *args, **kwargs):
        """
            批量重置密码
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
        return Response({
            "msg": "操作成功：所选用户账户密码已重置"
        }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    def set_inactive(self, request, *args, **kwargs):
        """
            禁用用户
            url: '/users/<pk>/set_inactive/'
            type: 'post'
        """
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({
            "msg": "用户" + user.username + "已被禁用"
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
        return Response({
            "msg": "操作成功：所选用户账户已被禁用"
        }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    def set_active(self, request, *args, **kwargs):
        """
            启用用户
            url: '/users/<pk>/set_active/'
            type: 'post'
        """
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({
            "msg": "用户" + user.username + "已被启用"
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
        return Response({
            "msg": "操作成功：所选用户账户已被启用"
        }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def create_multiple(self, request, *args, **kwargs):
        """
            批量创建用户
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
        for username in range(first_username, first_username+create_number):
            user = User.objects.create(username=username)
            user.set_password(serializer.validated_data["password"])
            user.save()
            info = UserInfo.objects.create(user=user)
            info.save()

        return Response({
            "msg": "操作成功：" + str(first_username) + "-" + str(username) + "账户已被创建"
        }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=True)
    def set_avatar(self, request, *args, **kwargs):
        """
            上传头像
            url: '/users/<pk>/set_avatar/'
        """
        from utils.save_file import save_img

        avatar = request.FILES.get("file")

        flag = save_img(avatar, "users/avatar")
        if flag == 0:
            return Response({
                "error": "操作失败：未选择上传的文件"
            }, status=status.HTTP_400_BAD_REQUEST)
        if flag == 1:
            return Response({
                "error": "操作失败：上传的文件超过2Mb"
            }, status=status.HTTP_400_BAD_REQUEST)
        if flag == 2:
            return Response({
                "error": "操作失败：上传的文件不属于图片"
            }, status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_object()
        instance.info.avatar = flag
        instance.info.save()
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
        """
        instance = self.get_object()
        instance.info.avatar = ""
        instance.info.save()
        return Response({
            "msg": "操作成功：已清理 " + instance.username + " 账户的头像"
        }, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def get_face_list(self, request, *args, **kwargs):
        from django.db.models import Q

        # 获取全部非冻结用户数据
        all_result = self.filter_queryset(self.get_queryset())
        all_result = all_result.filter(Q(is_active=True))

        # 分页页数
        page = int(request.GET.get('page', '0'))
        # 每页条数
        limit = int(request.GET.get('limit', '0'))

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
        from utils.save_file import save_img
        from utils import face_recognition
        from attendance_system import settings
        import json

        image = request.FILES.get("file")
        flag = save_img(image, "users/face_photo")
        if flag == 0:
            return Response({
                "error": "操作失败：未选择上传的文件"
            }, status=status.HTTP_400_BAD_REQUEST)
        if flag == 1:
            return Response({
                "error": "操作失败：上传的文件超过2Mb"
            }, status=status.HTTP_400_BAD_REQUEST)
        if flag == 2:
            return Response({
                "error": "操作失败：上传的文件不属于图片"
            }, status=status.HTTP_400_BAD_REQUEST)

        image_path = settings.MEDIA_ROOT.replace("\\", "/") + "/" + flag
        face_128d_features = face_recognition.return_face_128d_features(image_path)

        if face_128d_features == 0:
            return Response({
                "error": "操作失败：未检测到人脸"
            }, status=status.HTTP_400_BAD_REQUEST)
        if face_128d_features == 1:
            return Response({
                "error": "操作失败：检测到多张人脸"
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
        return Response({
            "code": 0,
            "msg": "操作成功：人脸数据设置成功",
            "data": {
                "src": "http://" + request.META['HTTP_HOST'] + "/face_photo/" + flag
            }
        }, status=status.HTTP_200_OK)


"""
class UsersViewset(mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = UserRegSerializer
    queryset = UserModel.objects.all()

    def get_permissions(self):
        if self.action == "create":
            return []
        if self.action == "update":
            return [IsAuthenticated(), UserIsOwner(), ]
        return []

    def get_serializer_class(self):
        if self.action == "create":
            return UserRegSerializer
        if self.action == "update":
            return ChangeEmailSerializer
        return UserRegSerializer

    def put(self, request, pk, *args, **kwargs):
        return self.update(request, *args, **kwargs)
"""


class ChangePasswordViewset(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    修改密码
    """
    permission_classes = (IsAuthenticated, UserIsOwner,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = ChangePasswordSerializer
    queryset = User.objects.all()


class VerifyCodeViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    发送邮箱验证码
    """
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = VerifyCodeSerializer

    def generate_code(self):
        """
        生成六位数字的验证码
        """
        seeds = "1234567890"
        random_str = []
        for i in range(6):
            random_str.append(choice(seeds))
        return "".join(random_str)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        code = self.generate_code()

        smtp.code_smtp(email, code)
        code_record = CaptchaModel(email=email, code=code)
        code_record.save()
        return Response({
            "msg": "发送成功"
        }, status=status.HTTP_201_CREATED)


class getUserFuzzyMailViewset(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
        获取模糊用户邮箱
        URL:
            /member/security/getUserFuzzyMail/
        TYPE:
            GET
    """
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    queryset = User.objects.all()

    def fuzzy_mail(self, mail):
        end = mail.index("@")
        if end % 2 == 1:
            start = int((end - 1) / 2)
        else:
            start = int(end / 2)
        fuzzyMail = mail.replace(mail[start:end], "****")
        return "".join(fuzzyMail)

    def list(self, request, *args, **kwargs):
        mail = self.request.user.email
        if mail is None:
            return Response({
                'detail': '未绑定邮箱'
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "email": self.fuzzy_mail(mail)
            }, status=status.HTTP_200_OK)


class checkUserMailViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
        检查用户邮箱
        URL:
            /member/security/checkUserMail/
        TYPE:
            POST
        JSON:
            {
                "email": "<email>"
            }
    """
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = checkUserMailSerializer

    def create(self, request, *args, **kwargs):
        user = self.request.user

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if user.email is None:
            return Response({
                'detail': '未绑定邮箱'
            }, status=status.HTTP_400_BAD_REQUEST)
        if user.email == serializer.validated_data["email"]:
            return Response({
                "msg": "邮箱校验正确"
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'detail': '邮箱校验不正确'
            }, status=status.HTTP_400_BAD_REQUEST)


class sendOldMailCaptchaViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
        向旧邮箱发送验证码
        URL:
            /member/security/sendOldMailCaptcha/
        TYPE:
            POST
    """
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = sendOldMailCaptchaSerializer

    def generate_code(self):
        """
        生成六位数字的验证码
        """
        seeds = "1234567890"
        random_str = []
        for i in range(6):
            random_str.append(choice(seeds))
        return "".join(random_str)

    def create(self, request, *args, **kwargs):
        user = self.request.user

        if user.email is None:
            return Response({
                'detail': '未绑定邮箱'
            }, status=status.HTTP_400_BAD_REQUEST)

        data = request.POST.copy()
        data['email'] = user.email

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        code = self.generate_code()

        if smtp.code_smtp(email, code) == 1:
            code_record = CaptchaModel(email=email, code=code)
            code_record.save()
            return Response({
                "msg": "发送成功"
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "detail": "发送失败"
            }, status=status.HTTP_400_BAD_REQUEST)


class confirmOldMailCaptchaViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
        确认旧邮箱验证码
        URL:
            /member/security/confirmOldMailCaptcha/
        TYPE:
            POST
        JSON:
        {
            "code": "<code>"
        }
    """
    permission_classes = (IsAuthenticated, UserIsOwner,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = confirmMailCaptchaSerializer

    def create(self, request, *args, **kwargs):
        user = self.request.user

        if user.email is None:
            return Response({
                'detail': '未绑定邮箱'
            }, status=status.HTTP_400_BAD_REQUEST)

        data = request.data.copy()
        data['email'] = user.email

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        return Response({
            'msg': '验证码正确'
        }, status=status.HTTP_200_OK)


class sendNewMailCaptchaViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
        向新邮箱发送验证码
        URL:
            /member/security/sendNewMailCaptcha/
        TYPE:
            POST
        JSON:
            {
                "email": "<email>"
            }
    """
    permission_classes = (IsAuthenticated, )
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = sendNewMailCaptchaSerializer

    def generate_code(self):
        """
        生成六位数字的验证码
        """
        seeds = "1234567890"
        random_str = []
        for i in range(6):
            random_str.append(choice(seeds))
        return "".join(random_str)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        code = self.generate_code()

        if smtp.code_smtp(email, code) == 1:
            code_record = CaptchaModel(email=email, code=code)
            code_record.save()
            return Response({
                "msg": "发送成功"
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "detail": "发送失败"
            }, status=status.HTTP_400_BAD_REQUEST)


class confirmNewMailCaptchaViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
        确认新邮箱验证码
        URL:
            /member/security/confirmNewMailCaptcha/
        TYPE:
            POST
        JSON:
            {
                "email": "<email>",
                "code": "<code>"
            }
    """
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = confirmMailCaptchaSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response({
            'msg': '验证码正确'
        }, status=status.HTTP_200_OK)
