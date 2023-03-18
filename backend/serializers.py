from rest_framework import serializers


class GetMenuImageSerializer(serializers.Serializer):
    menuList = serializers.ListField(
        child=serializers.CharField(
            min_length=1,
        )
    )


class GetCookingTnstrctionImageSerialzer(serializers.Serializer):
    instractions = serializers.ListField(
        child=serializers.CharField(
            min_length=1,
        )
    )
