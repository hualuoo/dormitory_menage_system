from django.db import models
from datetime import datetime
# Create your models here.


class Dormitory(models.Model):
    """
    宿舍房间
    """
    number = models.CharField(verbose_name="编号", max_length=10)
    area = models.CharField(verbose_name="宿舍区域", max_length=3)
    build = models.CharField(verbose_name="宿舍楼", max_length=1)
    floor = models.IntegerField(verbose_name="宿舍楼层")
    room = models.CharField(verbose_name="房间号", max_length=4)
    allow_live_number = models.IntegerField(verbose_name="允许居住人数")
    now_live_number = models.IntegerField(verbose_name="现已居住人数", default=0)
    note = models.CharField(verbose_name="备注", max_length=100, blank=True)
    add_time = models.DateTimeField(verbose_name="创建时间", default=datetime.now)

    class Meta:
        verbose_name = "宿舍房间"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.number


class WaterFees(models.Model):
    """
    宿舍水费
    """
    dormitory = models.ForeignKey(Dormitory, verbose_name="宿舍", on_delete=models.CASCADE, null=False, related_name='water_fees_dormitory')
    used_water = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="已用水量(吨)")
    surplus_water = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="剩余水量(吨)")
    total_water = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="总共水量(吨)")
    cost = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="水费(元/吨)")
    note = models.CharField(verbose_name="备注", max_length=100, blank=True)
    month = models.DateField(verbose_name="月份")

    class Meta:
        verbose_name = "宿舍水费"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.id


class ElectricityFees(models.Model):
    """
    宿舍电费
    """
    dormitory = models.OneToOneField(Dormitory, verbose_name="宿舍", on_delete=models.CASCADE, null=False,
                                  related_name='electricity_fees_dormitory')
    have_electricity_fees = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="现有金额(元)")
    note = models.CharField(verbose_name="备注", max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "宿舍电费"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.id
