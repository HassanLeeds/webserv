import argparse
import requests
import sys
import getpass
import re
import json
import time

URL = "http://127.0.0.1:8000/api"

class APIClient:

    def __init__(self, base_url="http://127.0.0.1:8000/api"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.token = None

    def register(self, username, email, password):
        url = f"{self.base_url}/register/"
        data = {
            "username": username,
            "email": email,
            "password": password
        }

        response = self.make_request("post", url, json=data)
        return response
    
    def login(self, username, password):
        url = f"{self.base_url}/login/"
        data = {
            "username": username,
            "password": password
        }

        response = self.make_request("post", url, json=data)

        token = response.get("data", {}).get("token")

        if token:
            self.token = token
            # Add the token to the session headers
            self.session.headers.update({"Authorization": f"Token {token}"})

        return response

    def list_modules(self):
        url = f"{self.base_url}/list/"  # Adjust URL to match your API endpoint
        response = self.make_request("get", url)
        return response

    def make_request(self, method, url, **kwargs):
        start_time = time.time()
        
        try:
            # If we have a token but it's not in headers yet, add it
            if self.token and "Authorization" not in self.session.headers:
                self.session.headers.update({"Authorization": f"Token {self.token}"})
                
            response = self.session.request(method, url, **kwargs)
            end_time = time.time()
            result = {
                "status_code": response.status_code,
                "response_time": round((end_time - start_time) * 1000, 2),  # ms
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

def register(api_client, username, email, password, verbose=False): 
    # Test the actual registration
    response = api_client.register(username, email, password)

    if response.get("status_code") == 201:
        print(f"SUCCESS: {response.get('data', {}).get('message', 'Registration successful')}")
    else:
        error_message = "Registration failed"

        # Try to extract error message from response
        if isinstance(response.get('data'), dict) and 'error' in response.get('data', {}):
            error_message = response.get('data', {}).get('error')
        elif "error" in response:
            error_message = response.get('error')

        print(f"ERROR: {error_message}")

    if verbose:
        print("\nDetails:")
        print(f"  Response time: {response.get('response_time', 'N/A')} ms")
        print(f"  Headers: {json.dumps(response.get('headers', {}), indent=2)}")

    return response.get("status_code") == 201


def login(api_client, username, password, verbose=False): 
    # Test the actual registration
    response = api_client.login(username, password)

    if response.get("status_code") == 200:
        print(f"SUCCESS: {response.get('data', {}).get('message', 'Registration successful')}")
    else:
        error_message = "Log-in failed"

        # Try to extract error message from response
        if isinstance(response.get('data'), dict) and 'error' in response.get('data', {}):
            error_message = response.get('data', {}).get('error')
        elif "error" in response:
            error_message = response.get('error')

        print(f"ERROR: {error_message}")

    if verbose:
        print("\nDetails:")
        print(f"  Response time: {response.get('response_time', 'N/A')} ms")
        print(f"  Headers: {json.dumps(response.get('headers', {}), indent=2)}")

    return response.get("status_code")==200

def list_modules(api_client):
    response = api_client.list_modules()
    
    if response.get("status_code") == 200:
        print(f"List of modules and their professors:")
        modules = response.get("data", {}).get("modules", [])
        
        if not modules:
            print("No modules found")
            return
        
        print("Modules List:")
        
        print("│ {:<10} │ {:<28} │ {:<6} │ {:<10} │ {:<35} │".format(
            "Code", "Name", "Year", "Semester", "Taught by"))
        for module in modules:
            print("-" * 105)
            code = module.get("code", "N/A")
            desc = module.get("description", "N/A")
            year = module.get("year", "N/A")
            profs = module.get("professors", [])
            sem = module.get("semester", "N/A")

            if not profs:
                print("│ {:<10} │ {:<28} │ {:<6} │ {:<10} │ {:<28} │".format(
                    code, desc, year, sem, "No Professors"))
            
            else:
                # Print first professor in first row with module details
                first_prof = profs[0]
                first_prof_name = first_prof.get('name', 'Unkown')
                first_prof_name_list = first_prof_name.split()
                first_prof_name = ""
                for name in first_prof_name_list[:-1]:
                    first_prof_name += name[0] + ". "
                first_prof_name += first_prof_name_list[-1]

                prof_str = f"{first_prof.get('id', 'N/A')}, Professor {first_prof_name}"
                print("│ {:<10} │ {:<28} │ {:<6} │ {:<10} │ {:<35} │".format(
                    code, desc[:28], year, sem, prof_str[:35]))
                
                for prof in profs[1:]:
                    
                    prof_name = prof.get('name', 'Unkown')
                    prof_name_list = prof_name.split()
                    prof_name = ""
                    for name in prof_name_list[:-1]:
                        prof_name += name[0] + ". "
                    prof_name += prof_name_list[-1]
                    prof_str = f"{prof.get('id', 'N/A')}, Professor {prof_name}"
                    print("│ {:<10} │ {:<28} │ {:<6} │ {:<10} │ {:<35} │".format(
                        code, desc, year, sem, prof_str[:35]))
        else:
            if "error" in response:
                error_message = response.get('error')
                print(f"ERROR: {error_message}")
def main():

    # Initialize API client
    api_client = APIClient(URL)

    print("Welcome to the professor rating client!\n")
    print("To exit the client type 'q' or 'quit'")
    
    print("Type 'h' or 'help' for a list of available commands.\n")
    logged_in = False
    while(True):
        command = input("-> ")
        if logged_in == False:
            # Print help information
            if command.strip().lower() == "h" or command.strip == "help":
                print("1) register: Registers a new user\
                        \n2) login: Login using existing account")

                # Register new user
            elif command.strip().lower() == "register":
                # Get username
                username = input("Enter username: ")

                email = input("Enter email: ")
                while not validate_email(email):
                    print("Invalid email format. Please try again.")
                    email = input("Enter email: ")

                password = getpass.getpass("Enter password: ")
                valid, message = validate_password(password)
                while not valid:
                    print(f"Invalid password: {message}")
                    password = getpass.getpass("Enter password: ")
                    valid, message = validate_password(password)

                # Confirm password
                confirm_password = getpass.getpass("Confirm password: ")
                while password != confirm_password:
                    print("Passwords do not match. Please try again.")
                    password = getpass.getpass("Enter password: ")
                    confirm_password = getpass.getpass("Confirm password: ")

                # Test registration
                success = register(api_client, username, email, password)
                if not success:
                    print("Please login or try again")

            elif command.strip().lower() == "login":
                username = input("Enter username: ")
                password = getpass.getpass("Enter password: ")

                # Login
                success = login(api_client, username, password)
                if success:
                    logged_in = True
                    print("Type 'h' or 'help' for a list of logged-in commands.")
                else:
                    print("Please try again or register")

        elif logged_in == True:
            # Print help information
            if command.strip().lower() == "h" or command.strip == "help":
                print("logout: Log-out of account")

            elif command.strip().lower() == "logout":
                logged_in = False
                print("Successfully logged-out")

            elif command.strip().lower() == "list":
                list_modules(api_client)

            else:
                print("Invalid command: type 'h' or 'help' for a list of logged-in commands.")

if __name__ == "__main__":
    main()
