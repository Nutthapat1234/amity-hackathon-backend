import json
from django.http.response import JsonResponse, HttpResponse
from django.conf import settings
from .serializers import (
    GetMenuImageSerializer,
    GetCookingTnstrctionImageSerialzer,
    GetMenu,
    GetInstruction,
)
from rest_framework import generics
import requests
import os
import openai
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


menu_list = []
genreated_menu = {}


def generate_menu(context_a, context_b):
    # get_receipes_response Session
    print("Generate Menu...")
    ingredient = str(context_a.split(",")).replace("'", '"')
    context = '{"ingredient": ' + ingredient +',"type": "' + context_b + '","no_serving": "2"}'

    get_receipes_response = requests.post(
        "http://127.0.0.1:8000/get_menu", data=context
    )
    get_receipes_response = get_receipes_response.json()
    receipe_html = "<div class='container'>"
    index = 1
    for receipe in get_receipes_response.get("data"):
        receipe_name = receipe.get("name")
        menu_list.append(receipe_name)
        receipe_image = receipe.get("image")
        receipe_html += f"<div class='column'><h1>{index}.{receipe_name}</h1><br>"
        receipe_html += f"<img src='{receipe_image}' alt='{receipe_name} Image'><br>"
        receipe_html += "<h2>Nutrition Information</h2><ul>"

        nutrition = receipe.get("nutrition")
        for key, value in nutrition.items():
            receipe_html += f"<li>{key}: {value}</li>"
        receipe_html += "</ul></div>"
        index += 1
    receipe_html += "</div>"

    return JsonResponse(data={"html": receipe_html, "state": "select-menu"})


def generate_instraction(context_a, context_b):
    if context_a.isnumeric() and ( 0 >= int(context_a) or int(context_a) > 5):
        return JsonResponse(
            data={
                "html": "<p style='color: red;'>Invalid Order; Are You kidding me?<p>",
                "state": "invalid-input",
            }
        )
    print("Generate Instraction...")
    actual_order = int(context_a) - 1
    if actual_order in genreated_menu.keys():
        return JsonResponse(data={"html": genreated_menu[actual_order], "state": "reselect-menu"})

    menu = menu_list[actual_order]
    context = '{ "menu_name" : "' + menu + '","no_serving" : "2"}'
    get_instraction_response = requests.post(
        "http://127.0.0.1:8000/get_instruction",
        data=context
    )

    get_instraction_response = get_instraction_response.json()
    receipe = get_instraction_response.get("Recipe")
    instraction_html = f"<div><h2>{receipe['Name']}</h2><h3>Ingredients</h3><ul>"

    for ingredient in receipe.get("Ingredients"):
        instraction_html += f"<li>{ingredient['Name']}: {ingredient['Amount']}</li>"
    instraction_html += "</ul></div><br><div class='container'>"
    instractions = receipe.get("Instructions")
    for instraction in instractions:
        instraction_detail = instraction.get("instraction_detail")
        instraction_image = instraction.get("image")
        instraction_html += f"<div class='column'><img src='{instraction_image}' alt='Instraction Image'><br>"
        instraction_html += f"<h4>{instraction_detail}</h3></div>"
    instraction_html += "</div>"
    genreated_menu[actual_order] = instraction_html

    return JsonResponse(data={"html": instraction_html, "state": "reselect-menu"})



state_mapping = {
    "input-ingredients": generate_menu,
    "select-menu": generate_instraction,
    "reselect-menu": generate_instraction,
}


def chatPage(request, *args, **kwargs):
    return render(request, "chatPage.html", {})


@csrf_exempt
def processMessage(request, *args, **kwargs):
    if request.method == "POST":
        print("Process Request...")
        state = request.POST.get("State")
        context_a = request.POST.get("InputField")
        context_b = request.POST.get("cookingTypeField")

        return state_mapping[state](context_a, context_b)


def generate_image_list(key, promt_list):
    result = []
    for prompt in promt_list:
        generate_image_response = requests.post(
            url="https://api.openai.com/v1/images/generations",
            headers={
                "Authorization": f"Bearer {settings.OPEN_AI_API_SECRET}",
                "Content-Type": "application/json",
            },
            json={"prompt": prompt, "n": 1, "size": "256x256"},
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


class GenerateCookingInstractionImages(generics.CreateAPIView):
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
        data = json.loads(request.body)
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            json_question = serializer.data
            message = [
                {
                    "role": "user",
                    "content": "What is the circumference in km of the planet Earth?",
                }
            ]
            receive_ingredient = json_question["ingredient"]
            receive_ingredient = ", ".join(receive_ingredient)
            type_ = json_question["type"]
            no_serving = json_question["no_serving"]
            content = (
                'answer me in the following json format only {\r\n  "Recipes": [\r\n    {\r\n      "Name": "<Recipe name>",\r\n      "Nutrition": {\r\n        "Calories": "<Calories count>",\r\n        "Protein": "<Protein count>",\r\n        "Fat": "<Fat count>",\r\n        "Carbohydrates": "<Carbohydrates count>",\r\n        "Fiber": "<Fiber count>"\r\n      }\r\n    }\r\n  ]\r\n} Give me 5 choices for '
                + type_
                + " I can cook with "
                + receive_ingredient
                + " within 30 minutes for a serving of "
                + no_serving
                + ". Also, show me the macro "
            )
            openai.api_key = settings.OPEN_AI_API_SECRET
            message[0]["content"] = content
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # this is "ChatGPT" $0.002 per 1k tokens
                messages=message,
                temperature=0,
            )
            text = completion["choices"][0]["message"]["content"]
            start_index = text.find("{")
            end_index = text.rfind("}")
            json_str = text[start_index : end_index + 1]
            json_obj = json.loads(json_str)
            foods = []
            nutritions = []
            for food in json_obj["Recipes"]:
                foods.append(food["Name"])
                nutritions.append(food["Nutrition"])
            result = generate_image_list("name", foods)
            for i in range(0, 5):
                result[i]["nutrition"] = nutritions[i]
        return JsonResponse({"data": result})
        # return JsonResponse({"data": result})


class GenerateInstruction(generics.ListCreateAPIView):
    serializer_class = GetInstruction

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            json_question = serializer.data
            message = [
                {
                    "role": "user",
                    "content": "What is the circumference in km of the planet Earth?",
                }
            ]
            receive_menu = json_question["menu_name"]
            no_serving = json_question["no_serving"]
            content = (
                'answer me in the following json format only {\r\n  "Recipe": {\r\n    "Name": "<Recipe name>",\r\n    "Servings": "<Recipe servings>",\r\n    "Ingredients": [\r\n      {\r\n        "Name": "<Ingredient name>",\r\n        "Amount": "<Ingredient amount>"\r\n      }\r\n    ],\r\n    "Instructions": ["<Step-by-step instructions>"],\r\n    "Nutrition": {\r\n      "Calories": "<Calories count>",\r\n      "Protein": "<Protein count>",\r\n      "Fat": "<Fat count>",\r\n      "Carbohydrates": "<Carbohydrates count>",\r\n      "Fiber": "<Fiber count>"\r\n    }\r\n  }\r\n}\r\n How do I cook '
                + receive_menu
                + " for "
                + no_serving
                + " people, also show me the macro"
            )
            openai.api_key = settings.OPEN_AI_API_SECRET
            message[0]["content"] = content
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # this is "ChatGPT" $0.002 per 1k tokens
                messages=message,
                temperature=0,
            )
            text = completion["choices"][0]["message"]["content"]
            start_index = text.find("{")
            end_index = text.rfind("}")
            json_str = text[start_index : end_index + 1]
            json_obj = json.loads(json_str)
            instructions = [
                instataction
                for instataction in json_obj.get("Recipe").get("Instructions")
            ]
            json_obj["Recipe"]["Instructions"] = generate_image_list(
                "instraction_detail", instructions
            )

        return JsonResponse(json_obj)
