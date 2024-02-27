import os
import gspread
from google.oauth2.service_account import Credentials
import re
from pwinput import pwinput

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('number-ninja')

USER_RECORDS_WORKSHEET = SHEET.worksheet("user_records")


def get_all_user_records():
    """ Get all user records """

    users = USER_RECORDS_WORKSHEET.get_all_records()
    return users


def get_all_user_names(user_records):
    """ Get all user name from user records """

    return {record['username']: record for record in user_records}

def is_valid_username(username):
    """ Do password validation """

    username_constrains = r"^[a-zA-Z][a-zA-Z0-9_]{3,11}$"
    if not re.fullmatch(username_constrains, username):
        return False
    return True

def show_username_constrains():
    """ Show username constrains message """

    username_constrains_msg = "Username must be 4 to 12 characters long.\n"\
            "Username must start with an alphabet "\
            "character.\nThe usename can contain alphabets, numbers "\
            "or underscores."
    print(f"\n{username_constrains_msg}")


def is_valid_password(password):
    """ Do password validation """

    password_constrains = r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)"\
            r"(?=.*[!%&*])[A-Za-z\d!%&*]{6,12}"
    if not re.fullmatch(password_constrains, password):
        return False
    return True

def show_password_constrains():
    """ Show password constrains message """

    password_constrains_msg = "Password must be 6-12 characters long\n"\
            "and include at least 1 lowercase letter, 1 uppercase letter,\n"\
                "1 number, and 1 special character (!, %, &, *)."
    print(f"\n{password_constrains_msg}")


def signup(user_records):
    """ Sign-up option for new user. """

    show_username_constrains()
    username = input("Enter username: ")
    if not is_valid_username(username):
        show_username_constrains()
        return
    user_names = get_all_user_names(user_records)
    if username in user_names:
        print("Username already exists. Please choose a different username.")
        return False
    else:
        show_password_constrains()
        password = pwinput("Enter password: ")        
        if not is_valid_password(password):
            show_password_constrains()
            return False
        USER_RECORDS_WORKSHEET.append_row([username, password])
        print("User successfully registered.")
        return True


def login(user_records):
    """ Authorize the user by prompting the credentials. """

    username = input("Enter username: ")
    password = pwinput("Enter password: ")
    user_names = get_all_user_names(user_records)
    if username in user_names:        
        if user_names[username]['password'] == password:
            return True
    return False

def main_menu(users_records):
    """ 
    Displays the main menu options for the user to 
    create or login account in order to start the game. 
    """
        
    print("Please select an option below.\n")
    print("1. Login")
    print("2. Sign up")
    print("3. Quit")

    incorrect_credentials = "Username or password is incorrect."
    while True:
        main_menu_response = input("Enter your option: ")
        if main_menu_response == "1":
            if login(users_records):
                print("Login successful.")                   
            else:
                print(incorrect_credentials)         
        elif main_menu_response == "2":
            if signup(users_records):
                users_records = get_all_user_records()                           
        elif main_menu_response == "3":
            return
        else:
            print("Invalid action. Please enter 1 or 2 or 3")

def main():
    """ Runs necessary functions at the start of the program. """
    
    users_records = get_all_user_records()  
    main_menu(users_records) 


main()
