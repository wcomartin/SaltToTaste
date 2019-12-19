from collections import defaultdict
from saltToTaste.models import db, Recipe, Tag, Ingredient, Note, Direction

def search_parser(search_data):
    # Format search data to allow for AND/OR keywords for Whoosh indexing
    search_items = search_data.lower().replace(' or ', ' OR ' ).replace(' and ', ' AND ').split(',')
    search_dict = defaultdict(list)
    # Organize search terms
    for item in search_items:
        if 'title:' in item:
            search_dict['title'].append(item.replace('title:', ''))
        elif 'tag:' in item:
            search_dict['tag'].append(item.replace('tag:', ''))
        elif 'ingredient:' in item:
            search_dict['ingredient'].append(item.replace('ingredient:', ''))
        elif 'direction:' in item:
            search_dict['direction'].append(item.replace('direction:', ''))
        elif 'calories' in item:
            search_dict['calories'].append(item.replace('calories:', ''))
        elif 'note' in item:
            search_dict['note'].append(item.replace('note:', ''))
        else:
            search_dict['general'].append(item)
    # Process search results
    search_results = defaultdict(list)
    if search_dict['general']:
        for item in search_dict['general']:
            query = Recipe.query.search(item).all()
            for recipe in query:
                if recipe not in search_results['general']:
                    search_results['general'].append(recipe)
    if search_dict['title']:
        for item in search_dict['title']:
            query = Recipe.query.search(item, fields=('title',)).all()
            for recipe in query:
                if recipe not in search_results['title']:
                    search_results['title'].append(recipe)
    if search_dict['tag']:
        for item in search_dict['tag']:
          query = Tag.query.search(item).all()
          for result in query:
              for recipe in result.recipe:
                  if recipe not in search_results['tag']:
                      search_results['tag'].append(recipe)
    if search_dict['ingredient']:
        for item in search_dict['ingredient']:
            query = Ingredient.query.search(item).all()
            for result in query:
                for recipe in result.recipe:
                    if recipe not in search_results['ingredient']:
                        search_results['ingredient'].append(recipe)
    if search_dict['direction']:
        for item in search_dict['direction']:
            query = Direction.query.search(item).all()
            for result in query:
                for recipe in result.recipe:
                    if recipe not in search_results['direction']:
                        search_results['direction'].append(recipe)
    if search_dict['calories']:
        intersection_list = []
        for item in search_dict['calories']:
            result_group = []
            if '<=' in item:
                query = Recipe.query.filter(Recipe.calories <= item.strip('<=')).order_by(Recipe.calories).all()
            elif '<' in item:
                query = Recipe.query.filter(Recipe.calories < item.strip('<')).order_by(Recipe.calories).all()
            elif '>=' in item:
                query = Recipe.query.filter(Recipe.calories >= item.strip('>=')).order_by(Recipe.calories).all()
            elif '>' in item:
                query = Recipe.query.filter(Recipe.calories > item.strip('>')).order_by(Recipe.calories).all()
            else:
                query = Recipe.query.filter(Recipe.calories == item).order_by(Recipe.calories).all()
            for result in query:
                result_group.append(result)
            # Only keep results that show up in every calorie query
            if len(intersection_list) < 1:
                for item in result_group:
                    intersection_list.append(item)
            else:
                set_result = set(intersection_list) & set(result_group)
                intersection_list.clear()
                for result in set_result:
                    intersection_list.append(result)

            search_results['calories'] = intersection_list

        search_results['calories'].sort(key=lambda x: x.calories)
    if search_dict['note']:
        for item in search_dict['note']:
            query = Note.query.search(item).all()
            for result in query:
                for recipe in result.recipe:
                    if recipe not in search_results['note']:
                        search_results['note'].append(recipe)
    # Combine results
    # Create an initial combined_list dict using the first search term results list unless calories is a key (so that results are sorted by calories primarily)
    if search_dict['calories']:
        initial_key = 'calories'
        combined_list = search_results[initial_key]
    else:
        for key in search_dict.keys():
            if search_dict[key]:
                initial_key = key
                combined_list = search_results[initial_key]
                break
    #Process results and only keep items that appear in every list
    for key in search_results:
        if key != initial_key:
            if search_results[key]:
                combined_list = [x for x in combined_list if x in search_results[key]]
    return [recipe.api_model() for recipe in combined_list]
