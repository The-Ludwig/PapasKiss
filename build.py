from jinja2 import Environment, FileSystemLoader, select_autoescape
from cooklang import parseRecipe
from glob import glob
import os
import re

# Global variable settings
BASE_NAME = os.getenv("BASE_NAME", "")
TEMPLATE_DIR = os.getenv("TEMPLATE_DIR", "templates")
RECIPE_FILE_PATTERN = os.getenv("RECIPE_FILE_PATTERN", "**/*.cook")
TEMPLATE_OVERVIEW = os.getenv("TEMPLATE_OVERVIEW", "overview.html")
TEMPLATE_RECIPE = os.getenv("TEMPLATE_RECIPE", "recipe.html")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "build")
LINK_EXTENSION = os.getenv("LINK_EXTENSION", "")
REPOSITORY = os.getenv("GITHUB_REPOSITORY", "the-ludwig/cook")
BRANCH = os.getenv("GITHUB_BASE_REF", "main")

env = {"BASE_NAME": BASE_NAME}

print(f"Link extension is {LINK_EXTENSION}")


# Helper functions
def filter_quantity(input: str):
    return input.strip("0").strip(".")
    # try:
    #     num = float(input)
    #     return
    # except ValueError:
    #     return input


def filter_get_ingredients(step):
    return list(filter(lambda x: x["type"] == "ingredient", step))


def link(location):
    return f"{BASE_NAME}/{location}{LINK_EXTENSION}"


def github_link(file_name):
    return f"https://github.com/{REPOSITORY}/blob/{BRANCH}/{file_name}"


def fix_recipe(parsed_recipe):
    """Fuses same ingredients in ingredients list."""
    ings = parsed_recipe["ingredients"]

    stapled = {}

    for idx, ing in enumerate(ings):
        key = (ing["name"], ing["units"])

        if key in stapled:
            try:
                stapled[key]["quantity_number"] += float(ing["quantity"])

                stapled[key]["quantity"] = str(stapled[key]["quantity_number"])
            except ValueError:
                # just give it multiple times if we can't add quantities
                stapled[(ing["name"] + str(idx), ing["units"])] = ing

        else:
            try:
                ing["quantity_number"] = float(ing["quantity"])
            except ValueError:
                ing["quantity_number"] = None
            stapled[key] = ing

    parsed_recipe["ingredients"] = stapled.values()
    return parsed_recipe


class Recipe:
    pattern = re.compile(r"(?P<category>\w+)/(?P<name>\w+).cook")

    def __init__(self, file_name: str):
        with open(file_name, "r") as file:
            self.source = file.read()

        match = Recipe.pattern.match(file_name).groupdict()
        self.category = match["category"]
        self.name = match["name"]
        self.recipe = fix_recipe(parseRecipe(self.source))
        self.display_name = self.name.replace("_", " ")
        self.file_name = file_name
        self.github_link = github_link(self.file_name)
        self.file_output_name = f"{self.name.replace('_', '')}.html"
        self.link = link(self.name.replace("_", ""))


def categories_from_recipe_list(recipe_list):
    categories = {}

    for recipe in recipe_list:
        if recipe.category not in categories:
            categories[recipe.category] = {"name": recipe.category, "recipes": []}

        categories[recipe.category]["recipes"] += [recipe]

    return categories


# Load the recipes
recipe_files = glob(RECIPE_FILE_PATTERN, recursive=True)
recipes = list(map(Recipe, recipe_files))
categories = categories_from_recipe_list(recipes)

# create output dir (build)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load the templates
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=select_autoescape())
env.filters["recipe_quantity"] = filter_quantity
env.filters["recipe_get_ingredients"] = filter_get_ingredients

# generate start page
overview_template = env.get_template(TEMPLATE_OVERVIEW)
with open(os.path.join(OUTPUT_DIR, "index.html"), "w") as file:
    file.write(overview_template.render(categories=list(categories.values()), *env))


# generate recipe pages
recipe_template = env.get_template(TEMPLATE_RECIPE)
for recipe in recipes:
    with open(os.path.join(OUTPUT_DIR, recipe.file_output_name), "w") as file:
        file.write(recipe_template.render(recipe=recipe, *env))
