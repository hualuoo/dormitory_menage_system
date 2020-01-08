from django.db import models
from datetime import datetime
from django.contrib.auth.models import AbstractUser

# Create your models here.


class UserModel(AbstractUser):
    """
    用户
    """
    email = models.EmailField(max_length=100, null=True, blank=True, verbose_name="邮箱")

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


class UserInfo(models.Model):
    """
    用户详情信息
    """
    realname = models.CharField(max_length=30, null=True, blank=True, verbose_name="姓名")
    birthday = models.DateField(null=True, blank=True, verbose_name="出生年月")
    gender = models.CharField(max_length=6, choices=(("male", u"男"), ("female", "女")), default="male",
                              verbose_name="性别")
    mobile = models.CharField(null=True, blank=True, max_length=11, verbose_name="电话")
    user = models.ForeignKey(UserModel, verbose_name="用户", on_delete=models.CASCADE)

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
