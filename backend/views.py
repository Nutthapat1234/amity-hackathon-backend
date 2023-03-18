from django.http.response import JsonResponse
from django.conf import settings


from .serializers import GetMenuImageSerializer, GetCookingTnstrctionImageSerialzer
from rest_framework import generics
from rest_framework.exceptions import ValidationError

import requests


def generate_image_list(key, promt_list):
    result = []
    for prompt in promt_list:
        generate_image_response = requests.post(
            url="https://api.openai.com/v1/images/generations",
            headers={
                "Authorization": f"Bearer {settings.OPEN_AI_API_SECRECT}",
                "Content-Type": "application/json",
            },
            json={"prompt": prompt, "n": 1, "size": "512x512"},
        )

        result.append(
            {key: prompt, "image": generate_image_response.json()["data"][0]["url"]}
        )
    return result


class GenerateMenuImage(generics.CreateAPIView):
    serializer_class = GetMenuImageSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            menus = serializer.validated_data.get("menuList")
            result = generate_image_list("name", menus)
            return JsonResponse({"data": result})

        except ValidationError as validate_err:
            return JsonResponse(validate_err.detail, status=validate_err.status_code)


class generateCookingInstractionImages(generics.CreateAPIView):
    serializer_class = GetCookingTnstrctionImageSerialzer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            instractions = serializer.validated_data.get("instractions")
            result = generate_image_list("instraction_descption", instractions)
            return JsonResponse({"data": result})

        except ValidationError as validate_err:
            return JsonResponse(validate_err.detail, status=validate_err.status_code)
