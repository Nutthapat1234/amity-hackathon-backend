import json

from django.http.response import JsonResponse
from django.conf import settings


from .serializers import GetMenuImageSerializer, GetCookingTnstrctionImageSerialzer, Get
from rest_framework import generics

import requests
import os
import openai



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

class GenerateMenu(generics.ListCreateAPIView):
    serializer_class = GetMenu
    def post(self, request, *args, **kwargs):
        #try:
        data = json.loads(request.body)
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            json_question = serializer.data
            message = [{"role": "user", "content": "What is the circumference in km of the planet Earth?"}]
            receive_ingredient = json_question['ingredient']
            receive_ingredient = ', '.join(receive_ingredient)
            type_ = json_question['type']
            no_serving = json_question['no_serving']
            content = "answer me in the following json format only {\r\n  \"Recipes\": [\r\n    {\r\n      \"Name\": \"<Recipe name>\",\r\n      \"Nutrition\": {\r\n        \"Calories\": \"<Calories count>\",\r\n        \"Protein\": \"<Protein count>\",\r\n        \"Fat\": \"<Fat count>\",\r\n        \"Carbohydrates\": \"<Carbohydrates count>\",\r\n        \"Fiber\": \"<Fiber count>\"\r\n      }\r\n    }\r\n  ]\r\n} Give me 5 choices for "+ type_ + " I can cook with "+ receive_ingredient + " within 30 minutes for a serving of "+no_serving+". Also, show me the macro "
            message[0]['content'] = content
            completion = openai.ChatCompletion.create(
               model="gpt-3.5-turbo",  # this is "ChatGPT" $0.002 per 1k tokens
               messages=message
            )
            json_obj = json.loads(completion['choices'][0]['message']['content'])
        return JsonResponse(json_obj)
