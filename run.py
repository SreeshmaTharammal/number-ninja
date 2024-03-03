import os
import gspread
from google.oauth2.service_account import Credentials
import re
from pwinput import pwinput
import random
from tabulate import tabulate

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


class ArithmaticOperator(NumberGenerator):
    """ Arithmatic operator class """
    def __init__(self, level, operation):
        super().__init__(level)
        self.operation = operation

    def __get_user_response(self, num1, num2, count):
        """ Return user response for the operation """ 
        print(f"\n*********Question {count}*********\n")
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

            if self.operator == "/":
               while num2 == 0:
                   num2 = super().get_number()

            user_response = self.__get_user_response(num1, num2, i+1)
            result = self.__is_answer_correct(num1, num2, user_response)
            if result == True:
                score += 1
                print("\n***********Correct***********\n")
            else:
                print("\n***********Wrong***********\n")
        return score 


class UserManager:
    """ """
    def __init__(self):
        self.__user_details = UserDetails()
        self.__current_username = ''

    def login(self):
        """ 
        Authorize the user by prompting the credentials. 
        If username or password is wrong user will be prompted
        maximum 3 times for the credentials. 
        """
        incorrect_credentials = "Username or password is incorrect."
        
        for i in range(3):
            username = input("Enter username: ")
            password = pwinput("Enter password: ")
            if self.__user_details.is_valid_credential(username, password):
                self.__current_username = username
                return True
            print(incorrect_credentials)
        print("Login attempt failed!\n\n")
        return False

    def signup(self):
        """ Sign-up option for new user. """        
        username = input("Enter username: ")
        if not self.__is_valid_username(username):
            self.__show_username_constrains()
            return
        
        if self.__user_details.is_username_exist(username):
            print("Username already exists. Please choose a different username.")
            return
        else:            
            password = pwinput("Enter password: ")
            if not self.__is_valid_password(password):
                self.__show_password_constrains()
                return
            print("User successfully registered.")

    def get_score(self, level, operator):
        """ """
        return self.__user_details.get_score(self.__current_username, level, operator)

    def update_score(self, level, operator, score):
        """ """
        self.__user_details.update_score(self.__current_username, level, operator, score)

    def __is_valid_username(self, username):
        """ Do password validation """
        username_constrains = r"^[a-zA-Z][a-zA-Z0-9_]{3,11}$"
        if not re.fullmatch(username_constrains, username):
            return False
        return True

    def __show_username_constrains(self):
        """ Show username constrains message """
        username_constrains_msg = "Invalid username, username must:\n"\
                "- At least 4 letters and maximum 12.\n"\
                "- Starts with an alphabet.\n"\
                "- Contain alphabets, numbers or underscores.\n"\
                "- No spaces."                
        print(f"\n{username_constrains_msg}")

    def __is_valid_password(self, password):
        """ Do password validation """
        password_constrains = r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)"\
                r"(?=.*[!%&*])[A-Za-z\d!%&*]{6,12}"
        if not re.fullmatch(password_constrains, password):
            return False
        return True

    def __show_password_constrains(self):
        """ Show password constrains message """
        password_constrains_msg = "Invalid password, password must include:\n"\
                "- At least 6 letters and maximum 12.\n"\
                "- At least 1 lowercase letter.\n"\
                "- At least 1 uppercase letter.\n"\
                "- At least 1 number.\n"\
                "- At least 1 special character (!, %, &, *).\n"\
                "- No spaces."
        print(f"\n{password_constrains_msg}")


class UserDetails:
    """ """
    score_cell_index_dict = {
        "easy_+": 3,
        "medium_+": 4,
        "hard_+": 5,
        "easy_-": 6,
        "medium_-": 7,
        "hard_-": 8,
        "easy_*": 9,
        "medium_*": 10, 
        "hard_*": 11,
        "easy_/": 12,
        "medium_/": 13,
        "hard_/": 14
    } 

    operator_converter_dict = {
        "+": "add",
        "-": "subtract",
        "*": "multiply",
        "/": "division"
    }

    def __init__(self):
        self.__update_user_records()

    def __update_user_records(self):
        """ Update user records and username """
        data = USER_RECORDS_WORKSHEET.get_all_records()
        self.__user_records = {record['username']: record for record in 
                             data}

    def is_username_exist(self, username):
        """ """
        return username in self.__user_records

    def is_valid_credential(self, username, password):
        """ """
        if not self.is_username_exist(username):
            return False
        if self.__user_records[username]['password'] == password:
            return True
        return False

    def add_user(self, username, password):
        """ """
        USER_RECORDS_WORKSHEET.append_row([username, password])
        self.__update_user_records()

    def get_score(self, username, level, operator):
        """ """
        cell_operator_name = UserDetails.operator_converter_dict[operator]
        return self.__user_records[username][f"{level}_{cell_operator_name}"]

    def update_score(self, username, level, operator, score):
        """ """
        if score <= self.get_score(username, level, operator):
            return
        username_cell = USER_RECORDS_WORKSHEET.find(username)
        col_to_update = UserDetails.score_cell_index_dict[f"{level}_{operator}"]
        cell_to_update = USER_RECORDS_WORKSHEET.cell(username_cell.row, col_to_update)
        cell_to_update.value = score
        USER_RECORDS_WORKSHEET.update_cells([cell_to_update])
        self.__update_user_records()


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


def start_game(user_manager):
    """ Start the game by getting the level and operation. """
    level = level_menu()
    if level == "q":
        return

    operation = operation_menu()
    if operation == "q":
        return

    arithmatic_operator = ArithmaticOperator(level, operation)
    score = arithmatic_operator.start()
    user_manager.update_score(level, operator, score)
    print(f"Your current score is {score} and highest score is {user_manager.get_score(level, operator)}")
 

def show_score(user_manager):
    """ """
    score_list = [['Level', 'Add', 'Subtract', 'Multiply', 'Division']]
    for level in ['easy', 'medium', 'hard' ]:
        level_score_list = []
        level_score_list.append(level)
        for operator in ['+', '-', '*', '/']:
            level_score_list.append(user_manager.get_score(level, operator))
        score_list.append(level_score_list)
    print("\n")
    print(tabulate(score_list, headers = "firstrow", tablefmt = "orgtbl"))


def user_options_menu(user_manager):
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
            start_game(user_manager)
        elif user_options_menu_response == "2":
            show_score(user_manager)
        elif user_options_menu_response == "3":
            return
        else:
            print("Invalid action. Please enter 1 or 2 or 3")


def main_menu():
    """ 
    Displays the main menu options for the user to 
    create or login account in order to start the game. 
    """   
    user_manager = UserManager()
    while True:
        print("\n\nPlease select an option below.\n")
        print("1. Login")
        print("2. Sign up")
        print("3. Quit\n")

        main_menu_response = input("Enter your option: ")
        if main_menu_response == "1":
            if user_manager.login():
                user_options_menu(user_manager) 
        elif main_menu_response == "2":
            user_manager.signup()    
        elif main_menu_response == "3":
            return
        else:
            print("Invalid action. Please enter 1 or 2 or 3")


def main():
    """ Runs necessary functions at the start of the program. """
    main_menu() 


main()
