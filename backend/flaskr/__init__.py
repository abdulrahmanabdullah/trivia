import os
import random
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import func
import random

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10


# Return randome row at questions table .
def random_question_row(cat_id):
    query = db.session.query(Question).filter(Question.category == cat_id)
    row_count = int(query.count())
    random_query = query.offset(int(row_count*random.random())).first()
    # show me your random list.
    print(f' random {random_query} 🔦🔦')
    return random_query


# Return questions related by page, each page contain 10 questions
def pagination_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in selection]
    current_question = questions[start:end]
    return current_question


def create_app(test_config=None):

    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, DELETE, PUT, PATCH, OPTIONS')
        return response

    # Endpoint for all categories.
    # for make it readable and accessable .
    @app.route('/categories')
    def all_categories():
        categories = Category.query.all()
        fromat_category = {}
        for item in categories:
            fromat_category[item.id] = item.type

        return jsonify(fromat_category)

    @app.route('/questions')
    def all_questions():
        questions = Question.query.all()
        current_question = pagination_questions(request, questions)
        return jsonify({
            "message": "success",
            "total_questions": len(questions),
            "questions": current_question,
            "current_category": None
        })

    # @TODO:
    # Create an endpoint to DELETE question using a question ID.

    # TEST: When you click the trash icon next to a question, the question will be removed.
    # This removal will persist in the database and when you refresh the page.

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_questions(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            # TODO:: Delete question and writing some test .
            question.delete()
            return jsonify({
                "message": "Success",
                "question_id": question.id
            })
        except Exception as exp:
            print(f' Some error ocurred {exp} ❌')
            abort(404)

    # POST NEW QUESTION ENDPOINT
    @app.route('/questions', methods=['POST'])
    def add_questions():
        body = request.get_json()
        # question, category, difficulty, answer and auto add id .
        question_request = body.get('question')
        category_request = body.get('category')
        difficulty_request = body.get('difficulty')
        answer_request = body.get('answer')

        # Check request values if it's NOT valid
        request_values = [question_request, category_request,
                          difficulty_request, answer_request]
        if None in request_values:
            abort(422)
        try:
            category = int(category_request)
            difficulty = int(difficulty_request)
            question = Question(
                question=question_request, category=category, difficulty=difficulty, answer=answer_request)
            question.insert()
            return jsonify({
                "Success": True,
                "message": "Question added"
            })
        except Exception as exp:
            print(f' Some error ocurred {exp} ❌')
            abort(400)

    # SEARCH QUESTIONS ENDPOINT
    @app.route('/questions/search', methods=['POST'])
    def search_quesions():
        body = request.get_json()
        post_question = body.get('searchTerm')

        # query all questions related with post_question
        questions = Question.query.filter(
            Question.question.ilike(f'%{post_question.lower()}%')).all()

        format_questions = [question.format() for question in questions]

        if questions is None:
            abort(404)
        else:
            return jsonify({
                "success": True,
                "questions": format_questions,
                "total_questions": len(questions),
                "current_category": None
            })

    # GET endpoint to get questions based on category.

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_with_category(category_id):
        categories = Category.query.filter(
            Category.id == category_id).one_or_none()
        if categories is None:
            abort(405)
        else:
            question = categories.id
            questions = Question.query.filter(
                Question.category == question).all()
            format_questions = [question.format() for question in questions]
            return jsonify({
                "message": "Success",
                "total_questions": len(questions),
                "questions": format_questions,
                "current_category": category_id
            })

    # POST endpoint to get questions to play the quiz.
    @app.route('/quizzes', methods=['POST'])
    def quizzes():
        body = request.get_json()
        previous_questions = body.get('previous_questions')
        quiz_category = body.get('quiz_category')
        quiz_category_id = int(quiz_category['id'])

        # Randomize category when id == 0
        if quiz_category_id == 0:
            quiz_category_id = random.randint(1, 6)
            print(f' id = 0 and update it to {quiz_category_id} 💡')

        test_randome_question = Question.query.order_by(func.random()).filter(
            Question.category == quiz_category_id).first()
        print(f' Rnadom Q = {test_randome_question} 👍🏻')

        category = Category.query.filter(
            Category.id == quiz_category_id).one_or_none()

        if category is None:
            abort(404)

        questions = Question.query.filter(
            Question.category == quiz_category_id).first()
        # format_question = [question.format() for question in questions]
        q = random_question_row(quiz_category_id)

        return jsonify({
            "message": "success",
            "question": q.format(),
            "quiz_category": category.type,
            "previous_questions": previous_questions
        })

    # Page not found
    @app.errorhandler(404)
    def error_handler(error):
        return jsonify({
            "success": False,
            "message": "404 Not found",
            "error": 404
        }), 404

    # INSERT ERROR HANDLER - Unprocessable entity.
    @app.errorhandler(422)
    def error_handler(error):
        return jsonify({
            "success": False,
            "message": "Unprocessable 422",
            "error": 422
        }), 422
    return app
