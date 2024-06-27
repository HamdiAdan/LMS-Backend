from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Import models
from models import User, Course, Category, Enrollment, Review, Content, Quiz, Question, Answer, Submission, Grade, Subscription

# Routes for user registration and login
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')

    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({'message': 'User already exists'}), 409

    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, email=email, password_hash=password_hash, role=role)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity={'id': user.id, 'role': user.role})
    return jsonify(access_token=access_token), 200

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

# routes for courses
@app.route('/courses', methods=['GET'])
def get_courses():
    courses = Course.query.all()
    return jsonify([course.to_dict() for course in courses]), 200

@app.route('/course', methods=['POST'])
@jwt_required()
def create_course():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    instructor_id = data.get('instructor_id')
    category_id = data.get('category_id')
    price = data.get('price')

    new_course = Course(title=title, description=description, instructor_id=instructor_id, category_id=category_id, price=price)
    db.session.add(new_course)
    db.session.commit()

    return jsonify({'message': 'Course created successfully'}), 201

@app.route('/course/<int:id>', methods=['PUT'])
@jwt_required()
def update_course(id):
    data = request.get_json()
    course = Course.query.get_or_404(id)

    course.title = data.get('title', course.title)
    course.description = data.get('description', course.description)
    course.category_id = data.get('category_id', course.category_id)
    course.price = data.get('price', course.price)

    db.session.commit()

    return jsonify({'message': 'Course updated successfully'}), 200

@app.route('/course/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_course(id):
    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    return jsonify({'message': 'Course deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
