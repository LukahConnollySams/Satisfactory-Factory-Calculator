from website.satisfactoryobjects.recipe import Recipe
from bs4 import BeautifulSoup, SoupStrainer
import requests
import regex as re
from website.webscraping.get_images import get_image


def get_recipe_links(url):
    """
    Retrieves the links for all craftable items from the provided url.

    Parameters
    ----------
    url : str
        URL to extract URL's from.

    Returns
    -------
    list[str]
        List of all the desired hyperlinks as strings.
    """
    html = requests.get(url)
    html = BeautifulSoup(html.text, 'html.parser')

    items_list = html.find('div', id='mw-pages').find('div', class_='mw-category mw-category-columns').find_all('a')

    links = []
    
    for link in items_list:
        hyper_link = link.get('href')
        links.append('https://satisfactory.wiki.gg' + str(hyper_link))

    return links

def get_recipes(url, get_images=True):
    """_summary_

    Parameters
    ----------
    url : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """

    links = get_recipe_links(url)
    recipes = []
    images = []
    partial_parse = SoupStrainer('table', class_='wikitable sortable recipetable')

    for link in links:

        #optional tracker
        #print(f'We got to {link}\n')
        if get_images:

            images.append(get_image(link))

        #get all the desired tables
        html = requests.get(link)
        recipe_tables = BeautifulSoup(html.text, 'html.parser', parse_only=partial_parse)

        for table in recipe_tables:

            #get table rows inside body of table (not header or footer)
            rows = table.find('tbody').find_all('tr')
            recipes.append(read_rows(rows))

            
    recipes = {item for row in recipes for item in row}

    return recipes, images
        
def read_rows(rows):
    """
    Read rows of recipe tables and produces a Recipe object for each row.

    Parameters
    ----------
    rows : list[soup]
        List of soup containing the rows of recipe table.

    Returns
    -------
    list[Recipe]
        List of recipe objects derived from the input.
    """
    
    recipes = []
    for row in rows:

        td = row.find_all('td')

        #issues with table formatting solved with this conditional
        if td and td[2].find('a').string != 'Build Gun':
            recipes.append(Recipe(
                td[0].contents[0],
                dict(get_items_from_table(td[1])), 
                dict(get_items_from_table(td[3])), 
                td[2].find('a').string,
                alternate=len(td[0].contents) > 1
            ))

        #add if statement for only handcraftable items...

    return recipes

def get_items_from_table(td):

    items = []

    for div in td.find_all('div', class_='recipe-item'):

        items.append((
            div.find('span', 'item-name').string,
            float(''.join(re.findall(r'\d+\.\d+|\d', div.find('span', 'item-minute').string)))
        ))
        

    return items

def write_recipes(recipe_list):
    """
    Writes a list of Recipe objects to file

    Parameters
    ----------
    recipe_list :list[Recipe]
        List of Recipe objects to be written to file.
    """
    file = open(r'website\static\recipes\recipes.txt', 'w')

    for recipe in recipe_list:

        #avoid extra blank line at end of file
        if recipe == recipe_list[-1]:

            file.write(str(recipe))
            break

        file.write(str(recipe) + '\n')

    file.close()
