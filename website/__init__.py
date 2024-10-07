from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .views import views

db = SQLAlchemy()
DB_NAME = 'satisfactory.db'


def database_init(recipe_file: str = r"website\static\recipes\recipes.txt"):
    """
    After database initialisation this will check to see if the database is empty. 
    If empty the function will populate the database with data taken from a file, if no file exist, it will create one with the webscraping module.

    Parameters
    ----------
    recipe_file : str, optional
        Location of the recipe file to populate database, by default r'website\static\recipes\recipes_test.txt'

    Returns
    ----------
    None
        Return None when database is already populated with data.
    """
    
    from website.models import RecipeTable, populate_table
    from website.satisfactoryobjects.recipe import Recipe
    import os 

    if db.session().query(RecipeTable).first():
        # true in this scenario means, no further action is needed (database populated)
        return None
    
    # get recipes from file
    if os.path.isfile(recipe_file):

        print('File found')
        recipes = Recipe.recipes_from_file(recipe_file)

    else:

        print('File Not found\nWebscraping Wiki.gg for data needed...')
        # if no file, webscrape and write to file
        from website.webscraping.get_recipes import get_recipes, write_recipes
        from website.webscraping.get_images import write_images
        
        recipe_list, image_links = get_recipes('https://satisfactory.wiki.gg/wiki/Category:Items')
        recipe_list2, image_links2 = get_recipes('https://satisfactory.wiki.gg/wiki/Category:Fluids')

        recipe_list.update(recipe_list2)
        image_links.extend(image_links2)

        write_recipes(list(recipe_list))
        write_images(image_links)

        recipes = Recipe.recipes_from_file(recipe_file)


    # add recipes to database
    for recipe in recipes:

        populate_table(recipe)

def create_app():    

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)


    app.register_blueprint(views, url_prefix='/')

    from .models import RecipeTable, ItemTable, ItemRecipeTable, BuildingTable

    with app.app_context():
        db.create_all()

        _ = database_init()

    return app
