from datetime import datetime

from django.db import models

from users.models import User
# Create your models here.


class SystemSetting(models.Model):
    """
    系统设定
    """
    code = models.CharField(verbose_name="代码", max_length=50)
    title = models.CharField(verbose_name="标题", max_length=20)
    content = models.TextField(verbose_name="内容")
    url = models.FileField(verbose_name="链接",upload_to="media/file/", max_length=100, blank=True, null=True)
    note = models.CharField(verbose_name="备注", max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "系统设置"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.code

class SystemLog(models.Model):
    """
    系统日志
    """
    content = models.CharField(verbose_name="操作内容", max_length=1000)
    category = models.CharField(verbose_name="操作种类", max_length=10)
    operator = models.ForeignKey(User, verbose_name="操作人", on_delete=models.CASCADE, null=False, related_name='system_log_s_operator')
    ip = models.CharField(verbose_name="操作IP", max_length=100)
    add_time = models.DateTimeField(verbose_name="操作时间", default=datetime.now)

    class Meta:
        verbose_name = "系统日志"
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.id)
