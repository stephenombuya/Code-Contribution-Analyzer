from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///code_analyzer.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Import models
from models import User, Repository, Contribution

# Routes
@app.route('/')
def home():
    return jsonify({"message": "Welcome to Code Contribution Analyzer API"})

@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    user_list = [{"id": user.id, "name": user.name, "email": user.email} for user in users]
    return jsonify(user_list)

@app.route('/api/repositories', methods=['GET'])
def get_repositories():
    repos = Repository.query.all()
    repo_list = [{"id": repo.id, "name": repo.name, "url": repo.url, "user_id": repo.user_id} for repo in repos]
    return jsonify(repo_list)

@app.route('/api/contributions', methods=['GET'])
def get_contributions():
    contributions = Contribution.query.all()
    contribution_list = [{
        "id": contrib.id,
        "repository_id": contrib.repository_id,
        "language": contrib.language,
        "lines_of_code": contrib.lines_of_code
    } for contrib in contributions]
    return jsonify(contribution_list)

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.json
    new_user = User(name=data['name'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully!"}), 201

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
