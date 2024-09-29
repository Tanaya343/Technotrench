# import string
# password = "Anuj@123"
# upper_case = any([1 if c in string.ascii_uppercase else 0 for c in password])
# lower_case = any([1 if c in string.ascii_lowercase else 0 for c in password])
# special = any([1 if c in string.punctuation else 0 for c in password])
# digits = any([1 if c in string.digits else 0 for c in password])
# characters = [upper_case, lower_case, special, digits]
# length = len(password)
# score = 0
# with open('10k most common.txt','r') as f:
#     common = f.read(). splitlines()

# if password in common:
#     print("Password was found in a common list. Score: 0/7")
#     exit()  
# if length > 8:
#     score += 1
# if length > 12:
#     score += 1
# if length > 17:
#     score += 1
# if length > 20:
#     score += 1   
# print(f"password length is {str(length)}, adding {str(score)} points!") 
# if sum(characters) > 1:
#     score += 1
# if sum(characters) > 2:
#     score += 1
# if sum(characters) > 3:
#     score +=1
# print(f"password has {str(sum(characters))} different character types, adding {str(sum(characters)-1)} points!")
# if score < 4:
#     print(f"The password is quite weak! Score:{str(score)}/7")
# elif score == 4:
#      print(f"The password is ok! Score:{str(score)}/7")
# elif score > 4 and score < 6:
#     print(f"The password is pretty good! Score {str(score)}/7")
# elif score == 6:
#     print(f"The password is great! Score: {str(score)}/7")
# elif score > 6:
#     print(f"The password is strong! Score: {str(score)}/7")

from flask import Flask, render_template, request
import string

app = Flask(__name__)

def calculate_password_strength(password, common_passwords):
    score = 0
    length = len(password)

    # Character type checks
    upper_case = any(c in string.ascii_uppercase for c in password)
    lower_case = any(c in string.ascii_lowercase for c in password)
    special = any(c in string.punctuation for c in password)
    digits = any(c in string.digits for c in password)
    characters = [upper_case, lower_case, special, digits]

    # Check if password is in common passwords list
    if password in common_passwords:
        return 0, "Password was found in a common list.Try an unique password."

    # Length-based score
    if length > 20:
        score += 4
    elif length > 17:
        score += 3
    elif length > 12:
        score += 2
    elif length > 8:
        score += 1

    # Character type-based score
    char_type_count = sum(characters)
    if char_type_count > 3:
        char_type_count = 4  # Maximum score increment based on character types

    score += char_type_count - 1

    # Strength message based on score
    if score < 4:
        strength_message = "The password is quite weak!"
    elif score == 4:
        strength_message = "The password is ok!"
    elif score > 4 and score < 6:
        strength_message = "The password is pretty good!"
    elif score == 6:
        strength_message = "The password is great!"
    else:
        strength_message = "The password is strong!"

    return score, strength_message

@app.route('/', methods=['GET', 'POST'])
def index():
    score = None
    message = None
    if request.method == 'POST':
        password = request.form['password']
        # Load common passwords from file
        try:
            with open('10k most common.txt', 'r') as file:
                common_passwords = set(file.read().splitlines())
        except FileNotFoundError:
            message = "Common passwords file not found."
            return render_template('index.html', message=message)

        # Calculate password strength
        score, message = calculate_password_strength(password, common_passwords)

    return render_template('index.html', score=score, message=message)

if __name__ == '__main__':
    app.run(debug=True)

