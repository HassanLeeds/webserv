from django.shortcuts import render
from .models import Professor, Module, Module_instance, Rating
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
import re

# Create your views here.

def validate_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one number"

    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"

    return True, ""

@api_view(["POST"])
def register(request):
    data = request.data
    uname = data.get("username")
    email = data.get("email")
    pw = data.get("password")

    # Server-side validation
    if not uname:
        return Response({"error": "Username is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    if not email:
        return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    if not validate_email(email):
        return Response({"error": "Invalid email format"}, status=status.HTTP_400_BAD_REQUEST)
    
    if not pw:
        return Response({"error": "Password is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    valid_pw, pw_message = validate_password(pw)
    if not valid_pw:
        return Response({"error": pw_message}, status=status.HTTP_400_BAD_REQUEST)

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
    # Query all module instances with their associated modules and professors
    module_instances = Module_instance.objects.all().select_related('mod')
    
    # Prepare the response data
    module_list = []
    formatted_output = ["Modules List:\n"]
    
    # Add header
    header = "│ {:<10} │ {:<28} │ {:<6} │ {:<10} │ {:<35} │".format(
        "Code", "Name", "Year", "Semester", "Taught by")
    formatted_output.append(header)
    
    for instance in module_instances:
        # Get all professors teaching this module instance
        professors = instance.prof.all()
        prof_info = [{"id": prof.id, "name": prof.name} for prof in professors]
        
        # Format module data for API response
        module_data = {
            "code": instance.mod.code,
            "description": instance.mod.desc,
            "year": instance.year,
            "semester": instance.sem,
            "professors": prof_info
        }
        module_list.append(module_data)
        
        # Add separator line
        formatted_output.append("-" * 105)
        
        code = instance.mod.code
        desc = instance.mod.desc[:28]  # Truncate long descriptions
        year = instance.year
        sem = instance.sem
        
        if not professors:
            # No professors for this module
            row = "│ {:<10} │ {:<28} │ {:<6} │ {:<10} │ {:<35} │".format(
                code, desc, year, sem, "No Professors")
            formatted_output.append(row)
        else:
            # Process first professor
            first_prof = professors[0]
            first_prof_name = first_prof.name
            first_prof_name_list = first_prof_name.split()
            formatted_name = ""
            
            # Format professor name (first initials + last name)
            for name in first_prof_name_list[:-1]:
                formatted_name += name[0] + ". "
            formatted_name += first_prof_name_list[-1]
            
            prof_str = f"{first_prof.id}, Professor {formatted_name}"
            
            # First row with module details and first professor
            row = "│ {:<10} │ {:<28} │ {:<6} │ {:<10} │ {:<35} │".format(
                code, desc, year, sem, prof_str[:35])
            formatted_output.append(row)
            
            # Add additional professors on separate rows
            for prof in professors[1:]:
                prof_name = prof.name
                prof_name_list = prof_name.split()
                formatted_name = ""
                
                for name in prof_name_list[:-1]:
                    formatted_name += name[0] + ". "
                formatted_name += prof_name_list[-1]
                
                prof_str = f"{prof.id}, Professor {formatted_name}"
                row = "│ {:<10} │ {:<28} │ {:<6} │ {:<10} │ {:<35} │".format(
                    "", "", "", "", prof_str[:35])
                formatted_output.append(row)
    
    return Response({
        "modules": module_list,
        "formatted_display": "\n".join(formatted_output)
    }, status=status.HTTP_200_OK)

@api_view(["POST"])
def rate_professor(request):
    # Verify the user is authenticated via token
    if not request.user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
    
    data = request.data
    prof_id = data.get("professor_id")
    module_code = data.get("module_code")
    year = data.get("year")
    semester = data.get("semester")
    stars = data.get("stars")
    
    # Validate input with detailed error messages
    if not prof_id:
        return Response({"error": "Professor ID is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    if not module_code:
        return Response({"error": "Module code is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate year is a valid integer
    if year is None:
        return Response({"error": "Year is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        year = int(year)
    except (ValueError, TypeError):
        return Response({"error": "Year must be a valid number"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate semester is 1 or 2
    if semester is None:
        return Response({"error": "Semester is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        semester = int(semester)
        if semester not in [1, 2]:
            return Response({"error": "Semester must be either 1 or 2"}, status=status.HTTP_400_BAD_REQUEST)
    except (ValueError, TypeError):
        return Response({"error": "Semester must be a valid number (1 or 2)"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate stars is between 1 and 5
    if stars is None:
        return Response({"error": "Rating (stars) is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        stars = int(stars)
        if stars < 1 or stars > 5:
            return Response({"error": "Stars must be between 1 and 5"}, status=status.HTTP_400_BAD_REQUEST)
    except (ValueError, TypeError):
        return Response({"error": "Stars must be a valid number between 1 and 5"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Find the professor
    try:
        professor = Professor.objects.get(id=prof_id)
    except Professor.DoesNotExist:
        return Response({"error": f"Professor with ID {prof_id} not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Find the module instance
    try:
        module = Module.objects.get(code=module_code)
        module_instance = Module_instance.objects.get(mod=module, year=year, sem=semester)
        
        # Verify professor teaches this module instance
        if not module_instance.prof.filter(id=prof_id).exists():
            return Response(
                {"error": f"Professor {prof_id} does not teach module {module_code} in year {year}, semester {semester}"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Module.DoesNotExist:
        return Response({"error": f"Module with code {module_code} not found"}, status=status.HTTP_404_NOT_FOUND)
    except Module_instance.DoesNotExist:
        return Response(
            {"error": f"Module instance for {module_code} in year {year}, semester {semester} not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Create the rating
    rating = Rating.objects.create(
        stars=stars,
        professor=professor,
        module=module_instance
    )
    
    # Prepare a formatted confirmation message
    formatted_confirmation = f"""
╔══════════════════════════════════════════════════════════════════╗
║                       RATING SUBMITTED                           ║
╠══════════════════════════════════════════════════════════════════╣
║ Professor: {professor.name:<46} ║
║ Module:    {module.desc[:44]:<46} ║
║ Year:      {year:<46} ║
║ Semester:  {semester:<46} ║
║ Rating:    {'★' * stars + '☆' * (5 - stars):<46} ║
╚══════════════════════════════════════════════════════════════════╝
"""
    
    return Response({
        "message": f"Rating submitted successfully for Professor {professor.name}, Module {module.desc}",
        "formatted_confirmation": formatted_confirmation
    }, status=status.HTTP_201_CREATED)
