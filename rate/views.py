from django.shortcuts import render
from .models import Professor, Module, Rating
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

# Create your views here.

@api_view(["POST"])
def register(request):
    data = request.data
    uname = data.get("username")
    email = data.get("email")
    pw = data.get("password")

    # Check if user exists
    if User.objects.filter(username=uname).exists():
        return Response({"error": "Username already in use!"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({"error": "Email already in use!"}, status=status.HTTP_400_BAD_REQUEST)

    # Create user
    user = User.objects.create_user(username=uname, email=email, password=pw)

    return Response({"message": f"New user {uname} registered successfully!"}, status=status.HTTP_201_CREATED)
