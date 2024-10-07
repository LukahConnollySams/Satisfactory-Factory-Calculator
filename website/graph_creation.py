from website import db
from website.satisfactoryobjects.recipe import Recipe
from pyvis.network import Network
from website.models import (
    ItemRecipeTable,
    ItemTable,
    RecipeTable
)
from app import app
from bs4 import BeautifulSoup
import networkx as nx


def remove_annoying_css(file: str) -> None:
    """
    Uses bs4 to remove a bunch of css from the html produced by VisJS, for easier display customisation.

    Parameters
    ----------
    file : .html file
        _description_
    """

    # open file
    html = open(file, "r")

    # parse file in bs4
    soup = BeautifulSoup(html, "html.parser")

    # remove the pain in the arse css that causes navbar in bootstrap to break
    soup.find(
        href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta3/dist/css/bootstrap.min.css"
    ).decompose()

    # this anooying css stops graph from being centered in page
    del soup.find(class_="card").attrs["style"]

    # rewrite original file
    with open(file, "wb") as file:
        file.write(soup.prettify("utf-8"))


def recipe_query(
    item: str,
    amount: int | None = None,
    recursive: bool = False,
    alt: bool = False,
    alt_recipes: list = []
):
    """
    Queries database to find the desired recipe from the outputs name.
    This function can be run recursively to get a list of recipes that chain together until branches are exhuasted.

    Parameters
    ----------
    item : str
        Item name
    amount : int | None, optional
        Amount of item needed, by default None
    recursive : bool, optional
        Whether or not to recursively call function, by default False
    alt : bool, optional
        _description_, by default False
    alt_recipes : list, optional
        _description_, by default []

    Returns
    -------
    list[tuple[Recipe, int | float]]
        List of recipes and scaling amounts zipped together
    """
    # waiting to add functionality for selecting specific recipes
    # query item table
    with app.app_context():
        items = db.session().query(ItemTable).filter_by(name=item).all()

        # use ids from above to query itemrecipe table with io = True
        outputs = []
        for query_result in items:
            is_outputs = (
                db.session().query(ItemRecipeTable).filter_by(item_id=query_result.id, io=True).all()
            )

            if is_outputs:
                outputs.extend(is_outputs)

        # query table to get recipes based on if they are alternative or base recipe
        final = []
        for result in outputs:
            not_alt = (
                db.session().query(RecipeTable).filter_by(id=result.recipe_id, alternate=alt).all()
            )

            if not_alt:
                final.extend(
                    not_alt
                )  # add func for alternate recipes (if statement to check string for compatible recipes)

        # if no recipes found
        if len(final) < 1:
            return False

        # checking for multiple outputs, prioritising those without, for simplicity
        for potential_recipe in final:
            # get recipe object from that
            temp_recipe = Recipe.from_db(potential_recipe, db)

            if temp_recipe.building == 'Converter':
                return False

            elif len(temp_recipe.outputs) > 1:
                if "Empty Canister" in temp_recipe.outputs:
                    continue

                recipe = temp_recipe
                continue

            else:
                recipe = temp_recipe
                break

        if amount is not None:
            scale = recipe.scale_recipe(amount, target_ouput=item)

        else:
            scale = 1

        # if statement to check for recursive functionality:
        if recursive:
            recursive_recipes = []
            scales = []  # noqa: F841
            for input, quantity in recipe.inputs.items():
                if input == "Water" or input == "Crude Oil":  # need a way to formalise this
                    continue

                thing = recipe_query(input, quantity * scale, recursive=True)

                if thing is None or not thing:
                    continue

                recursive_recipes.extend(thing)

        else:
            recursive_recipes = [(recipe, scale)]

        # remove false values
        recipes = [i for i in recursive_recipes if i]

        # zip scale together with recipe
        recipes.append((recipe, scale))

        return recipes


def make_net(recipes, network=None, file=r"website\templates\graph.html"):
    """
    Creates a Vis network graph from a list of recipes with scaling values.

    Parameters
    ----------
    recipes : list[tuple[Recipe, int | float]]
        _description_
    network : DiGraph | None, optional
        Networkx DiGraph to add new recipes to (will create a new one if None), by default None
    file : str, optional
        File to save html to, by default r"website\templates\graph.html"

    """

    # initialise networkx network
    if network is None:
        recipe_network = nx.DiGraph()

    else:
        recipe_network = network

    # get Network from Recipe Object
    for recipe, scale in recipes:
        recipe_network = recipe.get_nx_graph(
            recipe_network, scale
        )  # need to subtract input edge values from outputedge values

    # convert to PyVis network
    vis_network = Network(
        "800px",
        "1400px",
        directed=True,
        bgcolor="#1d1d1d",
        cdn_resources="local",
        font_color="white",
    )
    vis_network.from_nx(recipe_network)

    # Visualisation settings in json format
    options = """const options = {
  "edges": {
    "endPointOffset": {
      "to": 2
    },
    "color": {
      "inherit": false
    },
    "physics": false,
    "scaling": {
      "max": 20
    },
    "font": {
      "color": "white",
      "strokeWidth": 0
    },
    "smooth": false
  },
  "layout": {
    "imporvedLayout": false,
    "hierarchical": {
      "enabled": true,
      "levelSeparation": 250,
      "nodeSpacing": 250,
      "treeSpacing": 1,
      "edgeMinimization": false,
      "parentCentralization": false,
      "direction": "LR",
      "sortMethod": "directed",
      "shakeLeaves": "roots"
    }
  },
  "manipulation": {
    "enabled": true
  },
  "physics": {
    "enabled": true,
    "hierarchicalRepulsion": {
      "centralGravity": 0,
      "avoidOverlap": null
    },
    "minVelocity": 0.75,
    "solver": "hierarchicalRepulsion"
  },
  "interaction": {
    "multiselect": true
  }
}"""

    vis_network.set_options(options)

    # allow for physics rendering but disable after initial graph generation by implementing custom template (~lines 547-556)
    vis_network.set_template_dir(
        r"website\templates\my_pyvis_templates", template_file="template.html"
    )

    # display network
    vis_network.save_graph(file)

    # remove style sheet to be compatable with website
    remove_annoying_css(file)
