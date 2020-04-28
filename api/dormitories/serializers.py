from rest_framework import serializers

from .models import Dormitory, WaterFees, ElectricityFees
from users.models import User
from system_setting.models import SystemSetting


class DormitorySerializer(serializers.ModelSerializer):
    """
    宿舍 序列化类
    """
    number = serializers.CharField(help_text="编号", max_length=10)
    area = serializers.CharField(help_text="宿舍区域", max_length=3)
    build = serializers.CharField(help_text="幢", max_length=1)
    floor = serializers.IntegerField(help_text="楼")
    room = serializers.CharField(help_text="房间号", max_length=3)
    allow_live_number = serializers.IntegerField(help_text="允许居住人数")
    now_live_number = serializers.IntegerField(help_text="现已居住人数")
    note = serializers.CharField(help_text="备注", max_length=100)
    add_time = serializers.DateTimeField(help_text="创建时间", format="%Y-%m-%d %H:%M:%S", required=False)
    lived_users = serializers.StringRelatedField(read_only=True, many=True)

    class Meta:
        model = Dormitory
        fields = "__all__"


class DormitoryCreateSerializer(serializers.ModelSerializer):
    """
    宿舍 创建 序列化类
    """
    number = serializers.CharField(help_text="编号", max_length=10)
    area = serializers.CharField(help_text="宿舍区域", max_length=3)
    build = serializers.CharField(help_text="幢", max_length=1)
    floor = serializers.IntegerField(help_text="楼")
    room = serializers.CharField(help_text="房间号", max_length=4)
    allow_live_number = serializers.IntegerField(help_text="允许居住人数", max_value=8, min_value=0)

    def validate_number(self, number):
        import re
        flag = re.match(r'^[A-Z0-9]{5,7}$', number)
        if flag is None:
            raise serializers.ValidationError('操作失败：编号须为5~7位的数字和大写英文！')
        if len(Dormitory.objects.filter(number=number)) != 0:
            raise serializers.ValidationError('操作失败：已存在编号相同的宿舍！')
        return number

    def validate_area(self, area):
        import re
        flag = re.match(r'^[学][一|二|三|四|五|六|七|八|九|十]{1,3}$', area)
        if flag is None:
            raise serializers.ValidationError('操作失败：区域须以<学>字开头，中文数字结尾！')
        return area

    def validate_build(self, build):
        import re
        flag = re.match(r'^[A-Z]{1,1}$', build)
        if flag is None:
            raise serializers.ValidationError('操作失败：宿舍楼须为1位大写英文！')
        return build

    def validate_room(self, room):
        import re
        flag = re.match(r'^[0-9]{3,4}$', room)
        if flag is None:
            raise serializers.ValidationError('操作失败：房间号须为3~4位数字！')
        if len(room) == 3 and self.initial_data["floor"] != room[0]:
            raise serializers.ValidationError('操作失败：房间号前一位与楼层不对应！')
        if len(room) == 4 and self.initial_data["floor"] != room[0:2]:
            raise serializers.ValidationError('操作失败：房间号前两位与楼层不对应！')
        return room

    def create(self, validated_data):
        dormitory = super(DormitoryCreateSerializer, self).create(validated_data=validated_data)
        dormitory.save()
        water_fees = WaterFees.objects.create(dormitory=dormitory)
        electricity_fees = ElectricityFees.objects.create(dormitory=dormitory)
        water_fees.save()
        electricity_fees.save()
        return dormitory

    class Meta:
        model = Dormitory
        fields = "__all__"


class DormitoryOnChangeTransferSerializer(serializers.ModelSerializer):
    ids = serializers.CharField(help_text="调整的用户编号")
    index = serializers.IntegerField(help_text="调整方式", max_value=1, min_value=0)

    def validate_ids(self, ids):
        ids_list = ids.split(',')
        for i in ids_list:
            users = User.objects.filter(id=i)
            if users.count() == 0:
                raise serializers.ValidationError('操作失败：ID为' + i + '的用户不存在！')
        return ids

    class Meta:
        model = User
        fields = ("ids", "index", )


class DormitoryChangeAllowLiveNumberSerializer(serializers.ModelSerializer):
    allow_live_number = serializers.IntegerField(help_text="允许居住人数", max_value=8, min_value=0)

    def validate_allow_live_number(self, allow_live_number):
        if len(self.instance.lived_users.all()) > allow_live_number:
            raise serializers.ValidationError('操作失败：宿舍允许居住人数不允许小于现已住人数！')
        return allow_live_number

    class Meta:
        model = User
        fields = ("allow_live_number", )


class DormitoryChangeNoteSerializer(serializers.ModelSerializer):
    note = serializers.CharField(help_text="备注", max_length=100, allow_blank=True)

    class Meta:
        model = User
        fields = ("note", )


class WaterFeesSerializer(serializers.ModelSerializer):
    """
    宿舍水费 序列类
    """
    dormitory_number = serializers.CharField(source='dormitory.number')
    have_water_fees = serializers.DecimalField(max_digits=5, decimal_places=2)
    have_water = serializers.SerializerMethodField()
    note = serializers.CharField()

    def get_have_water(self, obj):
        return round(float(abs(obj.have_water_fees))/float(SystemSetting.objects.filter(code='water_fees').first().content), 2)

    class Meta:
        model = ElectricityFees
        fields = ("id", "dormitory_number", "have_water_fees", "have_water", "note", )


class WaterFeesRechargeAdminSerializer(serializers.ModelSerializer):
    """
    宿舍水费 充值 序列类
    """
    money = serializers.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        model = ElectricityFees
        fields = ("money", )


class WaterFeesChangeNoteSerializer(serializers.ModelSerializer):
    """
    宿舍水费 备注 序列类
    """
    note = serializers.CharField(help_text="备注", max_length=100, allow_blank=True)

    class Meta:
        model = ElectricityFees
        fields = ("note", )


class ElectricityFeesSerializer(serializers.ModelSerializer):
    """
    宿舍电费 列表 序列类
    """
    dormitory_number = serializers.CharField(source='dormitory.number')
    have_electricity_fees = serializers.DecimalField(max_digits=5, decimal_places=2)
    have_electricity = serializers.SerializerMethodField()
    note = serializers.CharField()

    def get_have_electricity(self, obj):
        return round(float(abs(obj.have_electricity_fees))/float(SystemSetting.objects.filter(code='electricity_fees').first().content), 2)

    class Meta:
        model = ElectricityFees
        fields = ("id", "dormitory_number", "have_electricity_fees", "have_electricity", "note", )


class ElectricityFeesRechargeSerializer(serializers.ModelSerializer):
    """
    宿舍电费 充值 序列类
    """
    money = serializers.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        model = ElectricityFees
        fields = ("money", )


class ElectricityFeesChangeNoteSerializer(serializers.ModelSerializer):
    """
    宿舍电费 备注 序列类
    """
    note = serializers.CharField(help_text="备注", max_length=100, allow_blank=True)

    class Meta:
        model = ElectricityFees
        fields = ("note", )