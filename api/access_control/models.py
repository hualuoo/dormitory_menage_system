from django.db import models
from datetime import datetime

from users.models import User
# Create your models here.


class AccessControl(models.Model):
    """
    门禁记录
    """
    photo = models.ImageField(upload_to="users/access_control/", null=True, blank=True, verbose_name="通过门禁的照片")
    person = models.ForeignKey(User, verbose_name="通过的人", on_delete=models.CASCADE, null=False, related_name='access_control_s_person')
    accuracy = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="准确率(%)")
    status = models.CharField(verbose_name="状态", max_length=8, choices=(("normal", "识别正常"), ("later", "学生晚归"), ("abnormal", "识别异常")), default="normal")
    add_time = models.DateTimeField(verbose_name="创建时间", default=datetime.now)
    note = models.CharField(verbose_name="备注", max_length=100, blank=True)

    class Meta:
        verbose_name = "门禁记录"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.id

class AccessControlAbnormalApplication(models.Model):
    """
    门禁记录 识别异常申请
    """
    main_record = models.OneToOneField(AccessControl, verbose_name="主记录", on_delete=models.CASCADE, null=False, related_name='abnormal_application')
    content = models.TextField(verbose_name="申请内容")
    result = models.CharField(verbose_name="结果", max_length=7, choices=(("pending", "待处理"), ("pass", "通过"), ("fail", "未通过")), default="pending")
    add_time = models.DateTimeField(verbose_name="申请时间", default=datetime.now)
    reply = models.TextField(verbose_name="申请回复")

    class Meta:
        verbose_name = "门禁记录 识别异常 申请"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.id