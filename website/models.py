from . import db


class RecipeTable(db.Model):  
    __tablename__ = "recipetable"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    building = db.Column(db.Integer, db.ForeignKey("buildingtable.id"), nullable=False)
    alternate = db.Column(db.Boolean)

    # relationship for inputs
    inputs = db.relationship(
        "ItemTable",
        secondary="itemrecipetable",
        primaryjoin="and_(RecipeTable.id == ItemRecipeTable.recipe_id, ItemRecipeTable.io == False)",
        secondaryjoin="ItemTable.id == ItemRecipeTable.item_id",
    )

    # relationship for outputs
    outputs = db.relationship(
        "ItemTable",
        secondary="itemrecipetable",
        primaryjoin="and_(RecipeTable.id == ItemRecipeTable.recipe_id, ItemRecipeTable.io == True)",
        secondaryjoin="ItemTable.id == ItemRecipeTable.item_id",
        overlaps="inputs",
    )


class ItemRecipeTable(db.Model):
    __tablename__ = "itemrecipetable"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("itemtable.id"))
    recipe_id = db.Column(db.Integer, db.ForeignKey("recipetable.id"))
    io = db.Column(db.Boolean, nullable=False)


class ItemTable(db.Model):
    __tablename__ = "itemtable"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)


class BuildingTable(db.Model):
    __tablename__ = "buildingtable"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    outputs = db.Column(db.Integer)

    recipes = db.relationship("RecipeTable")


def populate_table(insert_recipe) -> None:
    """
    Populates the databse tables with the inserted Recipe object.

    Parameters
    ----------
    insert_recipe : Recipe
        Recipe to be added to the database
    """
    # query the building tbale for recipe's building, add if not there 
    building = (
        db.session.query(BuildingTable).filter_by(name=insert_recipe.building).first()
    )
    
    if not building:
        building = BuildingTable(name=insert_recipe.building)
        db.session.add(building)
        db.session.commit()

    # 
    recipe = RecipeTable(
        name=insert_recipe.name, building=building.id, alternate=insert_recipe.alternate
    )
    db.session.add(recipe)
    db.session.commit()

    for item_name, amount in insert_recipe.inputs.items():
        item = (
            db.session.query(ItemTable).filter_by(name=item_name, amount=amount).first()
        )

        if not item:
            item = ItemTable(name=item_name, amount=amount)
            db.session.add(item)
            db.session.commit()

        item_recipe = ItemRecipeTable(recipe_id=recipe.id, item_id=item.id, io=False)
        db.session.add(item_recipe)

    for item_name, amount in insert_recipe.outputs.items():
        item = (
            db.session.query(ItemTable).filter_by(name=item_name, amount=amount).first()
        )

        if not item:
            item = ItemTable(name=item_name, amount=amount)
            db.session.add(item)
            db.session.commit()

        item_recipe = ItemRecipeTable(recipe_id=recipe.id, item_id=item.id, io=True)
        db.session.add(item_recipe)

    db.session.commit()
