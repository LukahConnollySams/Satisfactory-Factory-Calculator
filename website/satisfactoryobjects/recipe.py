from dataclasses import dataclass


@dataclass
class Recipe:
    name: str
    inputs: dict[str, int | float]
    outputs: dict[str, int | float]
    building: str
    alternate: bool

    def __str__(self) -> str:
        return f"{self.name}  {self.outputs}  {self.inputs}  {self.building}  Alternate={self.alternate}"

    def __hash__(self) -> int:
        return hash((self.name, str(self.inputs), str(self.outputs), self.building))

    def scale_recipe(self, output_amount: int, target_ouput: str|None=None):
        """
        Returns the factor of the output amount divided by the target recipe output's amount.

        Parameters
        ----------
        output_amount : int
            number for the output of recipe to be scaled to.
        target_ouput : str, optional
            name of the key in the output dict, if none, first output in dict is used instead, by default None.

        Returns
        -------
        float
            Number of _____.
        """
        if target_ouput is not None:
            scale: float = output_amount / self.outputs[target_ouput]

        else:
            scale: float = output_amount / list(self.outputs.values())[0]

        return scale

    @staticmethod
    def get_item_image(image_name: str) -> str:
        """
        Collect link for image from text file using by matching input with end of url.

        Parameters
        ----------
        image_name : str
            _description_

        Returns
        -------
        str
            _description_
        """
        # useful for comparison with webadress
        image_name = image_name.replace(" ", "_") + ".png"
        
        with open(r"website\static\images\images.txt", "r") as file:
            for line in file:
                # obtain final section of webadress
                separate = line.rstrip("\n").split("/")  

                # return line if it it for the desired string input
                if image_name == separate[-1]:
                    return line

            # return to avoid defaulting to None
            return "https://pngtree.com/so/placeholder-vector"

    def get_nx_graph(self, recipe_graph, scale):
        """
        

        Parameters
        ----------
        recipe_graph : _type_
            _description_
        scale : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        nodes = recipe_graph.nodes()
        edges = recipe_graph.edges()

        # networkx implementation
        if recipe_graph.has_node(self.name + " Recipe"):
            # add increased demand
            parse_node_label = nodes[self.name + " Recipe"]["label"]
            parse_node_label = round(
                float(parse_node_label.split("(x")[-1].split(" ")[0]) + scale, 4)
            nodes[self.name + " Recipe"]["label"] = (
                f"{self.name} Recipe:\n(x{round(scale, 4)} {self.building})")

        else:
            recipe_graph.add_node(
                self.name + " Recipe",
                shape="box",
                label=f"{self.name} Recipe:\n(x{round(scale, 4)} {self.building})",
                color="orange"
            )

        for input, amount in self.inputs.items():

            if recipe_graph.has_edge(input, self.name + " Recipe"):

                # check if edge is inbound or outbound, for subtraction instead of addition
                parse_edge_label = edges[(input, self.name + " Recipe")]["label"]  
                parse_edge_label = round(float(parse_edge_label.split(" ")[0]) + amount * scale, 4)
                edges[(input, self.name + " Recipe")]["label"] = (str(parse_edge_label) + " per/min")

            else:
                recipe_graph.add_node(
                    input, shape="image", image=Recipe.get_item_image(input)
                )
                recipe_graph.add_edge(
                    input,
                    self.name + " Recipe",
                    label=str(round(amount * scale, 4)) + " per/min"
                )

        # add all output nodes and direct recipe nodes to output nodes
        for output, amount in self.outputs.items():
            if recipe_graph.has_edge(self.name + " Recipe", output):
                parse_edge_label = edges[(self.name + " Recipe", output)]["label"]
                parse_edge_label = round(
                    float(parse_edge_label.split(" ")[0]) + amount * scale, 4
                )
                edges[(self.name + " Recipe", output)]["label"] = (
                    str(parse_edge_label) + " per/min"
                )

            else:
                recipe_graph.add_node(
                    output, shape="image", image=Recipe.get_item_image(output)
                )
                recipe_graph.add_edge(
                    self.name + " Recipe",
                    output,
                    label=str(round(amount * scale, 4)) + " per/min",
                )

        return recipe_graph

    @staticmethod
    def from_db(db_recipe, db):
        """
        Queries the databse to generate a Recipe Object from RecipeTable entry.

        Parameters
        ----------
        db_recipe : _type_
            _description_
        db : _type_
            Database that has been opened with app.context(), to be used in this session.

        Returns
        -------
        Recipe
            Recipe Object generated from database entry.
        """
        from website.models import (
            BuildingTable,
            ItemRecipeTable,
            ItemTable
        )

        # query recipe inputs and outputs
        inputs_outputs = (db.session().query(ItemRecipeTable).filter_by(recipe_id=db_recipe.id))

        # separate inputs and outputs
        db_inputs = [item for item in inputs_outputs if item.io is False]
        db_outputs = [item for item in inputs_outputs if item.io is True]

        #
        inputs = [db.session().query(ItemTable).get(item.item_id) for item in db_inputs]
        outputs = [db.session().query(ItemTable).get(item.item_id) for item in db_outputs]

        building = db.session().query(BuildingTable).get(db_recipe.building)

        # return Recipe object using data obtained from queries
        return Recipe(
            db_recipe.name,
            inputs={item.name: item.amount for item in inputs},
            outputs={item.name: item.amount for item in outputs},
            building=building.name,
            alternate=db_recipe.alternate
        )

    @staticmethod
    def recipes_from_file(file: str) -> list:
        """
        Generates Recipes from a text file of printed Recipe Objects.

        Parameters
        ----------
        file : str
            Name of file.

        Returns
        -------
        list
            List of generated Recipe Objects.
        """
        recipes = []
        with open(file, "r") as file:

            for line in file:
                data = line.split("  ")
                
                try:
                    recipes.append(
                        Recipe(
                            data[0],
                            eval(data[2]),
                            eval(data[1]),
                            data[3],
                            eval(data[4].split("=")[1]),
                        )) 
                    
                except:
                    continue
             
        # need to safeguard this if using in website
        return recipes
