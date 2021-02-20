import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@Done uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
@Done implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks")
def get_drinks():
    # Get the list of drinks from the database
    drinks_list = Drink.query.all()
    # Form the drinks in the short representation
    drinks = [drink.short() for drink in drinks_list]
    # Return success and the list of drinks
    return jsonify({
        "success": True,
        "drinks": drinks
    }), 200


'''
@Done implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks-detail")
@requires_auth("get:drinks-detail")
def get_drinks_detail(payload):
    # Get the list of drinks from the database
    drinks_list = Drink.query.all()
    # Form the drinks in the long representation
    drinks = [drink.long() for drink in drinks_list]
    # Return success and the list of drinks
    return jsonify({
        "success": True,
        "drinks": drinks
    }), 200


'''
@Done implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def add_drinks(payload):
    # Get the request body
    body = request.get_json()
    drink = Drink()
    drink.recipe = json.dumps(body["recipe"])
    drink.title = body["title"]
    drink.insert()
    return jsonify({
        "success": True,
        "drink": drink.long()
    }), 200


'''
@Done implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<int:id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def update_drinks(payload, id):
    # Get the request body
    body = request.get_json()
    # Get the drink by id
    drink = Drink.query.filter_by(id=id).one_or_none()
    # If no drinks found abort 404 not found
    if not drink:
        abort(404)
    try:   
        drink.recipe = body.get("recipe", drink.recipe)
        drink.title = body.get("title", drink.title)
        if isinstance(drink.recipe, list):
            drink.recipe = json.dumps(drink.recipe)
        drink.update()
    except Exception:
        abort(400)

    return jsonify({
        "success": True,
        "drink": drink.long()
    }), 200


'''
@Done implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<int:id>", methods=["DELETE"])
@requires_auth("patch:drinks")
def delete_drinks(payload, id):
    drink = Drink.query.filter_by(id=id).one_or_none()
    # If no drinks found abort 404 not found
    if not drink:
        abort(404)
    try:
        drink.delete()
    except Exception:
        abort(400)

    return jsonify({
        "success": True,
        "delete": id
    }), 200

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable",
        "error": error
    }), 422

'''
@Done implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@Done implement error handler for 404
    error handler should conform to general task above 
'''

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found",
        "error": error
    }), 404

'''
@Done implement error handler for AuthError
    error handler should conform to general task above 
'''

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed",
        "error": error
    }), 405


@app.errorhandler(401)
def permissions_error(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized action",
        "error": error
    }), 401


@app.errorhandler(400)
def user_error(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "user error",
        "error": error
    }), 400

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": 'internal server error',
        "error": error
    }), 500

if __name__ == "__main__":
    app.debug = True
    app.run()