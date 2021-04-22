import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page -1 ) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start: end]
    return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  #passes app to cors package. resources takes an object,
  # the key in the object represents any endpoint.
  # The value of this key is another object, which
  # the key "origins" has a value of any. What this line means
  # is that all resources are accessible by all clients from any
  # origin
  CORS(app, resources={r"/api/*": {"origins":"*"}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  # after a request is sent to our backend, we intercept the request here
  # before it reaches our endpoints. We set what type of headers that
  # we are allowing to be sent to our endpoints in the first response.headers
  #line. The response.headers line sets the methods that our app will be
  # using and thus which methods a request can have.
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
      response.headers.add('Access-Control-Allow-Methods', 'GET, DELETE , POST')
      return response
  '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''

  @app.route('/categories')
  def get_categories():
      try:
          cats = Category.query.all()
          categories = {cat.id: cat.type for cat in cats}
      except:
          abort(404)

      return jsonify({
        'success': True,
        'categories': categories,
      })
  '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''
  @app.route('/questions')
  def get_paginated_questions():
    try:
        selection = Question.query.all()
        cats = Category.query.all()
        categories = {cat.id: cat.type for cat in cats}
        current_questions = paginate_questions(request, selection)
    except:
        abort(404)

    return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(selection),
        'current_category': None,
        'categories': categories,
    })

  '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_questions(question_id):
      question = Question.query.filter(
      Question.id == question_id).one_or_none()
      if question == None:
          abort(422)
      question.delete()

      return jsonify({
        'success': True,
        'deleted': question.id,
      })

  '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''

  @app.route('/questions', methods=['POST'])
  def add_question():
      try:
          data = request.get_json()
          new_question = Question(
            question = data['question'],
            answer = data['answer'],
            category = data['category'],
            difficulty = data['difficulty']
          )
          new_question.insert()

      except:
          abort(422)

      return jsonify({
        'success': True,
      })
  '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''
  @app.route('/search', methods=['POST'])
  def search_questions():
      try:
          data = request.get_json()
          search_term = data['searchTerm']
          print('search term here',search_term)
          results = Question.query.filter(Question.question.ilike(
          f'%{search_term}%')).all()
          formatted_results = [result.format() for result in results]

      except:
          abort(404)

      return jsonify({
        'success': True,
        'questions': formatted_results,
        'total_questions': len(formatted_results),
        'current_category': None,
      })

  '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions(category_id):
      category = Category.query.filter(Category.id == category_id).one_or_none()
      if category == None:
          abort(422)
      questions = Question.query.filter(Question.category == category.id)
      formatted_questions = [question.format() for question in questions]

      return jsonify({
        'success': True,
        'questions': formatted_questions,
        'total_questions': len(formatted_questions),
      })

  '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''

  @app.route('/quizzes', methods=['POST'])
  def get_quiz_question():
      category = request.get_json()['quiz_category']
      print('check value here', category['id'])
      previous_questions = request.get_json().get('previous_questions', [])
      valid_category = Category.query.filter(Category.id == category['id']).one_or_none()

      if valid_category == None:
          abort(422)

      if category['id'] == 0:
          questions = Question.query.filter(
          Question.id.notin_(previous_questions)).all()
          question = random.choice(questions)

      else:
          questions = Question.query.filter(
          Question.category == category['id']).filter(
          Question.id.notin_(previous_questions)).all()

          if len(questions) < 1:
              return jsonify({
              'success': True,
              'question': False,
              })
          question = random.choice(questions)

      return jsonify({
        'success': True,
        'question': question.format(),
      })

  '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''
  @app.errorhandler(404)
  def bad_request(error):
      return jsonify({
          "success": False,
          "error": 404,
          "message": "File Not Found"
      }), 404

  @app.errorhandler(422)
  def unable_to_follow(error):
      return jsonify({
        'success': False,
        'error': 422,
        'message': "Unprocessable"
      }), 422

  @app.errorhandler(405)
  def method_not_allowed(error):
      return jsonify({
        'success': False,
        'error': 405,
        'message': 'Method Not Allowed',
      }), 405
  return app
