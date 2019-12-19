import logging
from saltToTaste.extensions import db
from saltToTaste.models import Recipe, Tag, Ingredient, Direction, Note

def get_recipes():
    recipes = Recipe.query.all()
    return [recipe.api_model() for recipe in recipes]

def get_recipe(recipe_id):
    recipe = Recipe.query.get(recipe_id)
    try:
        return recipe.api_model()
    except:
        return False

def get_recipe_by_title_f(title_formatted):
    recipe = Recipe.query.filter(Recipe.title_formatted == title_formatted).first()
    try:
        return recipe.api_model()
    except:
        return False

def add_recipe(recipe_data):
    if not Recipe.query.filter(Recipe.filename == recipe_data['filename']).first():
        logging.info(f'Inserting {recipe_data["filename"]} into database')
        recipe = Recipe(layout=recipe_data['layout'], title=recipe_data['title'], title_formatted=recipe_data['title'].lower().replace(' ', '_'))
        if recipe_data['image']:
            recipe.image_path = recipe_data['image']
        if recipe_data['imagecredit']:
            recipe.image_credit = recipe_data['imagecredit']
        if recipe_data['source']:
            recipe.source = recipe_data['source']
        if recipe_data['description']:
            recipe.description = recipe_data['description']
        if recipe_data['prep']:
            recipe.prep = recipe_data['prep']
        if recipe_data['cook']:
            recipe.cook = recipe_data['cook']
        if recipe_data['ready']:
            recipe.ready = recipe_data['ready']
        if recipe_data['servings']:
            recipe.servings = recipe_data['servings']
        if recipe_data['calories']:
            recipe.calories = recipe_data['calories']
        if recipe_data['last_modified']:
            recipe.file_last_modified = recipe_data['last_modified']
        if recipe_data['filename']:
            recipe.filename = recipe_data['filename']
        db.session.add(recipe)

        for t in recipe_data['tags']:
            if not Tag.query.filter(Tag.name == t).first():
                tag = Tag(name=t)
                db.session.add(tag)
            # Create Recipe-Tag mapping (creates entry in recipe_tag_assoc)
            tag = Tag.query.filter(Tag.name == t).first()
            recipe.tags.append(tag)

        for i in recipe_data['ingredients']:
            if not Ingredient.query.filter(Ingredient.name == i).first():
                ingredient = Ingredient(name=i)
                db.session.add(ingredient)
            ingredient = Ingredient.query.filter(Ingredient.name == i).first()
            recipe.ingredients.append(ingredient)

        for d in recipe_data['directions']:
            if not Direction.query.filter(Direction.name == d).first():
                direction = Direction(name=d)
                db.session.add(direction)
            direction = Direction.query.filter(Direction.name == d).first()
            recipe.directions.append(direction)

        for n in recipe_data['notes']:
            if not Note.query.filter(Note.name == n).first():
                note = Note(name=n)
                db.session.add(note)
            note = Note.query.filter(Note.name == n).first()
            recipe.notes.append(note)

        db.session.commit()

def delete_recipe(id):
    recipe = Recipe.query.filter(Recipe.id == id).first()
    if recipe:
        logging.info(f'Removing {recipe.title} from database')

        recipe.tags.clear()
        recipe.ingredients.clear()
        recipe.directions.clear()
        recipe.notes.clear()

        Recipe.query.filter(Recipe.id == id).delete()
        db.session.commit()
        return True

    return False

def delete_recipe_by_filename(filename):
    recipe = Recipe.query.filter(Recipe.filename == filename).first()
    delete_recipe(recipe.id)

def update_recipe(recipe_data): # this only gets used if the title has not been changed which means the filename doesnt change
    logging.info(f'Updating {recipe_data["title"]}')
    recipe_query = Recipe.query.filter(Recipe.filename == recipe_data['filename']).first()

    recipe_query.layout = recipe_data['layout']
    recipe_query.source = recipe_data['source'] or None
    recipe_query.prep = recipe_data['prep'] or None
    recipe_query.cook = recipe_data['cook'] or None
    recipe_query.ready = recipe_data['ready'] or None
    recipe_query.servings = recipe_data['servings'] or None
    recipe_query.calories = recipe_data['calories'] or None
    recipe_query.description = recipe_data['description'] or None
    recipe_query.last_modified = recipe_data['last_modified']
    recipe_query.tags.clear()
    recipe_query.ingredients.clear()
    recipe_query.directions.clear()
    recipe_query.notes.clear()

    for t in recipe_data['tags']:
        if not Tag.query.filter(Tag.name == t).first():
            tag = Tag(name=t)
            db.session.add(tag)
        tag = Tag.query.filter(Tag.name == t).first()
        recipe_query.tags.append(tag)

    for i in recipe_data['ingredients']:
        if not Ingredient.query.filter(Ingredient.name == i).first():
            ingredient = Ingredient(name=i)
            db.session.add(ingredient)
        ingredient = Ingredient.query.filter(Ingredient.name == i).first()
        recipe_query.ingredients.append(ingredient)

    for d in recipe_data['directions']:
        if not Direction.query.filter(Direction.name == d).first():
            direction = Direction(name=d)
            db.session.add(direction)
        direction = Direction.query.filter(Direction.name == d).first()
        recipe_query.directions.append(direction)

    for n in recipe_data['notes']:
        if not Note.query.filter(Note.name == n).first():
            note = Note(name=n)
            db.session.add(note)
        note = Note.query.filter(Note.name == n).first()
        recipe_query.notes.append(note)

    db.session.commit()

def update_recipes(recipe_list):
    logging.info('Checking for altered recipes')
    for recipe in recipe_list:
        recipe_query = Recipe.query.filter(Recipe.filename == recipe['filename']).first()
        if recipe_query.file_last_modified != recipe['last_modified']:
            update_recipe(recipe)

def add_all_recipes(recipe_list):
    logging.info('Initial insert of recipes')
    for recipe in recipe_list:
        add_recipe(recipe)

def add_new_recipes(recipe_list):
    logging.info('Checking for new recipes')
    db_recipes = [x.filename for x in Recipe.query.all()]
    for recipe in recipe_list:
        if recipe['filename'] not in db_recipes:
            add_recipe(recipe)

def remove_missing_recipes(recipe_list):
    logging.info('Checking for missing recipes to remove')
    db_recipes = [x.filename for x in Recipe.query.all()]
    recipe_files = [x['filename'] for x in recipe_list]
    for filename in db_recipes:
        if filename not in recipe_files:
            delete_recipe_by_filename(filename)

def db_cleanup():
    logging.info(f'Cleaning up database')
    tags = Tag.query.all()
    ingredients = Ingredient.query.all()
    directions = Direction.query.all()
    notes = Note.query.all()

    if tags:
        for t in tags:
            if not t.recipe:
                Tag.query.filter(Tag.id == t.id).delete()
    if ingredients:
        for i in ingredients:
            if not i.recipe:
                Ingredient.query.filter(Ingredient.id == i.id).delete()
    if directions:
        for d in directions:
            if not d.recipe:
                Direction.query.filter(Direction.id == d.id).delete()
    if notes:
        for n in notes:
            if not n.recipe:
                Note.query.filter(Note.id == n.id).delete()
    db.session.commit()
