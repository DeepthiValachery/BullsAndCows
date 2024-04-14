from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify
from App.models import db
from App.controllers import create_user

index_views = Blueprint('index_views', __name__, template_folder='../templates')


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
    return render_template("game_play.html")

@index_views.route("/leaderboard", methods=['GET'])
def leaderboard_page():
    return render_template("leaderboard.html")

def login_user(username, password):
  user = User.query.filter_by(username=username).first()
  if user and user.check_password(password):
    token = create_access_token(identity=user)
    return token
  return None

@index_views.route("/login", methods=['POST'])
def login_action():
  # implement login
  data = request.form
  token = login_user(data['username'], data['password'])
  print(token)
  response = None
  if token:
    flash('Logged in successfully.')  # send message to next page
    response = redirect(
        url_for('game_play'))  # redirect to main page if login successful
    set_access_cookies(response, token)
  else:
    flash('Invalid username or password')  # send message to next page
  return response

# @index_views.route("/login", methods=['POST'])
# def signup_action():
#     #implement user signup