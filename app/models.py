from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates, relationship
from datetime import datetime
import re

db = SQLAlchemy()

# User Model
class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    courses = db.relationship('Course', back_populates='instructor', cascade="all, delete-orphan")
    enrollments = db.relationship('Enrollment', back_populates='student', cascade="all, delete-orphan")
    reviews = db.relationship('Review', back_populates='student', cascade="all, delete-orphan")
    subscriptions_as_student = db.relationship('Subscription', back_populates='student', foreign_keys='Subscription.student_id', cascade="all, delete-orphan")
    subscriptions_as_tutor = db.relationship('Subscription', back_populates='tutor', foreign_keys='Subscription.tutor_id', cascade="all, delete-orphan")

    serialize_rules = ('-courses.instructor', '-enrollments', '-reviews', '-subscriptions_as_student', '-subscriptions_as_tutor')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    @validates('email')
    def validate_email(self, key, email):
        assert '@' in email
        assert re.match(r"[^@]+@[^@]+\.[^@]+", email), "Invalid email format"
        return email

    @validates('role')
    def validate_role(self, key, role):
        if role not in ['student', 'tutor', 'super admin']:
            raise ValueError("Role must be 'student', 'tutor', or 'super admin'.")
        return role

    @validates('password_hash')
    def validate_password(self, key, password_hash):
        assert len(password_hash) > 8
        return password_hash


# Course Model
class Course(db.Model, SerializerMixin):
    __tablename__ = 'courses'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    instructor = db.relationship('User', back_populates='courses')
    category = db.relationship('Category', back_populates='courses')
    enrollments = db.relationship('Enrollment', back_populates='course', cascade="all, delete-orphan")
    reviews = db.relationship('Review', back_populates='course', cascade="all, delete-orphan")
    contents = db.relationship('Content', back_populates='course', cascade="all, delete-orphan")
    quizzes = db.relationship('Quiz', back_populates='course', cascade="all, delete-orphan")

    # Serialization rules
    serialize_rules = ('-instructor.courses', '-category.courses', '-enrollments', '-reviews', '-contents', '-quizzes')

# Category Model
class Category(db.Model, SerializerMixin):
    __tablename__ = 'categories'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    courses = db.relationship('Course', back_populates='category', cascade="all, delete-orphan")

    # Serialization rules
    serialize_rules = ('-courses.category',)

# Enrollment Model
class Enrollment(db.Model, SerializerMixin):
    __tablename__ = 'enrollments'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
    completion_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = db.relationship('User', back_populates='enrollments')
    course = db.relationship('Course', back_populates='enrollments')

    # Serialization rules
    serialize_rules = ('-student.enrollments', '-course.enrollments')

# Review Model
class Review(db.Model, SerializerMixin):
    __tablename__ = 'reviews'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    course = db.relationship('Course', back_populates='reviews')
    student = db.relationship('User', back_populates='reviews')

    # Serialization rules
    serialize_rules = ('-course.reviews', '-student.reviews')

    # Validations
    @validates('rating')
    def validate_rating(self, key, rating):
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return rating

# Content Model
class Content(db.Model, SerializerMixin):
    __tablename__ = 'content'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    content_type = db.Column(db.String, nullable=False)  # Can be 'audio' or 'text'
    file_path = db.Column(db.VARCHAR)
    text_content = db.Column(db.Text)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    course = db.relationship('Course', back_populates='contents')

    # Serialization rules
    serialize_rules = ('-course.contents',)

# Quiz Model
class Quiz(db.Model, SerializerMixin):
    __tablename__ = 'quizzes'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    course = db.relationship('Course', back_populates='quizzes')
    questions = db.relationship('Question', back_populates='quiz', cascade="all, delete-orphan")
    submissions = db.relationship('Submission', back_populates='quiz', cascade="all, delete-orphan")

    # Serialization rules
    serialize_rules = ('-course.quizzes', '-questions.quiz', '-submissions.quiz')

# Question Model
class Question(db.Model, SerializerMixin):
    __tablename__ = 'questions'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    quiz = db.relationship('Quiz', back_populates='questions')
    answers = db.relationship('Answer', back_populates='question', cascade="all, delete-orphan")

    # Serialization rules
    serialize_rules = ('-quiz.questions', '-answers.question')

# Answer Model
class Answer(db.Model, SerializerMixin):
    __tablename__ = 'answers'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    answer_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    question = db.relationship('Question', back_populates='answers')

    # Serialization rules
    serialize_rules = ('-question.answers',)

# Submission Model
class Submission(db.Model, SerializerMixin):
    __tablename__ = 'submissions'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    grade = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    quiz = db.relationship('Quiz', back_populates='submissions')
    student = db.relationship('User', back_populates='submissions')

    # Serialization rules
    serialize_rules = ('-quiz.submissions', '-student.submissions')

# Grade Model
class Grade(db.Model, SerializerMixin):
    __tablename__ = 'grades'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submissions.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    feedback = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    submission = db.relationship('Submission', back_populates='grade')

    # Serialization rules
    serialize_rules = ('-submission.grade',)

# Subscription Model
class Subscription(db.Model, SerializerMixin):
    __tablename__ = 'subscriptions'

    # Columns
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tutor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = db.relationship('User', back_populates='subscriptions_as_student')
    tutor = db.relationship('User', back_populates='subscriptions_as_tutor')

    # Serialization rules
    serialize_rules = ('-student.subscriptions_as_student', '-tutor.subscriptions_as_tutor')
