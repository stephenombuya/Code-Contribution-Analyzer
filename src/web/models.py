from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    repositories = db.relationship('Repository', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.name}>"


class Repository(db.Model):
    __tablename__ = 'repositories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    url = db.Column(db.String(250), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    contributions = db.relationship('Contribution', backref='repository', lazy=True)

    def __repr__(self):
        return f"<Repository {self.name}>"


class Contribution(db.Model):
    __tablename__ = 'contributions'

    id = db.Column(db.Integer, primary_key=True)
    repository_id = db.Column(db.Integer, db.ForeignKey('repositories.id'), nullable=False)
    language = db.Column(db.String(50), nullable=False)
    lines_of_code = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Contribution {self.language}: {self.lines_of_code} LOC>"
