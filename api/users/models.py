from django.db import models
from datetime import datetime
from django.contrib.auth.models import AbstractUser

from dormitories.models import Dormitory
# Create your models here.


class User(AbstractUser):
    """
    用户
    """
    email = models.EmailField(max_length=100, blank=True, verbose_name="邮箱")
    lived_dormitory = models.ForeignKey(Dormitory, on_delete=models.CASCADE, verbose_name="居住宿舍", null=True, related_name='lived_users')

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class UserInfo(models.Model):
    """
    用户详情信息
    """
    birthday = models.DateField(null=True, blank=True, verbose_name="出生年月")
    gender = models.CharField(max_length=7, choices=(("male", "男"), ("female", "女"), ("unknown", "未知")), default="unknown",
                              verbose_name="性别")
    mobile = models.CharField(blank=True, max_length=11, verbose_name="电话")
    avatar = models.ImageField(upload_to="users/avatar/", null=True, blank=True, verbose_name="照片")
    face_128d_features = models.CharField(max_length=3000, blank=True, verbose_name="人脸128D数据")
    user = models.OneToOneField(User, verbose_name="用户", on_delete=models.CASCADE, related_name="info")

    class Meta:
        verbose_name = "用户详情信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.username


class CaptchaModel(models.Model):
    """
    邮件验证码
    """
    email = models.EmailField(max_length=100, null=True, blank=True, verbose_name="邮箱")
    code = models.CharField(max_length=10, verbose_name="验证码")
    create_time = models.DateTimeField(default=datetime.now, verbose_name="创建时间")

    class Meta:
        verbose_name = "邮件验证码"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.__str__()
