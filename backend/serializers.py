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


class GetMenu(serializers.Serializer):
    ingredient = serializers.ListField(child=serializers.CharField(max_length=100))
    type = serializers.CharField(min_length=1)
    no_serving = serializers.CharField(min_length=1)

class GetInstruction(serializers.Serializer):
    menu_name = serializers.CharField(min_length=1)
    no_serving = serializers.CharField(min_length=1)
