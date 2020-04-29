from django.db import models
from datetime import datetime

from users.models import User
from dormitories.models import Dormitory
# Create your models here.


class WaterFeesLog(models.Model):
    """
    水费使用记录
    """
    dormitory = models.ForeignKey(Dormitory, verbose_name="宿舍", on_delete=models.CASCADE, null=False, related_name='water_fees_log_s_dormitory')
    mode = models.CharField(verbose_name="操作方式", max_length=3, choices=(("add", "加"), ("sub", "减")), default="sub")
    change_money = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="改变金额(元)")
    operator = models.ForeignKey(User, verbose_name="操作人", on_delete=models.CASCADE, null=False, related_name='water_fees_log_s_operator')
    add_time = models.DateTimeField(verbose_name="创建时间", default=datetime.now)
    note = models.CharField(verbose_name="备注", max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "宿舍水费使用记录"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.id

class FeesRechargeOrder(models.Model):
    """
    充值 订单
    """
    operator = models.ForeignKey(User, verbose_name="操作人", on_delete=models.CASCADE, null=False,
                                 related_name='fees_recharge_order_s_operator')
    price = models.IntegerField(verbose_name="充值金额(元)")
    recharge_dormitory = models.ForeignKey(Dormitory, verbose_name="宿舍", on_delete=models.CASCADE, null=False, related_name='fees_recharge_order_s_dormitory')
    recharge_object = models.CharField(verbose_name="充值对象", max_length=11, choices=(("water", "水费"), ("electricity", "电费")), default="water")
    recharge_number = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="充值数量")
    recharge_type = models.CharField(verbose_name="充值方式", max_length=6, choices=(("alipay", "支付宝"), ("qqpay", "QQ钱包"), ("wechar", "微信")), default="alipay")
    recharge_status = models.CharField(verbose_name="充值状态", max_length=7, choices=(("success", "充值成功"), ("closed", "超时关闭"), ("paying", "待支付")), default="paying")
    pay_id = models.CharField(verbose_name="充值订单号", max_length=100)
    pay_no = models.CharField(verbose_name="充值流水号(支付平台订单号)", max_length=100, null=True)

    class Meta:
        verbose_name = "充值订单记录"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.id

class ElectricityFeesLog(models.Model):
    """
    电费使用记录
    """
    dormitory = models.ForeignKey(Dormitory, verbose_name="宿舍", on_delete=models.CASCADE, null=False, related_name='electricity_fees_log_s_dormitory')
    mode = models.CharField(verbose_name="操作方式", max_length=3, choices=(("add", "加"), ("sub", "减")), default="sub")
    change_money = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="改变金额(元)")
    operator = models.ForeignKey(User, verbose_name="操作人", on_delete=models.CASCADE, null=False, related_name='electricity_fees_log_s_operator')
    add_time = models.DateTimeField(verbose_name="创建时间", default=datetime.now)
    note = models.CharField(verbose_name="备注", max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "宿舍电费使用记录"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.id


class Repair(models.Model):
    """
    宿舍 报修单
    """
    title = models.CharField(verbose_name="标题", max_length=50)
    applicant = models.ForeignKey(User, verbose_name="申请人", on_delete=models.CASCADE, null=False, related_name='repair_s_applicant')
    dormitory = models.ForeignKey(Dormitory, verbose_name="宿舍", on_delete=models.CASCADE, null=False, related_name='repair_s_dormitory')
    content = models.TextField(verbose_name="报修内容")
    status = models.CharField(verbose_name="状态", max_length=10, choices=(("complete", "完成"), ("processing", "处理中"), ("untreated", "未处理")), default="untreated")
    add_time = models.DateTimeField(verbose_name="创建时间", default=datetime.now)

    class Meta:
        verbose_name = "宿舍报修单"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.id


class RepairLog(models.Model):
    """
    宿舍 报修单 回复
    """
    main_repair = models.ForeignKey(Repair, verbose_name="主报修单", on_delete=models.CASCADE, null=False, related_name='repair_log_s_main_repair')
    reply = models.TextField(verbose_name="报修回复")
    reply_type = models.CharField(verbose_name="回复类型", max_length=10, choices=(("complete", "已完成"), ("processing", "处理中")), default="processing")
    reply_person = models.ForeignKey(User, verbose_name="回复人", on_delete=models.CASCADE, null=False, related_name='repair_log_s_reply_person')
    add_time = models.DateTimeField(verbose_name="创建时间", default=datetime.now)

    class Meta:
        verbose_name = "宿舍报修单回复"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.id


