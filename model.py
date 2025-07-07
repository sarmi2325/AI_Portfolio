from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=0)


