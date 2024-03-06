import os
import random
import re
import base64
import gspread
from google.oauth2.service_account import Credentials
from pwinput import pwinput
from tabulate import tabulate
from cryptography.fernet import Fernet

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
    def __init__(self, level, operator):
        super().__init__(level)
        self.operator = operator

    def __get_user_response(self, num1, num2, count):
        """ Return user response for the operator """
        print(f"\n*********Question {count}/10*********\n")
        print(f"{num1} {self.operator} {num2} = ?")

        while True:
            try:
                return int(input("Enter your answer: "))
            except ValueError:
                print("Enter a valid response\n")

    def __is_answer_correct(self, num1, num2, user_response):
        expression = f"{num1} {self.operator} {num2}"
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
            if result is True:
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
        incorrect_credentials = "Username or password is incorrect.\n"

        print("\n\nEnter username and password to login")
        for i in range(3):
            username = input("Enter username: ")
            password = pwinput("Enter password: ")
            if self.__user_details.is_valid_credential(username, password):
                self.__current_username = username
                return True
            print(incorrect_credentials)
            if i < 2:
                if not self.__is_login_retry_required():
                    return False
        print("Login attempt failed!\n\n")
        return False

    def signup(self):
        """ Sign-up option for new user. """
        print("\n\nEnter user name and password to sign up")
        self.__show_username_constrains()
        self.__show_password_constrains()

        username = input("\n\nEnter username: ")
        if not self.__is_valid_username(username):
            self.__show_username_constrains()
            return

        if self.__user_details.is_username_exist(username):
            print("Username already exists. Please choose a \
                  different username.")
            return
        else:
            password = pwinput("Enter password: ")
            if not self.__is_valid_password(password):
                self.__show_password_constrains()
                return
            else:
                confirm_password = pwinput("Confirm your password: ")
                if password != confirm_password:
                    print("\nPassword doesn't match!")
                    return
                self.__user_details.add_user(username, password)
                print("User successfully registered.")

    def get_score(self, level, operator):
        """ """
        return self.__user_details.get_score(self.__current_username,
                                             level,
                                             operator)

    def update_score(self, level, operator, score):
        """ """
        self.__user_details.update_score(
            self.__current_username,
            level,
            operator,
            score
        )

    def __is_login_retry_required(self):
        retry_info = """
    Would you like to retry?
    [Y]es or [N]o
    """
        while True:
            print("Would you like to retry? ", end = "")
            retry = input("Enter [Y]es or [N]o: ")
            if retry == 'Y':
                return True
            elif retry == 'N':
                return False
            print("Invalid input. Enter either Y or N\n")

    def __is_valid_username(self, username):
        """ Do password validation """
        username_constrains = r"^[a-zA-Z][a-zA-Z0-9_]{3,11}$"
        if not re.fullmatch(username_constrains, username):
            return False
        return True

    def __show_username_constrains(self):
        """ Show username constrains message """
        print("\nUsername must include:\n"
              "- At least 4 letters and maximum 12.\n"
              "- Starts with an alphabet.\n"
              "- Contains alphabets, numbers or underscores.\n"
              "- No spaces.")

    def __is_valid_password(self, password):
        """ Do password validation """
        password_constrains = r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)"\
                              r"(?=.*[!%&*])[A-Za-z\d!%&*]{6,12}"
        if not re.fullmatch(password_constrains, password):
            return False
        return True

    def __show_password_constrains(self):
        """ Show password constrains message """
        print("\nPassword must include:\n"
              "- At least 6 letters and maximum 12.\n"
              "- At least 1 lowercase letter.\n"
              "- At least 1 uppercase letter.\n"
              "- At least 1 number.\n"
              "- At least 1 special character (!, %, &, *).\n"
              "- No spaces.")

class UserDetails:
    """ """
    score_cell_index_dict = {
        "easy_add": 3,
        "medium_add": 4,
        "hard_add": 5,
        "easy_subtract": 6,
        "medium_subtract": 7,
        "hard_subtract": 8,
        "easy_multiply": 9,
        "medium_multiply": 10,
        "hard_multiply": 11,
        "easy_division": 12,
        "medium_division": 13,
        "hard_division": 14
    }

    operator_converter_dict = {
        "+": "add",
        "-": "subtract",
        "*": "multiply",
        "/": "division"
    }

    def __init__(self):
        self.__update_user_records()
        self.__get_encryption_key()

    def __update_user_records(self):
        """ Update user records and username """
        try:
            data = USER_RECORDS_WORKSHEET.get_all_records()
        except:
            print("Something went wrong. Try again later")
            raise
        self.__user_records = {record['username']: record for record in data}

    def is_username_exist(self, username):
        """ """
        return username in self.__user_records

    def is_valid_credential(self, username, password):
        """ """
        if not self.is_username_exist(username):
            return False

        decoded_password = self.__decrypt_password(
            self.__user_records[username]['password']).decode("utf-8")
        if decoded_password == password:
            return True
        return False

    def add_user(self, username, password):
        """ """
        ciphertext = self.__encrypt_password(password).decode("utf-8")
        try:
            print("saving data...")
            USER_RECORDS_WORKSHEET.append_row([
                username, ciphertext,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
            ])
            self.__update_user_records()
            print("User registered successfully.")
        except:
            print("Unable to register user, try again later")

    def get_score(self, username, level, operator):
        """ """
        return self.__user_records[username][self.level_operator_str(level,
                                                                     operator)]

    def update_score(self, username, level, operator, score):
        """ """
        if score <= self.get_score(username, level, operator):
            return
        try:
            print("Saving score...")
            username_cell = USER_RECORDS_WORKSHEET.find(username)

            col_to_update = UserDetails.score_cell_index_dict[
                self.level_operator_str(level, operator)]
            cell_to_update = USER_RECORDS_WORKSHEET.cell(username_cell.row,
                                                        col_to_update)
            cell_to_update.value = score
            USER_RECORDS_WORKSHEET.update_cells([cell_to_update])
            self.__update_user_records()
            print(f"Your current score is {score} and highest score is "
                f"{self.get_score(level, operator)}")
        except:
            print("Sorry! Failed to update the score.")

    def level_operator_str(self, level, operator):
        return f"{level}_{UserDetails.operator_converter_dict[operator]}"

    def __get_encryption_key(self):
        key_str = os.getenv("Encryption_key")
        if key_str == None:
            f = open("encryption_key.txt", "r")
            print("Reading from file...")
            key_str = f.readline()
        key_str_bytes = key_str.encode("utf-8")
        self.encryption_key = base64.urlsafe_b64encode(key_str_bytes.ljust(32)[:32])

    def __encrypt_password(self, password):
        fernet = Fernet(self.encryption_key)
        return fernet.encrypt(password.encode("utf-8"))
    
    def __decrypt_password(self, ciphertext):
        fernet = Fernet(self.encryption_key)
        return fernet.decrypt(ciphertext)


def operator_menu():
    """
    Displays the operator menu for the user to select arithmatic
    operators '+', '-' or '*' or '/'
    """
    while True:
        print("\n\n*******Arithmatic Operator*******")
        print("Please select an option below.\n")
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
        clear_screen()
        print("\n\n*******Game Level*******")
        print("Please select an option below.\n")
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
            print("Invalid input. Please enter 1 or 2 or 3 or 4")


def start_game(user_manager):
    """ Start the game by getting the level and operator. """
    level = level_menu()
    if level == "q":
        return

    operator = operator_menu()
    if operator == "q":
        return

    print(f"\n\nStarting number game for the level '{level}' for the "
         f"operator '{UserDetails.operator_converter_dict[operator]}'")
    arithmatic_operator = ArithmaticOperator(level, operator)
    score = arithmatic_operator.start()
    user_manager.update_score(level, operator, score)


def show_score(user_manager):
    """ """
    score_list = [['Level', 'Add', 'Subtract', 'Multiply', 'Divide']]
    for level in ['easy', 'medium', 'hard']:
        level_score_list = []
        level_score_list.append(level)
        for operator in ['+', '-', '*', '/']:
            level_score_list.append(user_manager.get_score(level, operator))
        score_list.append(level_score_list)
    print("\n")
    print(tabulate(score_list, headers="firstrow", tablefmt="orgtbl"))


def user_options_menu(user_manager):
    """
    Displays the user option menu which are Game, Show Score
    and Quit.
    """
    while True:
        clear_screen()
        print("\n\n******User Options******")
        print("Please select an option below.\n")
        print("1. Start Number Game")
        print("2. Show Your Score")
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
    clear_screen()
    print("\nWelcome to Number Ninja Arithmatic Operator Game!\n")
    user_manager = UserManager()
    while True:
        print("\n\nPlease select an option below.\n")
        print("1. Login")
        print("2. Sign up")

        main_menu_response = input("Enter your option: ")
        if main_menu_response == "1":
            if user_manager.login():
                user_options_menu(user_manager)
        elif main_menu_response == "2":
            user_manager.signup()
        else:
            print("Invalid action. Please enter 1 or 2 or 3")


def clear_screen():
    """ Clear the screen. """
    os.system("clear")

def main():
    """ Runs necessary functions at the start of the program. """
    main_menu()


main()
