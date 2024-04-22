from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db
from datetime import datetime, timedelta 
from sqlalchemy import DateTime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username =  db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    last_play_time = db.Column(db.DateTime, nullable=True)

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def set_last_play_time(self):
        self.last_play_time = datetime.now()

    def can_play_game(self):
        if not self.last_play_time:
            return True  # if the user hasn't played before
        time_since_last_play = datetime.now() - self.last_play_time
        return time_since_last_play >= timedelta(hours=24)

    def get_json(self):
        return{
            'id': self.id,
            'username': self.username
        }

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

class CurrentGame(db.Model):
    __tablename__ = "current_game"
    id = db.Column(db.Integer, primary_key = True)
    userID = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    secretNumber = db.Column(db.String(120), nullable=False)
    #attempts_left = db.Column(db.Integer, nullable=True)
    is_Won = db.Column(db.Boolean)
    guesses = db.relationship('UserGuesses', backref='game', lazy=True)
    created_at = db.Column(DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, userID, secretNumber, is_Won = False):
        self.userID = userID
        self.secretNumber = secretNumber
        #self.attempts_left = attempts_left
        self.is_Won = is_Won

    def is_game_over(self, guess):
        if (guess == self.secretNumber):
            return True
        return False

    def check_guess (self,guess):
        cows = 0
        bulls = 0
        for i in range(4):
            if self.secretNumber[i] == guess[i]:
                bulls += 1
            elif guess[i] in self.secretNumber:
                cows += 1
        return bulls, cows

class UserGuesses(db.Model):
    guessID = db.Column(db.Integer,primary_key = True)
    userID = db.Column(db.Integer, db.ForeignKey('user.id'))
    gameID = db.Column(db.Integer, db.ForeignKey('current_game.id'))
    guess = db.Column(db.String(4), nullable=False)
    bullsCount = db.Column(db.Integer, nullable=True)
    cowsCount = db.Column(db.Integer, nullable=True)

    def __init__(self, userID, gameID, guess):
        self.userID = userID
        self.gameID = gameID
        self.guess = guess
        game = CurrentGame.query.get(gameID)
        bulls,cows = game.check_guess (guess)
        self.bullsCount = bulls
        self.cowsCount = cows


