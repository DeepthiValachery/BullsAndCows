from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify, url_for
from flask_jwt_extended import jwt_required
from App.models import db, CurrentGame, User, UserGuesses
from App.controllers import create_user, login, get_user
import random
from datetime import date, datetime

index_views = Blueprint('index_views', __name__, template_folder='../templates')

# Define a global variable to store the last generated number and its date
last_generated = {"date": None, "number": None}

#function to generate the secret number
def generate_secret_number():
    global last_generated
    
    # Get today's date
    today = date.today()
    
    # Check if a number has been generated today
    if last_generated["date"] != today:
        # Generate a new number
        random.seed(today.strftime("%Y%m%d"))
          # Generate a list of unique random digits
        secret_digits = random.sample(range(10), 4)
         # Convert the list of digits to a string --> only used if its being compared to a string
        secret_number = ''.join(map(str, secret_digits))
        
        # Update last_generated with today's date and the new number
        last_generated["date"] = today
        last_generated["number"] = secret_number
    else:
        # Return the previously generated number
        secret_number = last_generated["number"]
    
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

# used on login page to redirect to the signup page alone
@index_views.route("/signup", methods=['GET'])
def signup_page():
    return render_template("signup.html")

@index_views.route("/game", methods=['GET'])
def game_page():
    #generate the daily secret number for the game
    secret_number = generate_secret_number()
    current_user_ID = 1
    #filter game by existing user and secret number
    existing_game = CurrentGame.query.filter_by(userID=1, secretNumber=secret_number).first()

    if existing_game:
        #gets users guesses in the current game
        past_guesses = UserGuesses.query.filter_by(userID = 1, gameID = existing_game.id).all()
        # return the user game currently
        return render_template("game_play.html", existing_game = existing_game,  current_user_ID =  1, user_guesses=past_guesses)
    else:
        # No existing game with the same user ID and secret number, add the new game to the database
        new_game = CurrentGame(userID=1, secretNumber=secret_number, is_Won=False)
        db.session.add(new_game)
        db.session.commit()
        return render_template("game_play.html", new_game = new_game,  current_user_ID= current_user_ID)

@index_views.route("/leaderboard", methods=['GET'])
def leaderboard_page():
    #get all the games asscoiated with the user
    current_user_ID= 1
    past_games = CurrentGame.query.filter_by(userID=current_user_ID).all()
    user = User.query.filter_by(id=current_user_ID).first()
    return render_template("leaderboard.html", past_games=past_games, current_user_ID=current_user_ID, user=user)

#submit guess route
@index_views.route("/submit_guess", methods=['GET', 'POST'])
def submit_guess():
    if request.method == 'POST':
            user_guess = request.form.get('user_guess')
            current_game = CurrentGame.query.first()
            if current_game is None:
                return jsonify(message="No current game found"), 404
                
            if current_game.is_Won:
                return jsonify(message="Game is already won. You cannot submit more guesses.")
                
            if current_game.is_game_over(user_guess):
                current_game.is_Won = True
                user_guesses = UserGuesses(userID=current_game.userID, gameID=current_game.id, guess=user_guess)
                db.session.add(user_guesses)
                db.session.commit()
                return jsonify(message="Congratulations! You guessed the correct number.")
                
            bulls, cows = current_game.check_guess(user_guess)
            user_guesses = UserGuesses(userID=current_game.userID, gameID=current_game.id, guess=user_guess)
            user_guesses.bullsCount = bulls
            user_guesses.cowsCount = cows
            db.session.add(user_guesses)
            db.session.commit()
            return jsonify(message="Incorrect guess. Keep trying!", bulls=bulls, cows=cows)
