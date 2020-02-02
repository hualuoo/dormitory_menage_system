from rest_framework import mixins
from random import choice
from datetime import datetime, timedelta
from .models import UserModel, UserInfo, CaptchaModel
from utils import smtp
from .serializers import UserListSerializer, UserRegSerializer, VerifyCodeSerializer, ChangeEmailSerializer, ChangePasswordSerializer
from .serializers import checkUserMailSerializer, sendOldMailCaptchaSerializer, confirmMailCaptchaSerializer, sendNewMailCaptchaSerializer

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from utils.permission import UserIsOwner, UserInfoIsOwner

# Create your views here.


class UserInfoViewset(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    用户详细信息
    """
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = UserListSerializer
    queryset = UserModel.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        if self.action == "retrieve":
            return UserListSerializer
        if self.action == "update":
            return UserListSerializer
        return UserListSerializer

    def list(self, request, *args, **kwargs):
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
        # 排序列名
        field = request.GET.get('field', '')
        # 排序类型，升序降序
        order = request.GET.get('order', '')
        # 模糊搜索关键词
        search_username = request.GET.get('search_username', '')
        search_realname = request.GET.get('search_realname', '')
        search_email = request.GET.get('search_email', '')
        search_mobile = request.GET.get('search_mobile', '')

        # 替换字符串进行外链查询
        field = field.replace(".", "__")

        # 排序
        if field:
            if order == "asc":
                all_result = all_result.order_by(F(field).asc(nulls_last=True))
            elif order == "desc":
                all_result = all_result.order_by(F(field).desc(nulls_last=True))

        # 搜索
        if search_username:
            all_result = all_result.filter(Q(username__icontains=search_username))
        if search_realname:
            all_result = all_result.filter(Q(userinfo__realname__icontains=search_realname))
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
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
        """



class UsersViewset(mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    用戶列表
    """
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


class ChangePasswordViewset(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    修改密码
    """
    permission_classes = (IsAuthenticated, UserIsOwner,)
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = ChangePasswordSerializer
    queryset = UserModel.objects.all()


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
    queryset = UserModel.objects.all()

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
