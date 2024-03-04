# Number Ninja
Number Ninja is an arithmetic operator game

View the live site [here](https://number-ninja-3ab6f688eeb0.herokuapp.com/).

![screenshot of the live site](assets/readme-images/live-site-screenshot.png)

## Project Goals

### User Goals
- Allow user to sigup and login
- User should be able to login from diffrent machines.
- Play arithmatic opertors gmae with add, subtract, multiply and divion are supported
- Levels easy, medium and hard are supported
- User should be able to see the score.

### Site Owner Goals
- Simple arithmatic command line application
- Provide 10 arithmatic games for user selected level and operator
- Save the highest scrore for each level in the data storage

## User Experience

### Target Audience
- People who wants to imrove the arithmatic operator
- People who want to create profile and play arithmatic operators from different machines
- People who want to track the progress

### User Requirements and Expectations
- Easy to use and easy to understand
- Should be able to see score for every level and arithmatic operators
- Authorization is required to start the game and see the score.

### User Stories
As I user I want to:
1. Select every option for the application using single character
2. Sign up to the application
3. Login using the username and password provided during the signup
4. Select the levels - easy, medium or hard
5. Select the arithmatic operator - add, subtract, multiply or division
6. See result after each opertor game
7. See overall scrore for every level
8. Want to go to back layer above from every layer

### Program Flowchart

![Flowchart](assets/readme-images/number-ninja_flowchart.png)

### Data Storage
The data for the application including user name, password and scrore for every level are stored in a google sheet. You can view the sheet [here](https://docs.google.com/spreadsheets/d/1NEJbjlGX71COJ888ChN1LYDYgf0Q3zYNLa0SJBLC1AY/edit?usp=sharing)

### Features
#### Welcome Message
<TODO>

#### Main Menu
- The user is able to select the options Login or SignUp
- Select 1 for Login and 2 for Signup
![Main menu](assets/readme-images/main_menu.png)

#### Login Menu
- User is prompted to enter user name and password to autheticate
- Password entered is shown as '*'
- Username or password does not match the value in the data storage, error message will be shown to the user
- If username or password does not mach the value in the data storage, user will be prompted to again three times
![Main menu](assets/readme-images/login_menu.png)

#### Sign up menu
- User is prompted to enter username and password to create new profile
- If user name already exists, error message will be shown
- If user name or password does not meet the criteria, error message will be shown
![Signup menu](assets/readme-images/signup_menu.png)

#### User options menu
- The user options is displayed when user login succesfully.
- This presets user with options for:
    - Number game, which allows user to start the game
    - Shows score, which allows user to show score for all operators and levels
    - Quit, which allows user to quit user option menu and back to main menu
![UserOptions menu](assets/readme-images/user_option_menu.png)

#### Number Game
##### Level Menu
- The Level menu is disaplayed when user selects number game options from user options menu
- This presets user with options for:
    - Level Easy, where number ranges from 0 to 9
    - Level Medium, where number ranges from 0 to 99
    - Level Hard, where mumber ranges from 0 to 9999
    - Quit, where user can exit from level menu to user options menu
![Level menu](assets/readme-images/game_level_menu.png)

##### Arithmatic Operator Menu
- The arithmatic operator menu is disaplayed once user selected the level for the game as either easy or medium or hard
- This presets user with options for:
    - Addition, where user will be preseted with two numbers to add
    - Subtration, where user will be preseted with two numbers to subtract 
    - Multiplication, where user will be preseted with two numbers to multiply
    - Division, where user will be preseted with two numbers to divide
    - Quit, where user can exit to user options menu
![Arithmatic Operator menu](assets/readme-images/game_arithmatic_operator_menu.png)

##### Game start Menu
- Game start menu is disaplyed once user selected operator as wither addition, subtraction, multiplcation or division
- This will prset user questions with random number for the range selected by the user.
- Once user entered the answer, correcteness of the anwer will be displayed.
- User will be preseted with 10 questions
- Overall score of the game will be displayed after anwering all 10 questions.
![Game start menu](assets/readme-images/game_start_menu.png)

#### Show Score Menu
- This menu will be preseted when user selects show score option from user options menu
- This presets user highest score for every level and every operator in a tabular form
![Show Score menu](assets/readme-images/show_score_menu.png)

#### Feedback for invalid user name for sign up
- If user name entered is not valid, user will be preseted with invalid username menu
![Invalid Username menu](assets/readme-images/invalid_username_menu.png)

#### Feedback for invalid password for sign up
- If password entered is not valid, user will be preseted with invalid password menu
![Invalid Password menu](assets/readme-images/invalid_password_menu.png)

#### Feedback for invalid credentials for login
- If username or password does not match, user will be

### Technologies Used
- [draw.IO](https://app.diagrams.net/)
- HTML provided in the Code Institute template
- CSS provided in the Code Institute template
- JavaScript provided in the Code Institute template
- [Google Sheets](https://www.google.co.uk/sheets/about/) Used to host application data
- [Github](https://github.com/) Used to host the repository
- [Heroku](https://id.heroku.com/login) Used to deploy the project

### Python libraries used
- [GSpread](https://pypi.org/project/gspread/) Used to manipulate data in google sheets.
- [Tabulate](https://pypi.org/project/tabulate/) Used to present data in a table format.
- [pwinput](https://pypi.org/project/pwinput/) Used to show password input as *

### Testing
#### Python PEP8 Validation
Passed the code through a PEP8 linter and confirmed there are now no issues at the time of this test

