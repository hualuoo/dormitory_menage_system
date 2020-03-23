from rest_framework import serializers
from datetime import datetime

from .models import AccessControl


class AccessControlSerializer(serializers.ModelSerializer):
    """
    门禁记录 序列化类
    """
    photo = serializers.ImageField(help_text="通过门禁的照片")
    person__username = serializers.CharField(source="person.username", help_text="通过的人的用户名")
    person__first_name = serializers.CharField(source="person.first_name", help_text="通过的人的姓")
    person__last_name = serializers.CharField(source="person.last_name", help_text="通过的人的名")
    person__face__photo = serializers.ImageField(source="person.face.photo", help_text="通过的人的人脸照片")
    status = serializers.ChoiceField(help_text="状态", choices=(("normal", "识别正常"), ("later", "学生晚归"), ("abnormal", "识别异常")), default="normal")
    accuracy = serializers.DecimalField(max_digits=5, decimal_places=2)
    add_time = serializers.DateTimeField(help_text="创建时间", format="%Y-%m-%d %H:%M", default=datetime.now)
    note = serializers.CharField(help_text="备注", max_length=100, allow_blank=True)

    class Meta:
        model = AccessControl
        fields = ("id", "photo", "person__username", "person__first_name", "person__last_name", "person__face__photo", "status", "accuracy", "add_time", "note", )


class AccessControlUpdateSerializer(serializers.ModelSerializer):
    """
    门禁记录 修改 序列化类
    """
    status = serializers.ChoiceField(help_text="状态", choices=(("normal", "识别正常"), ("later", "学生晚归"), ("abnormal", "识别异常")), default="normal")
    note = serializers.CharField(help_text="备注", max_length=100, allow_blank=True)

    class Meta:
        model = AccessControl
        fields = ("status", "note", )