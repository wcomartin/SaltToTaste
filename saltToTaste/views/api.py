import os
import argparse
from flask import Blueprint, jsonify, request, abort
from datetime import datetime
from functools import wraps
from . import api_key
from saltToTaste.models import Recipe
from saltToTaste.database_handler import get_recipes, get_recipe, delete_recipe, add_recipe, update_recipe
from saltToTaste.search_handler import search_parser
from saltToTaste.recipe_handler import delete_recipe_file, delete_recipe_image, add_recipe_file, download_image

api = Blueprint('api', __name__)

# Create decorator to require API key
def require_apikey(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if request.headers.get('X-Salt-to-Taste-API-Key') and request.headers.get('X-Salt-to-Taste-API-Key') == api_key:
            return view_function(*args, **kwargs)
        else:
            abort(401)
    return decorated_function

@api.route('/recipe', methods=['GET'])
@require_apikey
def get_recipes_json():
    return jsonify({'recipes' : get_recipes()})

@api.route('/recipe/<int:recipe_id>', methods=['GET'])
@require_apikey
def get_recipe_json(recipe_id):
    recipe = get_recipe(recipe_id)
    if recipe is False:
        return jsonify({'error' : 'ID not found'})
    else:
        return jsonify({'recipe' : recipe})

@api.route('/search', methods=['GET'])
@require_apikey
def search_parser_json():
    search_data = request.args.get('data')
    return jsonify({'recipe' : search_parser(search_data)})

@api.route('/add', methods=['POST'])
@require_apikey
def add_recipe_json():
    data = request.get_json()
    title = data.get('title')
    title_formatted = title.replace(" ", "_").lower()

    recipe = {
        'layout' : data.get('layout') or 'recipe',
        'title' : data.get('title'),
        'formatted_title' : title_formatted,
        'image' : f'{title_formatted}.jpg',
        'imagecredit' : data.get('image_credit'), # this is the link to image to download
        'tags' : data.get('tags'),
        'source' : data.get('source'),
        'prep' : data.get('prep'),
        'cook' : data.get('cook'),
        'ready' : data.get('ready'),
        'servings' : data.get('servings'),
        'calories' : data.get('calories'),
        'description' : data.get('description'),
        'ingredients' : data.get('ingredients'),
        'directions' : data.get('directions'),
        'notes' : data.get('notes'),
        'filename' : f'{title_formatted}.txt'
    }

    if not recipe['title']:
        return jsonify({'error' : 'title missing'})

    download_image(recipe['imagecredit'], title_formatted)
    add_recipe_file(recipe)
    recipe['last_modified'] = datetime.fromtimestamp(os.stat(f'./_recipes/{recipe["filename"]}').st_mtime)
    add_recipe(recipe)
    return jsonify({'success' : 'Recipe added'})

@api.route('/update/<int:recipe_id>', methods=['PUT'])
@require_apikey
def update_recipes_json(recipe_id):
    data = request.get_json()
    recipe_query = Recipe.query.filter(Recipe.id == recipe_id).first()

    if not recipe_query:
        return jsonify({'error' : 'recipe not found'})

    title = data.get('title') or recipe_query.title
    title_formatted = title.replace(" ", "_").lower()

    recipe = {
        'layout' : data.get('layout') or recipe_query.layout,
        'title' : title,
        'formatted_title' : title_formatted,
        'image' : f'{title_formatted}.jpg',
        'imagecredit' : data.get('image_credit') or recipe_query.image_credit, # this is the link to image to download
        'tags' : [],
        'source' : data.get('source') or recipe_query.source,
        'prep' : data.get('prep') or recipe_query.prep,
        'cook' : data.get('cook') or recipe_query.cook,
        'ready' : data.get('ready') or recipe_query.ready,
        'servings' : data.get('servings') or recipe_query.servings,
        'calories' : data.get('calories') or recipe_query.calories,
        'description' : data.get('description') or recipe_query.description,
        'ingredients' : [],
        'directions' : [],
        'notes' : [],
        'filename' : f'{title_formatted}.txt'
    }

    if data.get('tags'):
        recipe['tags'] = data.get('tags')
    else:
        for tag in recipe_query.tags:
            recipe['tags'].append(tag.name)
    if data.get('ingredients'):
        recipe['ingredients'] = data.get('ingredients')
    else:
        for ingredient in recipe_query.ingredients:
            recipe['ingredients'].append(ingredient.name)
    if data.get('directions'):
        recipe['directions'] = data.get('directions')
    else:
        for direction in recipe_query.directions:
            recipe['directions'].append(direction.name)
    if data.get('notes'):
        recipe['notes'] = data.get('notes')
    else:
        for note in recipe_query.notes:
            recipe['notes'].append(note.name)

    if recipe_query.title != recipe['title']:
        print (f' * Recipe title was changed so the recipe is being replaced.')
        delete_recipe_file(recipe.filename)
        delete_recipe_image(recipe.image_path)
        delete_recipe(recipe_query.id)
        download_image(recipe['imagecredit'], title_formatted)
        add_recipe_file(recipe)
        recipe['last_modified'] = datetime.fromtimestamp(os.stat(f'./_recipes/{recipe["filename"]}').st_mtime)
        add_recipe(recipe)

        return jsonify({'success' : 'recipe updated', 'note' : 'recipe ID was changed'})

    add_recipe_file(recipe)
    recipe['last_modified'] = datetime.fromtimestamp(os.stat(f'./_recipes/{recipe["filename"]}').st_mtime)
    update_recipe(recipe)

    return jsonify({'success' : 'recipe updated'})

@api.route('/delete/<int:recipe_id>', methods=['DELETE'])
@require_apikey
def delete_recipe_json(recipe_id):
    recipe = Recipe.query.filter(Recipe.id == recipe_id).first()
    file = os.path.exists(f'./_recipes/{recipe.filename}')
    if recipe and file:
        delete_recipe_file(recipe.filename)
        delete_recipe_image(recipe.image_path)
        delete_recipe(recipe_id)
        return jsonify({'success' : 'Recipe deleted'})
    return jsonify({'error' : 'ID not found'})
