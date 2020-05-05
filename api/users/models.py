from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser

from dormitories.models import Dormitory
# Create your models here.


class User(AbstractUser):
    """
    用户
    """
    email = models.EmailField(max_length=100, blank=True, null=True, verbose_name="邮箱")
    lived_dormitory = models.ForeignKey(Dormitory, on_delete=models.SET_NULL, verbose_name="居住宿舍", null=True, related_name='lived_users')

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
    mobile = models.CharField(blank=True, null=True, max_length=11, verbose_name="电话")
    avatar = models.ImageField(upload_to="users/avatar/", null=True, blank=True, verbose_name="头像")
    user = models.OneToOneField(User, verbose_name="用户", on_delete=models.CASCADE, related_name="info")

    class Meta:
        verbose_name = "用户详情信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.username


class UserFace(models.Model):
    """
    用户人脸数据
    """
    photo = models.ImageField(upload_to="users/face_photo/", null=True, verbose_name="人脸照片")
    features = models.TextField(verbose_name="特征数据", null=True)
    user = models.OneToOneField(User, verbose_name="用户", on_delete=models.CASCADE, related_name="face")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="创建时间")

    class Meta:
        verbose_name = "用户详情信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.username


class CaptchaModel(models.Model):
    """
    邮件验证码
    """
    email = models.EmailField(max_length=100, verbose_name="邮箱")
    code = models.CharField(max_length=10, verbose_name="验证码")
    create_time = models.DateTimeField(default=datetime.now, verbose_name="创建时间")

    class Meta:
        verbose_name = "邮件验证码"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.email
