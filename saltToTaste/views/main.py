from flask import current_app, Blueprint, render_template, request, send_file, safe_join, abort, session, url_for, redirect, flash, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from saltToTaste.extensions import db
from saltToTaste.models import Recipe, Tag, Direction, Ingredient, Note
from saltToTaste.search_handler import search_parser
from saltToTaste.recipe_handler import ingredient_split
from saltToTaste.database_handler import get_recipes, get_recipe_by_title_f

main = Blueprint('main', __name__)

@main.route("/", methods=['GET', 'POST'])
def index():
    recipes = sorted(get_recipes(), key = lambda i: i['title'])

    if request.method == 'POST':
        search_data = request.form.getlist('taggles[]')
        if search_data:
            results = search_parser(search_data)
            return render_template("index.html", recipes=results)

    return render_template("index.html", recipes=recipes)

@main.route("/recipe/<string:recipe_link>")
def recipe(recipe_link):
    recipe = get_recipe_by_title_f(recipe_link)

    # Split ingredients into two lists
    ingredients_list = ingredient_split(recipe['ingredients'])

    return render_template("recipe.html", recipe=recipe, ingredients_list=ingredients_list)

@main.route("/download/<path:filename>")
# @login_required
def download_recipe(filename):
    filename = filename.lower()
    safe_path = safe_join(current_app.config["RECIPE_FILES"], filename)
    try:
        return send_file(safe_path, as_attachment=True, attachment_filename=filename)
    except FileNotFoundError:
        abort(404)

@main.route("/image/<path:filename>", methods=['GET'])
def image_path(filename):
    return send_from_directory(current_app.config["RECIPE_IMAGES"], filename)
