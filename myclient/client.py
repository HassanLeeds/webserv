import argparse
import requests
import sys
import getpass
import json
import time

URL = "http://127.0.0.1:8000/api"

# APIClient class
# Creates a client that communicates directly with the server
class APIClient:

    def __init__(self, base_url=URL):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.token = None
        self.username = None

    # Function to send registration request to the server
    def register(self, username, email, password):
        url = f"{self.base_url}/register/"
        data = {
            "username": username,
            "email": email,
            "password": password
        }

        response = self.make_request("post", url, json=data)
        return response
    
    # Function to send login request to the server
    def login(self, url, username, password):
        data = {
            "username": username,
            "password": password
        }

        response = self.make_request("post", url, json=data)
        
        try:
            token = response.get("data", {}).get("token")
        except AttributeError:
            token = None

        if token:
            self.token = token
            self.username = username
            # Add the token to the session headers
            self.session.headers.update({"Authorization": f"Token {token}"})

        return response

    # Function to send logout request to the server
    def logout(self):
        url = f"{self.base_url}/logout/"
        response = self.make_request("delete", url)
        
        # Regardless of server response, clear local authentication data
        self.token = None
        self.username = None
        if "Authorization" in self.session.headers:
            self.session.headers.pop("Authorization")
        
        return response

    # Function to send list request to the server
    def list_modules(self):
        url = f"{self.base_url}/list/"
        response = self.make_request("get", url)
        return response
    
    # Function to send new rating request to the server
    def rate_professor(self, professor_id, module_code, year, semester, stars):
        url = f"{self.base_url}/rate/"
        data = {
            "professor_id": professor_id,
            "module_code": module_code,
            "year": year,
            "semester": semester,
            "stars": stars
        }
        response = self.make_request("post", url, json=data)
        return response

    # Function to send view request to the server
    def view(self):
        url = f"{self.base_url}/view/"
        response = self.make_request("get", url)
        return response

    # Function to send average request to the server
    def average(self, professor_id, module_code):
        url = f"{self.base_url}/average/"

        data = {
            "professor_id": professor_id,
            "module_code": module_code
        }

        response = self.make_request("post", url, json=data)
        return response

    # Function that builds and sends requests and receives responses
    def make_request(self, method, url, **kwargs):
        
        try:
            # If we have a token but it's not in headers yet, add it
            if self.token and "Authorization" not in self.session.headers:
                self.session.headers.update({"Authorization": f"Token {self.token}"})
                
            response = self.session.request(method, url, **kwargs)
            result = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
            }

            try:
                result["data"] = response.json()
            except ValueError:
                result["data"] = response.text

            return result

        except requests.exceptions.ConnectionError:
            return {
                "error": f"Connection error: Could not connect to {url}",
                "status_code": None
            }
        except Exception as e:
            return {
                "error": f"Unexpected error: {str(e)}",
                "status_code": None
            }

# Gets user input for registration and invokes APIClient registration function
def register(api_client, verbose=False): 
    # Get user input
    username = input("Enter username: ")
    email = input("Enter email: ")
    password = getpass.getpass("Enter password: ")
    confirm_password = getpass.getpass("Confirm password: ")
    
    # Make sure password inputs match
    if password != confirm_password:
        print("ERROR: Passwords do not match.")
        return False
    
    # Invoke registration request
    response = api_client.register(username, email, password)


    # Handle all responses and errors

    if response.get("status_code") == 201:
        print(f"SUCCESS: {response.get('data', {}).get('message', 'Registration successful')}")
        return True
    else:
        error_message = "Registration failed"

        # Try to extract error message from response
        if isinstance(response.get('data'), dict) and 'error' in response.get('data', {}):
            error_message = response.get('data', {}).get('error')
        elif "error" in response:
            error_message = response.get('error')

        print(f"ERROR: {error_message}")

    return False

# Gets user input for login and invokes APIClient login function
def login(url, api_client): 
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")

    # Invoke login request
    response = api_client.login(url, username, password)

    # Handle all responses and errors

    if response.get("status_code") == 200:
        print(f"{response.get('data', {}).get('message', 'Login successful')}")
        return True
    elif response.get("status_code") == 404:
        print("URL not found, please check for any spellig mistakes")
    elif response.get("status_code") == 500:
        print("URL must end with a front slash '/'")
    else:
        error_message = "Login failed"

        # Try to extract error message from response
        if isinstance(response.get('data'), dict) and 'error' in response.get('data', {}):
            error_message = response.get('data', {}).get('error')
        elif "error" in response:
            error_message = response.get('error')

        print(f"ERROR: {error_message}")

    return False

#  Invokes APIClient list function
def list_modules(api_client):
    response = api_client.list_modules()
    
    # Handle all responses and errors
    if response.get("status_code") == 200:
        modules = response.get("data", {}).get("modules", [])
        if not modules:
            print("No modules found")
        else:
            # Format the module data for user to see
            formatted_output = ["Modules List:\n"]
            
            # Add header
            header = "│ {:<8} │ {:<30} │ {:<4} │ {:<8} │ {:<40} │".format(
                "Code", "Name", "Year", "Semester", "Taught by")
            formatted_output.append(header)
            
            for module in modules:
                code = module["code"]
                desc = module["description"][:30]  # Truncate long descriptions
                year = module["year"]
                sem = module["semester"]
                professors = module["professors"]
                
                # Add separator line
                formatted_output.append("-" * 105)
                
                if not professors:
                    # No professors for this module
                    row = "│ {:<8} │ {:<30} │ {:<4} │ {:<8} │ {:<40} │".format(
                        code, desc, year, sem, "No Professors")
                    formatted_output.append(row)
                else:
                    # Process first professor
                    first_prof = professors[0]
                    first_prof_name = first_prof["name"]
                    first_prof_name_list = first_prof_name.split()
                    formatted_name = ""
                    
                    # Format professor name (initials + last name)
                    for name in first_prof_name_list[:-1]:
                        formatted_name += name[0] + ". "
                    formatted_name += first_prof_name_list[-1]
                    
                    prof_str = f"{first_prof['id']}, Professor {formatted_name}"
                    
                    # First row with module details and first professor
                    row = "│ {:<8} │ {:<30} │ {:<4} │ {:<8} │ {:<40} │".format(
                        code, desc, year, sem, prof_str[:35])
                    formatted_output.append(row)
                    
                    # Add additional professors on separate rows
                    for prof in professors[1:]:
                        prof_name = prof["name"]
                        prof_name_list = prof_name.split()
                        formatted_name = ""
                        
                        for name in prof_name_list[:-1]:
                            formatted_name += name[0] + ". "
                        formatted_name += prof_name_list[-1]
                        
                        prof_str = f"{prof['id']}, Professor {formatted_name}"
                        row = "│ {:<8} │ {:<30} │ {:<4} │ {:<8} │ {:<40} │".format(
                            "", "", "", "", prof_str[:35])
                        formatted_output.append(row)
            
            print("\n".join(formatted_output))
    else:
        if "error" in response.get('data', {}):
            error_message = response.get('data', {}).get('error')
            print(f"ERROR: {error_message}")
        elif "error" in response:
            error_message = response.get('error')
            print(f"ERROR: {error_message}")
        else:
            print("ERROR: Failed to retrieve modules")

# Invokes APIClient rate_professor function using data from arguments
def rate_professor(professor_id, module_code, year, semester, stars, api_client):
    
    # Convert inputs to proper types
    try:
        year = int(year)
        semester = int(semester)
        stars = int(stars)
    except ValueError:
        # Server handles validation errors
        pass
    
    # Create resonse JSON
    response = api_client.rate_professor(
        professor_id=professor_id,
        module_code=module_code,
        year=year,
        semester=semester,
        stars=stars
    )
    
    # Handle resoponse messages and errors
    if response.get("status_code") == 201:
        # Format the response for client to see 
        data = response.get("data", {})
        professor = data.get("professor", {})
        module = data.get("module", {})
        rating = data.get("stars", 0)
        
        formatted_response = f"""
--------------------------------------------------------------------
                       RATING SUBMITTED                           
--------------------------------------------------------------------
  Professor: {professor.get('name', 'Unknown'):<50} 
  Module:    {module.get('description', 'Unknown')[:49]:<50} 
  Year:      {data.get('year', 'Unknown'):<50} 
  Semester:  {data.get('semester', 'Unknown'):<50} 
  Rating:    {'★' * rating + '☆' * (5 - rating):<50} 
--------------------------------------------------------------------
"""
        print(formatted_confirmation)
    else:
        # Check for the specific case of an already existing rating
        if response.get("status_code") == 400 and "existing_rating" in response.get("data", {}):
            existing_rating = response.get("data", {}).get("existing_rating", 0)
            error_message = response.get("data", {}).get("error", "You have already rated this professor in this module instance")
            
            print(f"ERROR: {error_message}")
            print(f"Your previous rating: {'★' * existing_rating + '☆' * (5 - existing_rating)}")
            
        else:
            error_message = "Rating submission failed"
            
            if isinstance(response.get('data'), dict) and 'error' in response.get('data', {}):
                error_message = response.get('data', {}).get('error')
            elif "error" in response:
                error_message = response.get('error')
                
            print(f"ERROR: {error_message}")

# Invokes APIClient view function
def view(api_client):
    # Invike view request
    response = api_client.view()

    # Handle all responses and error messages
    if response.get("status_code") == 200:
        professors = response.get("data", {}).get("professors", [])
        
        if not professors:
            print("No professor ratings available")
        else:
            # Format the professor ratings for the user to see
            formatted_output = ["Professor Ratings:\n"]
            
            for professor in professors:
                # Format professor name (initials + last name)
                name = professor.get("name", "")
                name_parts = name.split()
                formatted_name = ""
                
                for part in name_parts[:-1]:
                    formatted_name += part[0] + ". "
                formatted_name += name_parts[-1] if name_parts else ""
                
                avg_rating = professor.get("average_rating", 0)
                rating_count = professor.get("rating_count", 0)
                prof_id = professor.get("id", "")
                
                # Round to nearest integer for display
                rounded_rating = round(avg_rating)
                
                if rating_count > 0:
                    star_display = f"{'★' * rounded_rating + '☆' * (5 - rounded_rating):<53}" 
                    formatted_output.append(f"The rating of Professor {formatted_name} ({prof_id}) is {star_display}")
                else:
                    formatted_output.append(f"Professor {formatted_name} ({prof_id}) doesn't have a rating")
            
            print("\n".join(formatted_output))
    else:
        if "error" in response.get("data", {}):
            err_msg = response.get("data", {}).get("error")
            print(f"ERROR: {err_msg}")
        elif "error" in response:
            err_msg = response.get("error")
            print(f"ERROR: {err_msg}")
        else:
            print("ERROR: Failed to retrieve professor ratings")

# Invokes APIClient average function using arguments
def average(professor_id, module_code, api_client):
    # Invoke average request
    response = api_client.average(professor_id, module_code)

    # Handle all response messages and errors
    if response.get("status_code") == 200:
        data = response.get("data", {})
        professor = data.get("professor", {})
        module = data.get("module", {})
        teaches_module = data.get("teaches_module", False)
        avg_rating = data.get("average_rating")
        rating_count = data.get("rating_count", 0)
        
        # Format professor name
        name = professor.get("name", "")
        name_parts = name.split()
        formatted_name = ""
        
        for part in name_parts[:-1]:
            formatted_name += part[0] + ". "
        formatted_name += name_parts[-1] if name_parts else ""
        
        prof_id = professor.get("id", "")
        mod_desc = module.get("description", "")
        mod_code = module.get("code", "")
        
        if not teaches_module:
            print(f"Professor {formatted_name} ({prof_id}) does not teach {mod_desc} ({mod_code})")
        elif avg_rating is None or rating_count == 0:
            print(f"Professor {formatted_name} ({prof_id}) has no ratings for {mod_desc} ({mod_code})")
        else:
            # Round to nearest integer for display
            stars = round(avg_rating)
            output = f"The rating of Professor {formatted_name} ({prof_id}) in module {mod_desc} ({mod_code}) is:\n{'★' * stars + '☆' * (5 - stars)}"
            print(output)
    else:
        if "error" in response.get("data", {}):
            err_msg = response.get("data", {}).get("error")
            print(f"ERROR: {err_msg}")
        elif "error" in response:
            err_msg = response.get("error")
            print(f"ERROR: {err_msg}")
        else:
            print("ERROR: Failed to retrieve professor average rating")

def main():
    # Initialize API client object
    api_client = APIClient(URL)

    print("Welcome to the professor rating client!\n")
    print("To exit the client type 'q' or 'quit'")
    
    print("Type 'h' or 'help' for a list of available commands.\n")
    logged_in = False
    
    # Keep running until loop breaks
    while True:
        command = input("-> ")

        # Divide command into seperate arguments
        command = command.split()
        
        if not command:
            continue

        if command[0] in ["q", "quit", "exit"]:
            print("Goodbye!")
            break

        # List, view and average commands work whether logged in or out
        elif command[0] == "list":
            list_modules(api_client)

        elif command[0] == "view":
            view(api_client)

        elif command[0] == "average":
            if len(command) < 3:
                print("Please use the command as following: 'average <professor_id> <module_code>'")
            else:
                average(command[1], command[2], api_client)

            
        elif not logged_in:
            # Print help information
            if command[0] in ["h", "help"]:
                print("Available commands:")
                print("1) register: Register a new user")
                print("2) login <api_url>: Login to provided api using existing account")
                print("3) list: List all modules and professors")
                print("4) view: List ratings of all professors")
                print("5) average <professor_id> <module_code>: Display average rating for a professor in a module")
                print("6) q/quit/exit: Exit the application")

            # Register new user
            elif command[0] == "register":
                success = register(api_client)
                if not success:
                    print("Please login or try again")

            elif command[0] == "login":
                if len(command) < 2:
                    print("Please use the command as following: 'login <URL>'")
                else:
                    success = login(command[1],api_client)
                    if success:
                        logged_in = True

            else:
                print("Invalid command: type 'h' or 'help' for a list of logged-in commands.")
        
        else:  # logged_in == True
            # Print help information
            if command[0] in ["h", "help"]:
                print("Available commands:")
                print("1) list: List all modules and professors")
                print("2) average <professor_id> <module_code>: Display average rating for a professor in a module")
                print("3) view: List ratings of all professors")
                print("4) rate <professor_id> <module_code> <year> <semester> <rating>: Rate a professor for a specific module")
                print("5) logout: Log out of your account")
                print("6) q/quit/exit: Exit the application")

            
            elif command[0] == "logout":
                response = api_client.logout()
                
                if response.get("status_code") in [200, 204]:
                    print("Successfully logged out")
                else:
                    error_message = "Logout completed with warning"
                    
                    if isinstance(response.get('data'), dict) and 'error' in response.get('data', {}):
                        error_message = response.get('data', {}).get('error')
                    elif "error" in response:
                        error_message = response.get('error')
                        
                    print(f"WARNING: {error_message}, but you've been logged out locally")
                
                logged_in = False

            elif command[0] == "rate":

                if len(command) < 6:
                    print("Please use the command as following: 'rate <professor_id> <module_code> <year> <semester> <rating>'")
                
                else:
                    rate_professor(command[1], command[2], command[3], command[4], command[5], api_client)

            else:
                print("Invalid command: type 'h' or 'help' for a list of logged-in commands.")


if __name__ == "__main__":
    main()
