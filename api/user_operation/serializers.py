from datetime import datetime

from rest_framework import serializers

from .models import ElectricityFeesLog, Repair, RepairLog, FeesRechargeOrder


class WaterFeesLogSerializer(serializers.ModelSerializer):
    dormitory_number = serializers.CharField(source='dormitory.number')
    mode = serializers.ChoiceField(help_text="操作方式", choices=(("add", "加"), ("sub", "减")), default="sub")
    change_money = serializers.DecimalField(max_digits=5, decimal_places=2, help_text="改变金额(元)")
    operator__username = serializers.CharField(source='operator.username')
    operator__first_name = serializers.CharField(source='operator.first_name')
    operator__last_name = serializers.CharField(source='operator.last_name')
    add_time = serializers.DateTimeField(help_text="创建时间", default=datetime.now, format="%Y-%m-%d %H:%M:%S")
    note = serializers.CharField(help_text="备注", max_length=100, allow_blank=True, allow_null=True)

    class Meta:
        model = ElectricityFeesLog
        fields = ("id", "dormitory_number", "mode", "change_money", "operator__username", "operator__first_name", "operator__last_name", "add_time", "note", )


class ElectricityFeesLogSerializer(serializers.ModelSerializer):
    dormitory_number = serializers.CharField(source='dormitory.number')
    mode = serializers.ChoiceField(help_text="操作方式", choices=(("add", "加"), ("sub", "减")), default="sub")
    change_money = serializers.DecimalField(max_digits=5, decimal_places=2, help_text="改变金额(元)")
    operator__username = serializers.CharField(source='operator.username')
    operator__first_name = serializers.CharField(source='operator.first_name')
    operator__last_name = serializers.CharField(source='operator.last_name')
    add_time = serializers.DateTimeField(help_text="创建时间", default=datetime.now, format="%Y-%m-%d %H:%M:%S")
    note = serializers.CharField(help_text="备注", max_length=100, allow_blank=True, allow_null=True)

    class Meta:
        model = ElectricityFeesLog
        fields = ("id", "dormitory_number", "mode", "change_money", "operator__username", "operator__first_name", "operator__last_name", "add_time", "note", )


class RepairSerializer(serializers.ModelSerializer):
    title = serializers.CharField(help_text="标题", max_length=50)
    applicant__username = serializers.CharField(source='applicant.username', required=False)
    applicant__first_name = serializers.CharField(source='applicant.first_name', required=False)
    applicant__last_name = serializers.CharField(source='applicant.last_name', required=False)
    dormitory__number = serializers.CharField(source='dormitory.number', required=False)
    content = serializers.CharField(help_text="报修内容")
    status = serializers.ChoiceField(help_text="状态", choices=(("complete", "已完成"), ("processing", "处理中"), ("untreated", "未处理")))
    add_time = serializers.DateTimeField(help_text="创建时间", format="%Y-%m-%d %H:%M:%S", required=False)

    class Meta:
        model = Repair
        fields = ("id", "title", "applicant__username", "applicant__first_name", "applicant__last_name", "dormitory__number", "content", "status", "add_time", )


class RepairCreateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(help_text="标题", max_length=50)
    content = serializers.CharField(help_text="报修内容")

    class Meta:
        model = Repair
        fields = ("title", "content", )


class RepairLogSerializer(serializers.ModelSerializer):
    main_repair__id = serializers.IntegerField(source='main_repair.id', required=False)
    reply = serializers.CharField(help_text="报修回复")
    reply_type = serializers.ChoiceField(help_text="回复类型", choices=(("complete", "完成"), ("processing", "处理中")))
    reply_person__username = serializers.CharField(source='reply_person.username', required=False)
    reply_person__first_name = serializers.CharField(source='reply_person.first_name', required=False)
    reply_person__last_name = serializers.CharField(source='reply_person.last_name', required=False)
    add_time = serializers.DateTimeField(help_text="创建时间", format="%Y-%m-%d %H:%M:%S", required=False)

    class Meta:
        model = RepairLog
        fields = ("id", "main_repair__id", "reply", "reply_type", "reply_person__username", "reply_person__first_name", "reply_person__last_name", "add_time", )


class RepairLogCreateSerializer(serializers.ModelSerializer):
    main_repair__id = serializers.IntegerField()
    reply = serializers.CharField(help_text="报修回复")
    reply_type = serializers.ChoiceField(help_text="回复类型", choices=(("complete", "完成"), ("processing", "处理中")))

    class Meta:
        model = RepairLog
        fields = ("main_repair__id", "reply", "reply_type", )


class FeesRechargeOrderCreateSerializer(serializers.ModelSerializer):
    price = serializers.IntegerField(help_text="充值金额(元)", max_value=1000, min_value=1)
    type = serializers.ChoiceField(help_text="充值方式", choices=(("1", "支付宝"), ("2", "QQ钱包"), ("3", "微信支付")))
    object = serializers.ChoiceField(help_text="充值对象", choices=(("water", "水费"), ("electricity", "电费")))

    class Meta:
        model = FeesRechargeOrder
        fields = ("price", "type", "object", )
