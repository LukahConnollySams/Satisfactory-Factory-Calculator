from flask import Blueprint, render_template, request, redirect, url_for
from sqlalchemy import text

views = Blueprint("views", __name__)


@views.route("/")
def home():
    return render_template("base.html")


@views.route("/calculator", methods=["GET", "POST"])
def calculator():
    from website import db
    from .models import ItemTable

    item_names = db.session().query(ItemTable, text("name")).order_by("name").all()
    item_names = [item[1] for item in item_names]

    item_name = []
    _ = [item_name.append(item) for item in item_names if item not in item_name]

    # on form submission
    if request.method == "POST":
        from website.graph_creation import recipe_query, make_net

        # get inputs
        output = request.form.get("output")
        per_min = float(request.form.get("per min"))
        recursive = bool(request.form.get("recursive") == "Yes")

        # generate network graph
        make_net(recipe_query(output, per_min, recursive=recursive))

        return redirect(url_for("views.results"))

    return render_template("calculator.html", name="Calculator", item_db=item_name)


@views.route("/calculator/results")
def results():
    return render_template("results.html")


@views.route("/data")
def data():
    # get links for each image in order to display
    image_links = list(open(r"website\static\images\images.txt", "r"))
    titles = []
    
    # get names of each item for the images
    for link in image_links:
        link = link.split("/")[-1].split(".png")[0].replace("%", "").replace("_", " ")
        new_link = "".join(i for i in link if not i.isdigit())
        titles.append(new_link)

    image_no = len(image_links)

    return render_template(
        "data.html", name="Data", images=zip(image_links, titles), image_no=image_no
    )


@views.route("/recipes")
def recipes():
    # QUERY RECIPES then display
    # NOT IMPLEMENTED YET

    return render_template("recipes.html", name="Recipes")


@views.route("/changelog")
def changelog():
    #will be implemented with automatic changelog
    return render_template("changelog.html", name="Changelog")


@views.route("/quick_graph/<item_name>")
def quick_item_graph(item_name):
    from website.graph_creation import recipe_query, make_net

    item_name_unlinked = str(item_name).replace("_", " ")
    make_net(
        recipe_query(item_name_unlinked, recursive=False),
        file=r"website\templates\quick_graph_result.html",
    )

    return render_template("quick_graph.html", name=item_name_unlinked)
