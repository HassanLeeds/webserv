# Professor Rating Service Client

## Overview
This command-line client application provides an interface to interact with the Professor Rating Service API. It allows users to register, login, view modules and professors, check ratings, and submit new ratings for professors teaching specific modules.

## Requirements
- Python 3.x
- Required packages: `requests`

To install the required packages:
```
pip install requests
```

## Usage
Run the client application using:
```
python client.py
```

## Available Commands

### Before Login
- `register` - Register a new user account
- `login <url>` - Login to the service (URL format: `http://example.pythonanywhere.com/api`)
- `list` - View a list of all module instances and the professors teaching them
- `view` - View the ratings of all professors
- `average <professor_id> <module_code>` - View the average rating of a specific professor for a specific module
- `h` or `help` - Display available commands
- `q` or `quit` or `exit` - Exit the application

### After Login
All commands available before login, plus:
- `rate <professor_id> <module_code> <year> <semester> <rating>` - Rate a professor for a specific module instance
- `logout` - Log out from the current session

## Command Details

### `register`
Allows a new user to register with the service by providing a username, email, and password.

```
-> register
Enter username: student1
Enter email: student1@example.com
Enter password: ********
Confirm password: ********
```

### `login <url>`
Log in to the service using existing credentials.

```
-> login http://yourusername.pythonanywhere.com/api/
Enter username: student1
Enter password: ********
```

### `list`
Displays a table of all module instances and the professors teaching them.

```
-> list
```

Example output:
```
Modules List:

│ Code     │ Name                           │ Year │ Semester │ Taught by                                │
---------------------------------------------------------------------------------------------------------
│ CD1      │ Computing for Dummies          │ 2017 │ 1        │ JE1, Professor J. Excellent             │
│          │                                │      │          │ VS1, Professor V. Smart                 │
---------------------------------------------------------------------------------------------------------
│ CD1      │ Computing for Dummies          │ 2018 │ 2        │ JE1, Professor J. Excellent             │
---------------------------------------------------------------------------------------------------------
│ PG1      │ Programming for the Gifted     │ 2017 │ 2        │ TT1, Professor T. Terrible              │
```

### `view`
Displays the overall ratings of all professors.

```
-> view
```

Example output:
```
Professor Ratings:

The rating of Professor J. Excellent (JE1) is ★★★★★
The rating of Professor T. Terrible (TT1) is ★
The rating of Professor V. Smart (VS1) is ★★
```

### `average <professor_id> <module_code>`
Shows the average rating of a specific professor for a specific module.

```
-> average VS1 CD1
```

Example output:
```
The rating of Professor V. Smart (VS1) in module Computing for Dummies (CD1) is:
★★★
```

### `rate <professor_id> <module_code> <year> <semester> <rating>`
Rate a professor for a specific module instance. Ratings must be between 1 and 5.

```
-> rate JE1 CD1 2018 2 5
```

Example output:
```
--------------------------------------------------------------------
                       RATING SUBMITTED                           
--------------------------------------------------------------------
  Professor: J. Excellent                                          
  Module:    Computing for Dummies                                
  Year:      2018                                                 
  Semester:  2                                                    
  Rating:    ★★★★★                                               
--------------------------------------------------------------------
```

### `logout`
Logs the current user out of the service.

```
-> logout
```

### `q` or `quit` or `exit`
Exits the client application.

```
-> quit
Goodbye!
```

## Notes
- Users must register and login before they can submit ratings.
- Users can only rate a professor for a module instance once.
- Ratings must be integer values between 1 and 5.
- The service calculates the overall ratings of professors automatically.

## Troubleshooting
- If you receive a connection error, check that the service URL is correct and that the server is running.
- If you receive an authentication error, check your username and password.
- If a POST request fails, ensure the URL ends with a slash (/).
- For detailed error messages, check the output from the server response.
