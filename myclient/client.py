import argparse
import requests
import sys
import getpass
import json
import time

URL = "http://127.0.0.1:8000/api"

class APIClient:

    def __init__(self, base_url=URL):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.token = None
        self.username = None

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
            self.username = username
            # Add the token to the session headers
            self.session.headers.update({"Authorization": f"Token {token}"})

        return response

    def list_modules(self):
        url = f"{self.base_url}/list/"
        response = self.make_request("get", url)
        return response
    
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

    def view(self):
        url = f"{self.base_url}/view/"
        response = self.make_request("get", url)
        return response

    def average(self, professor_id, module_code):
        url = f"{self.base_url}/average/"

        data = {
            "professor_id": professor_id,
            "module_code": module_code
        }

        response = self.make_request("post", url, json=data)
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

def register(api_client, verbose=False): 
    # Get user input
    username = input("Enter username: ")
    email = input("Enter email: ")
    password = getpass.getpass("Enter password: ")
    confirm_password = getpass.getpass("Confirm password: ")
    
    # Simple check for password match (this is still reasonable to do client-side)
    if password != confirm_password:
        print("ERROR: Passwords do not match.")
        return False
    
    # Test the actual registration
    response = api_client.register(username, email, password)

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

    if verbose:
        print("\nDetails:")
        print(f"  Response time: {response.get('response_time', 'N/A')} ms")
        print(f"  Headers: {json.dumps(response.get('headers', {}), indent=2)}")

    return False

def login(api_client, verbose=False): 
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")

    # Test the actual login
    response = api_client.login(username, password)

    if response.get("status_code") == 200:
        print(f"SUCCESS: {response.get('data', {}).get('message', 'Login successful')}")
        return True
    else:
        error_message = "Login failed"

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

    return False

def list_modules(api_client):
    response = api_client.list_modules()
    
    if response.get("status_code") == 200:
        # Simply print the server-formatted display
        formatted_display = response.get("data", {}).get("formatted_display")
        
        if formatted_display:
            print(formatted_display)
        else:
            modules = response.get("data", {}).get("modules", [])
            if not modules:
                print("No modules found")
            else:
                print("Module list available but formatted display not provided")
    else:
        if "error" in response.get('data', {}):
            error_message = response.get('data', {}).get('error')
            print(f"ERROR: {error_message}")
        elif "error" in response:
            error_message = response.get('error')
            print(f"ERROR: {error_message}")
        else:
            print("ERROR: Failed to retrieve modules")

def rate_professor(professor_id, module_code, year, semester, stars, api_client):
    
    # Convert inputs to proper types without validation
    try:
        year = int(year)
        semester = int(semester)
        stars = int(stars)
    except ValueError:
        # Let the server handle the validation error
        pass
    
    response = api_client.rate_professor(
        professor_id=professor_id,
        module_code=module_code,
        year=year,
        semester=semester,
        stars=stars
    )
    
    if response.get("status_code") == 201:
        # Check if there's a formatted confirmation from the server
        formatted_confirmation = response.get("data", {}).get("formatted_confirmation")
        if formatted_confirmation:
            print(formatted_confirmation)
        else:
            print(f"SUCCESS: {response.get('data', {}).get('message', 'Rating submitted successfully')}")
    else:
        error_message = "Rating submission failed"
        
        if isinstance(response.get('data'), dict) and 'error' in response.get('data', {}):
            error_message = response.get('data', {}).get('error')
        elif "error" in response:
            error_message = response.get('error')
            
        print(f"ERROR: {error_message}")

def view(api_client):
    response = api_client.view()

    if response.get("status_code") == 200:
        formatted_display = response.get("data", {}).get("formatted_display")
        
        if formatted_display:
            print(formatted_display)
        else:
            print("No professor ratings available")

    else:
        if "error" in response.get("data", {}):
            err_msg = response.get("data", {}).get("error")
            print(err_msg)
        elif "error" in response:
            err_msg = response.get("error")
            print(err_msg)
        else:
            print("ERROR: Failed to retrieve professor ratings")

def average(professor_id, module_code, api_client):
    response = api_client.average(professor_id, module_code)

    if response.get("status_code") == 200:
        display = response.get("data", {}).get("display")

        if display:
            print(display)
        else:
            print("Average rating not available")

    else:
        if "error" in response.get("data", {}):
            err_msg = response.get("data", {}).get("error")
            print(err_msg)
        elif "error" in response:
            err_msg = response.get("error")
            print(err_msg)
        else:
            print("ERROR: Failed to retrieve professor average rating")

def main():
    # Initialize API client
    api_client = APIClient(URL)

    print("Welcome to the professor rating client!\n")
    print("To exit the client type 'q' or 'quit'")
    
    print("Type 'h' or 'help' for a list of available commands.\n")
    logged_in = False
    
    while True:
        command = input("-> ")
        command = command.split()

        if command[0] in ["q", "quit", "exit"]:
            print("Goodbye!")
            break

        elif command[0] == "list":
            list_modules(api_client)

        elif command[0] == "view":
            view(api_client)

        elif command[0] == "average":
            if len(command) < 3:
                print("Please use the command as following: 'average professor_id module_code'")
            else:
                average(command[1], command[2], api_client)

            
        elif not logged_in:
            # Print help information
            if command[0] in ["h", "help"]:
                print("Available commands:")
                print("1) register: Register a new user")
                print("2) login: Login using existing account")
                print("3) list: List all modules and professors")
                print("4) view: List ratings of all professors")
                print("5) average professor_id module_code: Display average rating for a professor in a module")
                print("6) q/quit/exit: Exit the application")

            # Register new user
            elif command[0] == "register":
                success = register(api_client)
                if not success:
                    print("Please login or try again")

            elif command[0] == "login":
                success = login(api_client)
                if success:
                    logged_in = True
                else:
                    print("Please try again or register")

            else:
                print("Invalid command: type 'h' or 'help' for a list of commands.")

        else:  # logged_in == True
            # Print help information
            if command[0] in ["h", "help"]:
                print("Available commands:")
                print("1) list: List all modules and professors")
                print("2) average professor_id module_code: Display average rating for a professor in a module")
                print("3) view: List ratings of all professors")
                print("4) rate professor_id module_code year semester rating: Rate a professor for a specific module")
                print("5) logout: Log out of your account")
                print("6) q/quit/exit: Exit the application")

            elif command[0] == "logout":
                logged_in = False
                api_client.token = None
                api_client.username = None
                api_client.session.headers.pop("Authorization", None)
                print("Successfully logged out")

            elif command[0] == "rate":
                if len(command) < 6:
                    print("Please use the command as following: 'rate professor_id module_code year semester rating'")
                else:

                    rate_professor(command[1], command[2], command[3], command[4], command[5], api_client)

            else:
                print("Invalid command: type 'h' or 'help' for a list of logged-in commands.")

if __name__ == "__main__":
    main()
