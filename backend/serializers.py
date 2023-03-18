from rest_framework import serializers

class GetMenuImages(serializers.Serializer):
    menus = serializers.ListField(child=serializers.CharField(min_length=1))