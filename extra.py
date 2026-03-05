"""Extra APIs."""

import re

from shared import *


# TODO: known bug, can't extract from super old editor images.
def extract_image_name(url):
    match = re.search(r"/(\w+)\.jpg", url)
    try:
        return match.group(1) + ".jpg"
    except:
        return "a6efce1b9d16fdfa6291460ab98f8c5495ee7b51.jpg"
