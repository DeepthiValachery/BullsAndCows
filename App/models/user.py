from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username =  db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

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
    gameID = db.Column(db.Integer,primary_key = True,nullable=False)
    userID = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    secretNumber = db.Column(db.String(120), nullable=False)
    attempts_left = db.Column(db.Integer, nullable=True)
    is_Won = db.Column(db.Boolean)

    def __init__(self, userID, secretNumber, attempts_left = 12, is_Won = False):
        self.userID = userID
        self.secretNumber = secretNumber
        self.attempts_left = attempts_left
        self.is_Won = is_Won

    def is_game_over(self, guess):
        if (guess == self.secretNumber ):
            return True
        return False

    # def check_guess (self,guess):
    #     cows = 0
    #     bulls = 0
    #     for i in range(4):
    #         if self.secretNumber[i] == guess[i]:
    #             bulls += 1
    #         elif guess[i] in self.secretNumber:
    #             cows += 1
    #     return bulls, cows

class UserGuesses(db.Model):
    guessID = db.Column(db.Integer,primary_key = True,nullable=False)
    userID = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    gameID = db.Column(db.Integer, db.ForeignKey('CurrentGame.gameID'),nullable=False)
    guess = db.Column(db.String(4), nullable=False)
    bullsCount = db.Column(db.Integer, nullable=True)
    cowsCount = db.Column(db.Integer, nullable=True)

    def __init__(self, userID, gameID, guess):
        self.userID = userID
        self.gameID = gameID
        self.guess = guess
        cows = 0
        bulls = 0
        for i in range(4):
            if self.secretNumber[i] == guess[i]:
                bulls += 1
            elif guess[i] in self.secretNumber:
                cows += 1
        self.bullsCount = bulls
        self.cowsCount = cows


