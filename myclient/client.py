#!/usr/bin/env python3
import argparse
import requests
import sys
import getpass
import re
import json
import time

class APIClient:
    """Client for interacting with the API"""
    
    def __init__(self, base_url="http://127.0.0.1:8000/api"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.token = None
    
    def register(self, username, email, password):
        """Register a new user"""
        url = f"{self.base_url}/register/"
        data = {
            "username": username,
            "email": email,
            "password": password
        }
        
        response = self.make_request("post", url, json=data)
        return response
    
    def make_request(self, method, url, **kwargs):
        """Make a request to the API with proper error handling"""
        start_time = time.time()
        
        try:
            response = self.session.request(method, url, **kwargs)
            end_time = time.time()
            
            # Create a response object with timing information
            result = {
                "status_code": response.status_code,
                "response_time": round((end_time - start_time) * 1000, 2),  # ms
                "headers": dict(response.headers),
            }
            
            # Try to parse JSON response
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
    """Basic email validation using regex"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Basic password validation"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one number"
    
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"
    
    return True, ""

def test_register(api_client, username, email, password, verbose=False):
    """Test the register endpoint"""
    # Test validation
    print(f"\n[TEST] Registration for user: {username}")
    
    # Test the actual registration
    response = api_client.register(username, email, password)
    
    if response.get("status_code") == 201:
        print(f"✓ SUCCESS: Registration successful")
        print(f"  Message: {response.get('data', {}).get('message', 'N/A')}")
    else:
        print(f"✗ FAILED: Registration failed")
        print(f"  Status code: {response.get('status_code')}")
        print(f"  Response: {response.get('data', 'No data')}")
    
    if verbose:
        print("\nDetails:")
        print(f"  Response time: {response.get('response_time', 'N/A')} ms")
        print(f"  Headers: {json.dumps(response.get('headers', {}), indent=2)}")
    
    return response.get("status_code") == 201

def stress_test_register(api_client, base_username, base_email, password, count=10, verbose=False):
    """Perform a simple stress test by registering multiple users"""
    print(f"\n[STRESS TEST] Registering {count} users")
    
    success_count = 0
    failed_count = 0
    total_time = 0
    
    for i in range(count):
        username = f"{base_username}{i}"
        email = f"{base_email.split('@')[0]}{i}@{base_email.split('@')[1]}"
        
        start_time = time.time()
        response = api_client.register(username, email, password)
        end_time = time.time()
        
        if response.get("status_code") == 201:
            success_count += 1
        else:
            failed_count += 1
        
        total_time += (end_time - start_time)
        
        if verbose:
            print(f"  User {i+1}/{count}: {username} - {'SUCCESS' if response.get('status_code') == 201 else 'FAILED'}")
    
    print(f"\nResults:")
    print(f"  Successful registrations: {success_count}/{count}")
    print(f"  Failed registrations: {failed_count}/{count}")
    print(f"  Average response time: {round((total_time / count) * 1000, 2)} ms")
    
    return success_count, failed_count

def main():
    parser = argparse.ArgumentParser(description="CLI for testing the API")
    parser.add_argument("--url", default="http://127.0.0.1:8000/api", 
                        help="API base URL (default: http://127.0.0.1:8000/api)")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Register command
    register_parser = subparsers.add_parser("register", help="Register a new user")
    register_parser.add_argument("--username", help="Username for registration")
    register_parser.add_argument("--email", help="Email for registration")
    register_parser.add_argument("--password", help="Password for registration (not recommended, use prompt instead)")
    register_parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed response")
    
    # Stress test command
    stress_parser = subparsers.add_parser("stress", help="Perform stress testing")
    stress_parser.add_argument("--base-username", default="testuser", help="Base username for test users")
    stress_parser.add_argument("--base-email", default="test@example.com", help="Base email for test users")
    stress_parser.add_argument("--password", default="TestPass123", help="Password for test users")
    stress_parser.add_argument("--count", type=int, default=10, help="Number of test users to create")
    stress_parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed progress")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize API client
    api_client = APIClient(args.url)
    
    # Execute command
    if args.command == "register":
        # Get username
        username = args.username
        if not username:
            username = input("Enter username: ")
        
        # Get email
        email = args.email
        if not email:
            email = input("Enter email: ")
            while not validate_email(email):
                print("Invalid email format. Please try again.")
                email = input("Enter email: ")
        
        # Get password
        password = args.password
        if not password:
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
        success = test_register(api_client, username, email, password, args.verbose)
        sys.exit(0 if success else 1)
        
    elif args.command == "stress":
        success_count, failed_count = stress_test_register(
            api_client, 
            args.base_username, 
            args.base_email, 
            args.password, 
            args.count, 
            args.verbose
        )
        sys.exit(0 if failed_count == 0 else 1)

if __name__ == "__main__":
    main()
