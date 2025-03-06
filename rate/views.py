from django.shortcuts import render
from .models import Professor, Module, Rating
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate

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

@api_view(["POST"])
def login(request):
    data = request.data
    uname = data.get("username")
    pw = data.get("password")

    # Check if credentials are provided
    if not uname or not pw:
        return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        # Authenticate the user
        user = authenticate(username=uname, password=pw)
        
        if user is not None:
            # Generate or get authentication token
            from rest_framework.authtoken.models import Token
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                "message": f"User {uname} logged-in successfully!",
                "token": token.key
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(["GET"])
def list_modules(request):
    # Verify the user is authenticated via token
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Get all modules with their associated professors
    from .models import Module, Professor
    
    # Query all modules
    modules = Module.objects.all()
    
    # Prepare the response data
    module_list = []
    for module in modules:
        # Get all professors teaching this module
        professors = module.prof.all()
        prof_info = [{"id": prof.id, "name": prof.name} for prof in professors]
        
        module_list.append({
            "code": module.code,
            "description": module.desc,
            "year": module.year,
            "semester": module.sem,
            "professors": prof_info
        })
    
    return Response({
        "modules": module_list
    }, status=status.HTTP_200_OK)
