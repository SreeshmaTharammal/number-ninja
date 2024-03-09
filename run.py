import os
import random
import re
import base64
import time
import gspread
from google.oauth2.service_account import Credentials
from pwinput import pwinput
from tabulate import tabulate
from cryptography.fernet import Fernet
from colorama import just_fix_windows_console, Fore, Style
import pyfiglet

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
        """ Shows the question to user and returns the user response. """
        color_print(Fore.BLUE, f"\n********* Question {count}/10 *********\n")
        print(f"{num1} {self.operator} {num2} = ?")

        while True:
            try:
                return int(input("Enter your answer: "))
            except ValueError:
                print("Enter a valid response\n")

    def __is_answer_correct(self, num1, num2, user_response):
        """
        Evalutes the arithmatic operator aginst the user response and returns
        True if correct and False otherwise
        """
        expression = f"{num1} {self.operator} {num2}"
        result = eval(expression)
        if int(result) == user_response:
            return True
        return False

    def start(self):
        """
        This function starts the arithmatic game and shows 10 questions and
        prompts user to enter the answer. User response is validated against
        the correct answer. If answer is correct, score is incremented by 1 and
        message will be shown to user. Otherwise wrong message will be shown
        to user.
        """
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
                color_print(
                    Fore.GREEN,
                    "\n\n************ Correct ************\n"
                    )
            else:
                color_print(
                    Fore.RED,
                    "\n\n************* Wrong *************\n"
                    )
        return score


class UserManager:
    """ User Manager class """
    def __init__(self):
        self.__user_details = UserDetails()
        self.__current_username = ''

    def login(self):
        """
        Authorize the user by prompting the credentials.
        If username or password is wrong user will be prompted
        maximum 3 times for the credentials.
        """
        clear_screen()
        incorrect_credentials = "Username or password is incorrect.\n"

        for i in range(3):
            print("\n\nEnter username and password to login")

            username = input("Enter username: ")
            password = pwinput("Enter password: ")
            if self.__user_details.is_valid_credential(username, password):
                self.__current_username = username
                return True

            show_error_msg_with_timeout(incorrect_credentials)
            if i < 2:
                clear_screen()
                if not self.__is_login_retry_required():
                    break

            clear_screen()

        show_error_msg_with_timeout("Login attempt failed!\n\n")
        return False

    def signup(self):
        """
        This function helps to create user account using username and
        password. Password and username are validated against the policy.
        If user entered user name and passwords satisfies the policy, new
        user is added to the data storage.
        """
        clear_screen()

        print("\n\nEnter user name and password to sign up")
        self.__show_username_policy()
        self.__show_password_policy()

        username = input("\n\nEnter username: ")
        if not self.__is_valid_username(username):
            color_print(Fore.RED, "Invalid username")

            self.__show_username_policy()
            time.sleep(2)
            return

        if self.__user_details.is_username_exist(username):
            show_error_msg_with_timeout("""
Username already exists. Please choose a different username.
""")
            return
        else:
            password = pwinput("Enter password: ")
            if not self.__is_valid_password(password):
                color_print(Fore.RED, "Invalid password")

                self.__show_password_policy()
                time.sleep(2)
                return
            else:
                confirm_password = pwinput("Confirm your password: ")
                if password != confirm_password:
                    show_error_msg_with_timeout("\nPassword doesn't match!")
                    return
                self.__user_details.add_user(username, password)

    def get_score(self, level, operator):
        """
        Invokes user details to return the score of the current log in user.
        """
        return self.__user_details.get_score(
            self.__current_username,
            level,
            operator
        )

    def update_score(self, level, operator, score):
        """
        Invokes user details update scrore using the current log in
        user name.
        """
        self.__user_details.update_score(
            self.__current_username,
            level,
            operator,
            score
        )

    def __is_login_retry_required(self):
        """
        Checks a retry for login is required or not. If user enters 'Y'
        then returns True and if user selected 'N' returns false. For any
        other input, invalid input message will be shown and retry message
        will be shown again.
        """
        while True:
            print("""
Would you like to retry?
Make sure you enter uppercase lettter [Y/N]
""")
            retry = input("Enter [Y/N]:")
            if retry == 'Y':
                return True
            elif retry == 'N':
                return False

            show_error_msg_with_timeout("Invalid input. Enter either Y or N\n")
            clear_screen()

    def __is_valid_username(self, username):
        """ Validates username meets the policy requirments """
        username_constrains = r"^[a-zA-Z][a-zA-Z0-9_]{3,11}$"
        if not re.fullmatch(
            username_constrains,
            username
        ):
            return False
        return True

    def __show_username_policy(self):
        """ Show username policy message """
        username_info = """
    Username must include:
    - At least 4 letters and maximum 12.
    - Starts with an alphabet.
    - Contains alphabets, numbers or underscores.
    - No spaces.
    """
        print(username_info)

    def __is_valid_password(self, password):
        """ Validates password meets the policy requirments """
        password_regex = r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)"\
                         r"(?=.*[!%&*])[A-Za-z\d!%&*]{6,12}"
        if not re.fullmatch(
            password_regex,
            password
        ):
            return False
        return True

    def __show_password_policy(self):
        """ Shows password policy message """
        password_info = """
    Password must include:
    - At least 6 letters and maximum 12.
    - At least 1 lowercase letter.
    - At least 1 uppercase letter.
    - At least 1 number.
    - At least 1 special character (!, %, &, *).
    - No spaces.
    """
        print(password_info)


class UserDetails:
    """ User details class """

    # To get worksheet cell index corresponding to level and operator
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

    # To get operator name from the operator symbol
    operator_converter_dict = {
        "+": "add",
        "-": "subtract",
        "*": "multiply",
        "/": "division"
    }

    def __init__(self):
        """
        Updates local copy of user records. Also reads the encryption key
        which is used for encrypting password.
        """
        self.__update_local_user_records()
        self.__get_encryption_key()

    def __update_local_user_records(self):
        """
        Reads all records from data storage and constructs a dictionary
        where the usernames serve as keys, and the associated records
        are the corresponding values. If read from data storage failied,
        will throw exception.
        """
        try:
            data = USER_RECORDS_WORKSHEET.get_all_records()
        except Exception:
            show_error_msg_with_timeout(
                "Something went wrong. Try again later")
            raise
        self.__user_records = {record['username']: record for record in data}

    def is_username_exist(self, username):
        """ Checks same user name already exists in the data storage. """
        return username in self.__user_records

    def is_valid_credential(self, username, password):
        """
        Validates user name and password against values in the data storage.
        Password read from data storage is decrypted and compared aginst the
        received password. If password or username does not match, returns
        false otherwise returns true.
        """
        if not self.is_username_exist(username):
            return False

        decoded_password = self.__decrypt_password(
            self.__user_records[username]['password']).decode("utf-8")
        if decoded_password == password:
            return True
        return False

    def add_user(self, username, password):
        """
        Add user details to data storage. If save to data storage failied,
        error message will be displayed to user. Password is encrypted before
        writing to data storage. Also, updates local copy of user records
        if user is added registered succesfully.
        """
        ciphertext = self.__encrypt_password(password).decode("utf-8")
        try:
            print("saving data...")
            USER_RECORDS_WORKSHEET.append_row([
                username, ciphertext,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
            ])

            self.__update_local_user_records()

            color_print(Fore.GREEN, "User registered successfully.")
        except Exception:
            show_error_msg_with_timeout(
                "Unable to register user, try again later")

    def get_score(self, username, level, operator):
        """ Returns score of the username from the data storage """
        return self.__user_records[username][self.level_operator_str(level,
                                                                     operator)]

    def update_score(self, username, level, operator, score):
        """
        Updates the score to data storage. If the current score is less than or
        equal to highest scrore in the data storage, then score will not be
        updated to data storage. If update score failied due to some reason,
        error message will be displayed. Also, updates local user records,
        if score updated succesfully.
        """
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

            self.__update_local_user_records()
            print("Score updated successfully")
        except Exception:
            show_error_msg_with_timeout("Sorry! Failed to update the score.")

    def level_operator_str(self, level, operator):
        """ Generates string for user selected level and operator """
        return f"{level}_{UserDetails.operator_converter_dict[operator]}"

    def __get_encryption_key(self):
        """
        Reads the encryption key from heroku environment. If failed to read
        the key, exception will be thrown and application will not start.
        """
        key_str = os.getenv("Encryption_key")
        if key_str is None:
            f = open("encryption_key.txt", "r")
            print("Reading from file...")
            key_str = f.readline()

        key_str_bytes = key_str.encode("utf-8")
        self.encryption_key = base64.urlsafe_b64encode(
            key_str_bytes.ljust(32)[:32]
        )

    def __encrypt_password(self, password):
        """ Encrypt password using the encryption key """
        fernet = Fernet(self.encryption_key)
        return fernet.encrypt(password.encode("utf-8"))

    def __decrypt_password(self, ciphertext):
        """ Decrypt cipher text and returns the password as string """
        fernet = Fernet(self.encryption_key)
        return fernet.decrypt(ciphertext)


def operator_menu():
    """
    Displays the operator menu for the user to select arithmatic
    operators '+', '-' or '*' or '/'. Also shows the option to quit the number
    game and go back to user option menu. This menu clears the screen first
    and if user selected invalid option, shows menu again.
    """
    operator_selection = """

****** Arithmatic Operator ******

Please select an option below:
1. Addition
2. Subtration
3. Multiplication
4. Division
5. Quit
"""
    while True:
        clear_screen()
        print(operator_selection)

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
            show_error_msg_with_timeout(
                "Invalid input. Please enter 1 or 2 or 3 or 4 or 5")


def level_menu():
    """
    Displays the level menu which are Easy, Medium or Hard or Quit.
    Quit option allows user to exit the number game and go back to user
    options menu. if user selected invalid option, shows menu again.
    """
    while True:
        clear_screen()
        game_level_selection = """

******* Game Level *******"

Please select an option below
1. Easy
2. Medium
3. Hard
4. Quit
"""
        print(game_level_selection)

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
            show_error_msg_with_timeout(
                "Invalid input. Please enter 1 or 2 or 3 or 4")


def start_game(user_manager):
    """
    Start the number game. This function first clear the screen.
    Shows user to select the required level and required operator. Once user
    selected level and operator, starts to show the questions for the
    selected level and operator.
    """
    clear_screen()
    level = level_menu()
    if level == "q":
        return

    operator = operator_menu()
    if operator == "q":
        return

    clear_screen()
    print(f"\n\nStarting number game for the level '{level}' for the "
          f"operator '{UserDetails.operator_converter_dict[operator]}'")
    arithmatic_operator = ArithmaticOperator(level, operator)
    score = arithmatic_operator.start()
    user_manager.update_score(level, operator, score)

    color_print(Fore.GREEN,
                f"Your current score is {score} and highest "
                f"score is {user_manager.get_score(level, operator)}")

    wait_user_input()


def show_score(user_manager):
    """
    Show highest score for the logged in user for every level and
    every operator in tablular format. This function clear screen before
    showing the score for the user. Also wait for user to press Enter key
    to exit.
    """
    clear_screen()
    print("Your Score:")
    score_list = [['Level', 'Add', 'Subtract', 'Multiply', 'Divide']]
    for level in ['easy', 'medium', 'hard']:
        level_score_list = []
        level_score_list.append(level)
        for operator in ['+', '-', '*', '/']:
            level_score_list.append(user_manager.get_score(level, operator))
        score_list.append(level_score_list)
    print("\n")
    color_print(Fore.LIGHTCYAN_EX, tabulate(score_list,
                                            headers="firstrow",
                                            tablefmt="orgtbl"))

    wait_user_input()


def user_options_menu(user_manager):
    """
    Displays the user option menu which are start number Game, Show Score
    and Quit. Start number game option can be used to start number game,
    show Your score, displays highest score for the log in user for every level
    and every arithmatic operators.
    """
    user_options = """

****** User Options ******

Please select an option below
1. Start Number Game
2. Show Your Score
3. Quit
"""
    while True:
        clear_screen()
        print(user_options)

        user_options_menu_response = input("Enter your option: ")
        if user_options_menu_response == "1":
            start_game(user_manager)
        elif user_options_menu_response == "2":
            show_score(user_manager)
        elif user_options_menu_response == "3":
            return
        else:
            show_error_msg_with_timeout(
                "Invalid input. Please enter 1 or 2 or 3")


def main_menu():
    """
    Displays the main menu options for the user to
    create or login or shows the instructions for the game.
    This function clear s the screen first before showing the option menu.
    """
    clear_screen()

    ascii_art = pyfiglet.figlet_format("Number Ninja", font="slant")
    color_print(Fore.YELLOW, ascii_art)

    print("\nWelcome to Number Ninja Arithmatic Operator Game!\n")
    user_manager = UserManager()
    main_menu_option = """

Please select an option below
1. Login
2. Sign up
3. Instructions
"""
    while True:
        print(main_menu_option)

        main_menu_response = input("Enter your option: ")
        if main_menu_response == "1":
            if user_manager.login():
                user_options_menu(user_manager)
        elif main_menu_response == "2":
            user_manager.signup()
        elif main_menu_response == "3":
            show_instruction_menu()
        else:
            show_error_msg_with_timeout(
                "Invalid input. Please enter 1 or 2 or 3")
        clear_screen()


def show_instruction_menu():
    """
    Displays the instruction menu in color. Screen is cleared first before
    showing the instructions for the menu
    """
    clear_screen()
    color_print(Fore.LIGHTCYAN_EX, """
************************** Instructions *************************

1. User account is required to start the game. If user account not
   created, use sign up option from main menu to create one.
2. Use Login option from main menu to login to the application.
3. Once login, user will presented with options to start game
   or show score.
4. Start game option can be used to select the game
   and required arithmatic oprator to play the game.
5. Show score option can be used to show the score for the user.
6. User will be presented with 10 games for the selected level
   and operator when select game is selected.
7. For division interger part of quotient is considered as correct answer.
   For example, for the question 9/2, correct answer is 4.
8. For level easy, two random number between 0 and 9 will be used to
   generate question
9. For level medium, two random number between 0 and 99 will be used to
   generate question
10. For level hard, two random number between 0 and 9999 will be used to
    generate question
11. From any level in the game, can use option 'Quit' to go back to
    previous level.
""")
    wait_user_input()


def clear_screen():
    """ Clear the screen. """
    os.system("clear")


def color_print(color, message):
    """
    Shows the print in the required color given as parameter.
    After the print, resets color back to default
    """
    print(color, message)
    print(Style.RESET_ALL)


def show_error_msg_with_timeout(msg):
    """ Shows error message in red color and sleeps for 2 seconds. """
    color_print(Fore.RED, msg)
    time.sleep(2)


def wait_user_input():
    """ Waits for user to press Enter key """
    input("Press Enter to continue...")


def main():
    """ Runs necessary functions at the start of the program. """
    just_fix_windows_console()
    main_menu()


if __name__ == "__main__":
    main()
