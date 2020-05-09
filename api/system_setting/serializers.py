from rest_framework import serializers

from .models import SystemSetting, SystemLog


class SystemSettingSerializer(serializers.ModelSerializer):
    code = serializers.CharField(help_text="代码", max_length=20)
    title = serializers.CharField(help_text="标题", max_length=20)
    content = serializers.CharField(help_text="内容", max_length=100)
    url = serializers.FileField(help_text="链接", allow_null=True)
    note = serializers.CharField(help_text="备注", max_length=100, allow_null=True)

    class Meta:
        model = SystemSetting
        fields = ("id", "code", "title", "content", "url", "note", )


class SystemSettingUpdateSerializer(serializers.ModelSerializer):
    water_fees = serializers.DecimalField(max_digits=5, decimal_places=2, help_text="水费(元/吨)")
    electricity_fees = serializers.DecimalField(max_digits=5, decimal_places=2, help_text="水费(元/吨)")
    todo_list = serializers.CharField(help_text="控制台代办事项列表")
    overview_info = serializers.CharField(help_text="控制台概略信息显示")
    data_overview_start_date = serializers.DateField(help_text="控制台数据概览起始日期", format="%Y-%m-%d")
    notice_title = serializers.CharField(help_text="首页公告标题")
    notice_content = serializers.CharField(help_text="首页公告内容")

    def validate_overview_info(self, overview_info):
        if len(overview_info.split(',')) != 4:
            raise serializers.ValidationError('概略信息显示只能选择四个选项！')
        return overview_info

    class Meta:
        model = SystemSetting
        fields = ("water_fees", "electricity_fees", "todo_list", "overview_info", "data_overview_start_date", "notice_title", "notice_content", )


class SystemLogSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(help_text="ID")
    operator = serializers.SerializerMethodField(help_text="操作人")
    category = serializers.CharField(help_text="操作种类")
    content = serializers.CharField(help_text="操作内容")
    add_time = serializers.DateTimeField(help_text="操作时间", format="%Y-%m-%d %H:%M:%S")
    ip = serializers.CharField(help_text="操作IP")

    def get_operator(self, obj):
        return obj.operator.username + '(' + obj.operator.first_name + obj.operator.last_name + ')'

    class Meta:
        model = SystemLog
        fields = ("id", "operator", "category", "content", "add_time", "ip", )
