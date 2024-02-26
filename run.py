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

def get_all_user_name():
    """ Get all user names """
        
    users = USER_RECORDS_WORKSHEET.col_values(1)[1:]
    return users

def main():
    """ Run all program function """
    users = get_all_user_name()    
    print(users)

main()