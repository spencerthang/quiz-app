from flask import Flask, request, jsonify
from database import initialize, Question, User, Response, Config

from typing import Dict, List

DATABASE_URI = "sqlite:///test.db"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
db = initialize(app)


class APIError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


@app.errorhandler(APIError)
def hanfdle_api_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def get_args(mandatory_args: List[str]) -> Dict[str, str]:
    ret = {}
    for arg in mandatory_args:
        value = request.args.get(arg, "")
        if len(value) == 0:
            raise APIError(f"{arg} is not specified")
        ret[arg] = value
    return ret


@app.route("/")
def hello_world():
    results = db.session.query(Config).filter(Config.key == "initialized").all()
    return f"Results: {len(results)} -- {results[0].key}"


@app.route("/start_quiz", methods=["GET"])
def start_quiz():
    username = request.args.get("username", "")
    if not username:
        raise APIError("Username not specified")

    results = db.session.query(Question).all()
    return jsonify([q.to_dict() for q in results])


@app.route("/submit_response", methods=["GET"])
def submit_response():
    args = get_args(["username", "question_id", "response_text"])

    user = db.session.query(User).filter(User.username == args["username"]).one()
    if not user:
        raise APIError("Username is invalid")

    question = (
        db.session.query(Question).filter(Question.id == args["question_id"]).one()
    )
    if not question:
        raise APIError("Question is invalid")

    response = Response(
        response_text=args["response_text"], user_id=user.id, question_id=question.id
    )
    db.session.add(response)
    db.session.commit()
    return "OK"


@app.route("/admin/responses_by_user", methods=["GET"])
def get_admin_responses_by_user():
    args = get_args(["username"])

    user = db.session.query(User).filter(User.username == args["username"]).one()
    if not user:
        raise APIError("Username is invalid")

    return jsonify([r.to_dict() for r in user.responses])


@app.route("/admin/responses_by_question", methods=["GET"])
def get_admin_responses_by_question():
    args = get_args(["question_id"])

    question = (
        db.session.query(Question).filter(Question.id == args["question_id"]).one()
    )
    if not question:
        raise APIError("Question is invalid")

    return jsonify([r.to_dict() for r in question.responses])
