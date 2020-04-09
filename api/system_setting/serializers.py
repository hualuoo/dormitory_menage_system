from rest_framework import serializers
from datetime import datetime

from .models import SystemSetting


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
    todo_list = serializers.CharField(help_text="代办事项列表")
    overview_info = serializers.CharField(help_text="概略信息显示")
    data_overview_start_date = serializers.DateField(help_text="首页数据概览起始日期", format="%Y-%m-%d")

    def validate_overview_info(self, overview_info):
        if len(overview_info.split(',')) != 4:
            raise serializers.ValidationError('概略信息显示只能选择四个选项！')
        return overview_info

    class Meta:
        model = SystemSetting
        fields = ("water_fees", "electricity_fees", "todo_list", "overview_info", "data_overview_start_date", )
