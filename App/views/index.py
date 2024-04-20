from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify, url_for
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

@index_views.route("/game", methods=['GET', 'POST'])
def game_page():
    user = User.query.filter_by(username='bob').first()
    if request.method == 'GET':
        if user.can_play_game():
            #generate the secret number for the game
            secret_number = generate_secret_number()
            new_game = CurrentGame(userID=1,  secretNumber = secret_number, attempts_left = None, is_Won = False)
            db.session.add(new_game)
            user.set_last_play_time()
            db.session.commit()
            return render_template("game_play.html")
        else:
            time_since_last_play = datetime.now() - user.last_play_time
            hours_left = 24 - (time_since_last_play.total_seconds() / 3600)
            return jsonify (message="You have already played today. Please wait {hours_left:.2f} hours before playing again")
    
    elif request.method == 'POST':
        user_guess = request.form.get ('user_guess')
        current_game = CurrentGame.query.first()
        
        if current_game.is_Won:
            return jsonify(message="Game is already won. You cannot submit more guesses.")
        #current_game.attempts_left -= 1
        
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
        return jsonify(message="Incorrect guess. Keep trying!")

@index_views.route("/leaderboard", methods=['GET'])
def leaderboard_page():
    return render_template("leaderboard.html")


