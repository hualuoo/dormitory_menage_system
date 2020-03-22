from django.db import models
from datetime import datetime

from users.models import User
# Create your models here.


class AccessControl(models.Model):
    """
    门禁 记录
    """
    photo = models.ImageField(upload_to="users/access_control/", null=True, blank=True, verbose_name="通过门禁的照片")
    person = models.ForeignKey(User, verbose_name="通过的人", on_delete=models.CASCADE, null=False, related_name='access_control_s_person')
    accuracy = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="准确率(%)")
    status = models.CharField(verbose_name="状态", max_length=10, choices=(("normal", "正常"), ("later", "晚归"), ("abnormal", "异常")), default="normal")
    add_time = models.DateTimeField(verbose_name="创建时间", default=datetime.now)

    class Meta:
        verbose_name = "门禁记录"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.id
