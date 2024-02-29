import os
import gspread
from google.oauth2.service_account import Credentials
import re
from pwinput import pwinput
import random

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

class NumberGenerator:
    """ Random number generator class based on level """
    def __init__(self, level):
        self.level = level

    def get_number(self):
        """ Returns the ramdom number based on level """
        if self.level == 'easy':
            return random.randint(0, 9)           
        elif self.level == 'medium':
            return random.randint(0, 99)            
        elif self.level == 'hard':
            return random.randint(0, 9999)            


class ArithematicOperator(NumberGenerator):
    """ Arithematic operator class """
    def __init__(self, level, operation):              
        super().__init__(level)
        self.operation = operation
        
    def __get_user_response(self, num1, num2):
        """ Return user response for the operation """
        print(f"{num1} {self.operation} {num2} = ?")
        
        while True:
            try:
                return int(input("Enter your answer: "))
            except ValueError:
                print("Enter a valid response\n")

    def __is_answer_correct(self, num1, num2, user_response):
        expression = f"{num1} {self.operation} {num2}" 
        result = eval(expression)
        if int(result) == user_response:
            return True
        return False
    
    def start(self):
        score = 0
        for i in range(10):
            num1 = super().get_number()
            num2 = super().get_number()
            user_response = self.__get_user_response(num1, num2)
            result = self.__is_answer_correct(num1, num2, user_response)
            if result == True:
                score += 1
        print(f"score = {score}") 


    

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
    """ 
    Authorize the user by prompting the credentials. 
    If username or password is wrong user will be prompted
    maximum 3 times for the credentials. 
    """
    incorrect_credentials = "Username or password is incorrect."
    user_names = get_all_user_names(user_records)
    for i in range(3):
        username = input("Enter username: ")
        password = pwinput("Enter password: ")
        if username in user_names:        
            if user_names[username]['password'] == password:
                return True
        print(incorrect_credentials)
    print("Login attempt failed!\n\n")
    return False


def operation_menu():
    """
    Displays the operation menu for the user to select arithmatic
    operators '+', '-' or '*' or '/'
    """
    while True:
        print("\n\nPlease select an option below.\n")
        print("1. Addition")
        print("2. Subtration")
        print("3. Multiplication")
        print("4. Division")
        print("5. Quit\n")

        opertion_menu_response = input("Enter your option: ")
        if opertion_menu_response == "1":
            return '+' 
        elif opertion_menu_response == "2":
            return '-'
        elif opertion_menu_response == "3":
            return '*'
        elif opertion_menu_response == "4":
            return '/'
        elif opertion_menu_response == "5":
            return 'q'
        else:
            print("Invalid action. Please enter 1 or 2 or 3 or 4 or 5")


def level_menu():
    """
    Displays the level menu for the user to select levels
    Easy, Medium or Hard or Quit
    """
    while True:
        print("\n\nPlease select an option below.\n")
        print("1. Easy")
        print("2. Medium")
        print("3. Hard")
        print("4. Quit\n")

        level_menu_response = input("Enter your option: ")
        if level_menu_response == "1":
            return "easy" 
        elif level_menu_response == "2":
            return "medium"  
        elif level_menu_response == "3":
            return "hard"                                
        elif level_menu_response == "4":
            return "q"
        else:
            print("Invalid action. Please enter 1 or 2 or 3 or 4")


def start_game():
    """ Start the game by getting the level and operation. """
    level = level_menu()
    if level == "q":
        return
    
    operation = operation_menu()
    if operation == "q":
        return
   
    arithematic_operator = ArithematicOperator(level, operation)
    arithematic_operator.start()
        

def user_options_menu():
    """ 
    Displays the user option menu which are Game, Show Score 
    and Quit. 
    """
    while True:
        print("\n\nPlease select an option below.\n")
        print("1. Game")
        print("2. Show Score")
        print("3. Quit\n")

        user_options_menu_response = input("Enter your option: ")
        if user_options_menu_response == "1":
            start_game()
        elif user_options_menu_response == "2":
            print("Show score.")                           
        elif user_options_menu_response == "3":
            return
        else:
            print("Invalid action. Please enter 1 or 2 or 3")


def main_menu(users_records):
    """ 
    Displays the main menu options for the user to 
    create or login account in order to start the game. 
    """   
    while True:
        print("\n\nPlease select an option below.\n")
        print("1. Login")
        print("2. Sign up")
        print("3. Quit\n")

        main_menu_response = input("Enter your option: ")
        if main_menu_response == "1":
            if login(users_records):
                user_options_menu() 
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
