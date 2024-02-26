import gspread
from google.oauth2.service_account import Credentials

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

def signup(users):
    """ Sign-up option for new user """
    
    while True:
        username = input("Enter username: ")
        if username in users:
            print("Username already exists. Please choose a different username.")
        else:
            password = input("Enter password: ")
            USER_RECORDS_WORKSHEET.append_row([username, password])
            print("User successfully registered.")
            break

def login(user_records):
    """ Authorize the user by prompting the credentials """
    incorrect_credentials = "Username or password is incorrect."
    username = input("Enter username: ")
    password = input("Enter password: ")
    user_names = get_all_user_names(user_records)
    if username in user_names:    
        print(user_names[username]['password'])          
        if user_names[username]['password'] == password:
            print("Login successful.")            
        else:
            print(incorrect_credentials)
    else:
        print(incorrect_credentials)


def main():
    """ Run all program function """
    users = get_all_user_records()    
    print(users)
    login(users)
    signup(users)

main()