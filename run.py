import gspread
from google.oauth2.service_account import Credentials
import re

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

def is_valid_password(password):
    """ Do password validation """
    password_constrains = r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)"\
            r"(?=.*[!%&*])[A-Za-z\d!%&*]{6,12}"
    if not re.fullmatch(password_constrains, password):
        return False
    return True

def show_password_constrains():
    password_constrains_msg = "Password must be 6-12 characters long "\
            "and include at least 1 lowercase letter, 1 uppercase letter, "\
                "1 number, and 1 special character (!, %, &, *)."
    print(f"\n{password_constrains_msg}")

def signup(user_records):
    """ Sign-up option for new user """

    username = input("Enter username: ")
    user_names = get_all_user_names(user_records)
    if username in user_names:
        print("Username already exists. Please choose a different username.")
        return False
    else:
        show_password_constrains()
        password = input("Enter password: ")
        if not is_valid_password(password):
            show_password_constrains()
            return False
        USER_RECORDS_WORKSHEET.append_row([username, password])
        print("User successfully registered.")
        return True


def login(user_records):
    """ Authorize the user by prompting the credentials """

    username = input("Enter username: ")
    password = input("Enter password: ")
    user_names = get_all_user_names(user_records)
    if username in user_names:
        print(user_names[username]['password'])
        if user_names[username]['password'] == password:
            return True
    return False


def main():
    """ Run all program function """

    incorrect_credentials = "Username or password is incorrect."
    users_records = get_all_user_records()
    while True:
        action = input("Do you want to 'signup' or 'login' or 'quit'? ")
        if action == 'signup':
            if signup(users_records):
                users_records = get_all_user_records()
        elif action == 'login':
            if login(users_records):
                print("Login successful.")
            else:
                print(incorrect_credentials)
        elif action == 'quit':
            return
        else:
            print("Invalid action. Please enter 'signup' or 'login' or 'quit'")


main()
