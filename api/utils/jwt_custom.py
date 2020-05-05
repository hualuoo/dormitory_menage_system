from datetime import datetime

from rest_framework import serializers
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from aliyunsdkcore import client
from aliyunsdkcore.profile import region_provider
from utils.aliyun_python_sdk_afs.aliyunsdkafs.request.v20180112 import AuthenticateSigRequest

from users.models import User
from system_setting.models import SystemLog
from django.conf import settings
from utils.smtp import login_smtp

region_provider.add_endpoint('afs', 'cn-hangzhou', 'afs.aliyuncs.com')
clt = client.AcsClient(settings.ALICLOUD_AFS_ACCESSKEY, settings.ALICLOUD_AFS_ACCESS_SECRET, 'cn-hangzhou')


class CustomBackend(ModelBackend):
    """
    用户自定义用户验证
    """
    # 修改了 \venv\Lib\site-packages\rest_framework_jwt\serializers.py 文件添加传参
    def authenticate(self, request, username=None, password=None, session_id=None, sig=None, token=None, scene=None, ip=None, **kwargs):# 重写这个函数
        import json

        if session_id:
            afs_request = AuthenticateSigRequest.AuthenticateSigRequest()
            # 会话ID。必填参数，从前端获取，不可更改。
            afs_request.set_SessionId(session_id)
            # 签名串。必填参数，从前端获取，不可更改。
            afs_request.set_Sig(sig)
            # 请求唯一标识。必填参数，从前端获取，不可更改。
            afs_request.set_Token(token)
            # 场景标识。必填参数，从前端获取，不可更改。
            afs_request.set_Scene(scene)
            # 应用类型标识。必填参数，后端填写。
            afs_request.set_AppKey('FFFF0N00000000008F12')
            # 客户端IP。必填参数，后端填写。
            afs_request.set_RemoteIp(ip)
            # 返回code 100表示验签通过，900表示验签失败
            result = clt.do_action_with_exception(afs_request)

            if json.loads(str(result, encoding="utf-8"))['Code'] == 900:
                raise serializers.ValidationError({'detail': '滑动验证不通过，请刷新重试！'})

        user = User.objects.filter(Q(username=username) | Q(email=username))
        if user.count() == 0:
            raise serializers.ValidationError({'detail': '用户名不存在'})
            return None
        last_user = user[0]
        if last_user.is_active == 0:
            raise serializers.ValidationError({'detail': '用户已被禁用'})
            return None
        if last_user.is_superuser is False and session_id is None:
            raise serializers.ValidationError({'detail': '滑动验证不通过，请刷新重试！'})
        if last_user.check_password(password):
            last_user.last_login = datetime.now()
            last_user.save()
            system_log = SystemLog.objects.create(content='用户登录（用户名：' + last_user.username + '）',
                                                  category="登录",
                                                  operator=request.user,
                                                  ip=request.META.get("REMOTE_ADDR"))
            system_log.save()
            if last_user.email is not None:
                # login_smtp(user, ip)
                return last_user
            return last_user
        else:
            raise serializers.ValidationError({'detail': '密码错误'})
            return None


def jwt_response_payload_handler(token, user=None, request=None):
    """
        登录成功后自定义返回
    """
    return {
        "username": user.username,
        "is_superuser": user.is_superuser,
        "token": token
    }