from bs4 import BeautifulSoup, SoupStrainer
import requests


def write_images(images, file=r'website\static\images\images.txt') -> None:
    """
    Writes a list of strings to a file

    Parameters
    ----------
    images : list[str]
        List of images to write to file
    file : regexp, optional
        Location of file to write to, by default r'website\static\images\images_test.txt'
    """
    file = open(file, 'w')
    for link in images:

        if len(link) < 1:

            continue

        if link == images[-1]:

            file.write(link)
            break
        
        file.write(link + '\n')

    file.close()


def get_image(url: str) -> str:
    """
    Uses bs4 to get first img from the url

    Parameters
    ----------
    url : str
        Url to get image from

    Returns
    -------
    str
        Url of image
    """
    partial_parse = SoupStrainer('img', class_='pi-image-thumbnail')

    html = requests.get(url)
    html = BeautifulSoup(html.text, 'html.parser', parse_only=partial_parse)

    try:

        image_link = 'https://satisfactory.wiki.gg/' + html.find('img')['src']

    except:

        image_link = ""

    return image_link
