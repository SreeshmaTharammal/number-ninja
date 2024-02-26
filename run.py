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

def signup(users):
    """ Sign-up option for new user"""
    
    while True:
        username = input("Enter a username for signup: ")
        if username in users:
            print("Username already exists. Please choose a different username.")
        else:
            password = input("Enter a password for signup: ")
            USER_RECORDS_WORKSHEET.append_row([username, password])
            print("User successfully registered.")
            break

def main():
    """ Run all program function """
    users = get_all_user_name()    
    print(users)
    signup(users)

main()