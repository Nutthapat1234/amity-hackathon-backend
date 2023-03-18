from django.http.response import JsonResponse
from django.conf import settings


from .serializers import GetMenuImages
from rest_framework import generics

import requests

class GenerateMenuImage(generics.ListCreateAPIView):
    serializer_class = GetMenuImages

    def get(self, request, *args, **kwargs):
        print(request.query_params)
        # dall_e_response = requests.post(
        #     url="https://api.openai.com/v1/images/generations"
        #     headers={
        #         "Authorization": f"Bearer {settings.OPEN_AI_API_SECRECT}",
        #         "Content-Type": "application/json" 
        #     },
        #     json={
        #         "prompt": "A cute baby sea otter",
        #         "n": 1,
        #         "size": "512x512"
        #     }'
        # )
        return JsonResponse({})