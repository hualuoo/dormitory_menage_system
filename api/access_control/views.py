from django.shortcuts import render
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from .models import AccessControl
from .serializers import AccessControlSerializer
# Create your views here.


class AccessControlViewset(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    用户 视图类
    """
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)
    serializer_class = AccessControlSerializer
    queryset = AccessControl.objects.all()

    def list(self, request, *args, **kwargs):
        from django.db.models import Q,F

        # 获取全部门禁通过记录数据
        all_result = self.filter_queryset(self.get_queryset())

        # 默认按创建时间倒数排序
        all_result = all_result.order_by(F("add_time").desc())

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