from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify
from App.models import db, CurrentGame
from App.controllers import create_user, login, get_user
import random
from datetime import date

index_views = Blueprint('index_views', __name__, template_folder='../templates')

#function to generate the secret number
def generate_secret_number():
    # Use the current date to seed the random number generator
    today = date.today()
    random.seed(today.strftime("%Y%m%d"))

    # Generate a list of unique random digits
    secret_digits = random.sample(range(10), 4)
    #return secret_digits
    
    # Convert the list of digits to a string --> only used if its being compared to a string
    secret_number = ''.join(map(str, secret_digits))
    return secret_number

@index_views.route('/', methods=['GET'])
def index_page():
    return render_template('login.html')

@index_views.route('/init', methods=['GET'])
def init():
    db.drop_all()
    db.create_all()
    create_user('bob', 'bobpass')
    return jsonify(message='db initialized!')

# @index_views.route('/health', methods=['GET'])
# def health_check():
#     return jsonify({'status':'healthy'})

# used on login page to redirect to the signup page alone
@index_views.route("/signup", methods=['GET'])
def signup_page():
    return render_template("signup.html")

@index_views.route("/game", methods=['GET'])
def game_page():
    #generate the secret number for the game
    secret_number = generate_secret_number()
    new_game = CurrentGame(userID=1,  secretNumber = secret_number, attempts_left = 12, is_Won = False)
    return render_template("game_play.html")

@index_views.route("/leaderboard", methods=['GET'])
def leaderboard_page():
    return render_template("leaderboard.html")


