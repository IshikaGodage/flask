import functools
from flask import jsonify, Blueprint, flash, g, redirect, render_template, request, session, url_for
from db import get_db, close_db

bp = Blueprint('recipes', __name__, url_prefix='/recipes')

@bp.route('/', methods=['GET'])
def index():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT id, title, making_time, serves, ingredients, cost FROM recipes ORDER BY created_at ASC')
    recipes = cursor.fetchall()
    cursor.close()
    close_db()

    # Convert posts to a list of dictionaries
    recipes_list = [dict(row) for row in recipes]

    # Check if posts are empty and return 404 if so
    if not recipes_list:
        return jsonify({'error': 'No posts found'}), 200

    # Return the posts as JSON with a 200 status code
    response = {
        "recipe": recipes_list
    }

    return jsonify(response), 200


@bp.route('/<int:id>', methods=['GET'])
def get(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT id, title, making_time, serves, ingredients, cost FROM recipes WHERE id = %s', [id])
    recipe = cursor.fetchone()
    cursor.close()
    close_db()

    # Check if the recipe is empty and return 404 if so
    if recipe is None:
        return jsonify({'error': 'No recipe found'}), 200

    recipe_dict = dict(recipe)

    # Return the recipe as JSON with a 200 status code
    response = {
        "message": "Recipe details by id",
        "recipe": [recipe_dict]
    }

    return jsonify(response), 200


@bp.route('/', methods=['POST'])
def create():
    # Extract data from JSON request body
    data = request.get_json()
    title = data.get('title')
    making_time = data.get('making_time')
    serves = data.get('serves')
    ingredients = data.get('ingredients')
    cost = data.get('cost')

    error = None

    # Validate the input
    if not title:
        error = 'Title is required.'
    if not making_time:
        error = 'Making time is required.'
    if not serves:
        error = 'Serves is required.'
    if not ingredients:
        error = 'Ingredients are required.'
    if not cost:
        error = 'Cost is required.'

    if error is not None:
        response = {
            "message": "Recipe creation failed!",
            "required": "title, making_time, serves, ingredients, cost"
        }
        return jsonify(response), 200

    # Insert data into the database
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        'INSERT INTO recipes (title, making_time, serves, ingredients, cost)'
        ' VALUES (%s, %s, %s, %s, %s)',
        [title, making_time, serves, ingredients, cost]
    )
    db.commit()

    # Fetch the newly created recipe
    recipe_id = cursor.lastrowid
    cursor.execute(
        'SELECT * FROM recipes WHERE id = %s',
        [recipe_id]
    )
    recipe = cursor.fetchone()
    cursor.close()
    close_db()

    # Convert the recipe to a dictionary
    recipe_dict = dict(recipe)

    response = {
        "message": "Recipe successfully created!",
        "recipe": [recipe_dict]
    }

    return jsonify(response), 200


@bp.route('/<int:id>', methods=['PATCH'])
def update_recipe(id=1):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM recipes WHERE id = %s',[id])
    recipe = cursor.fetchone()

    if recipe is None:
        return jsonify({"message": "No recipe found"}), 200

    data = request.get_json()
    title = data.get('title')
    making_time = data.get('making_time')
    serves = data.get('serves')
    ingredients = data.get('ingredients')
    cost = data.get('cost')

    if not data:
        return jsonify({"message": "No data provided for update."}), 200

    # Construct the SET part of the SQL query dynamically based on provided fields
    set_query = []
    values = []

    if title is not None:
        set_query.append('title = %s')
        values.append(title)

    if making_time is not None:
        set_query.append('making_time = %s')
        values.append(making_time)

    if serves is not None:
        set_query.append('serves = %s')
        values.append(serves)

    if ingredients is not None:
        set_query.append('ingredients = %s')
        values.append(ingredients)

    if cost is not None:
        set_query.append('cost = %s')
        values.append(cost)

    # Join the SET part of the query
    set_query = ', '.join(set_query)

    # Execute the SQL query
    cursor.execute(f'UPDATE recipes SET {set_query} WHERE id = %s', [*values, id])
    db.commit()

    # Fetch the newly updated recipe
    cursor.execute('SELECT * FROM recipes WHERE id = %s',[id])
    recipe = cursor.fetchone()

    cursor.close()
    close_db()

    # Convert the recipe to a dictionary
    recipe_dict = dict(recipe)

    response = {
        "message": "Recipe successfully updated!",
        "recipe": [recipe_dict]
    }

    return jsonify(response), 200


@bp.route('/<int:id>', methods=['DELETE'])
def delete(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute('SELECT * FROM recipes WHERE id = %s',[id])
    recipe = cursor.fetchone()

    if recipe is None:
        return jsonify({"message": "No recipe found"}), 200

    cursor.execute('DELETE FROM recipes WHERE id = %s', (id,))
    db.commit()
    cursor.close()
    close_db()

    return jsonify({ "message": "Recipe successfully removed!" }), 200
