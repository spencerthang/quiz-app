from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(65535), nullable=False)

    def __repr__(self):
        return f"<Question id: {self.id}, question_text: {self.question_text}>"

    def to_dict(self):
        return {"question_text": self.question_text, "question_id": self.id}


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)

    def __repr__(self):
        return f"<User id: {self.id}, question_text: {self.username}>"


class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref=db.backref("responses", lazy=True))

    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)
    question = db.relationship("Question", backref=db.backref("responses", lazy=True))

    response_text = db.Column(db.String(65535), nullable=False)

    def __repr__(self):
        return f"<User id: {self.id}, username: {self.username}>"

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.user.username,
            "question_id": self.question_id,
            "question": self.question.question_text,
            "response_text": self.response_text,
        }


class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(65535), unique=True, nullable=False)
    value = db.Column(db.String(65535), nullable=False)

    def __repr__(self):
        return f"<Config id: {self.id}, key: {self.key}, value: {self.value}>"


def initialize(app: Flask) -> SQLAlchemy:
    db.app = app
    db.init_app(app)
    db.create_all()

    # Check if initialized with default rows
    conf_initialized = (
        db.session.query(Config).filter(Config.key == "initialized").all()
    )
    print(conf_initialized)

    if not conf_initialized:
        print("Initializing database...")
        init_objects = []

        # Add config
        init_objects += [Config(key="initialized", value="true")]

        # Add questions
        questions_str = [
            "What is your favorite color?",
            "What is your favorite city?",
            "What is your favorite food?",
            "What is your favorite phone?",
            "What is your favorite chair?",
        ]
        init_objects += [Question(question_text=q) for q in questions_str]

        # Add users
        init_objects += [
            User(username="spencer"),
            User(username="strive"),
            User(username="strive2"),
        ]

        db.session.add_all(init_objects)

        db.session.commit()

    return db
