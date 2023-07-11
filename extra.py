'''Extra APIs'''

import requests
import bs4
import re

from shared import *

def extract_image_name(url):
    match = re.search(r'/(\w+)\.jpg', url)
    return match.group(1) + '.jpg'

@cache.cached(timeout=60, key_prefix='tieba_info')
def find_tieba_info(tname):
    """Get the tiebat avatar for the forum name.

    :param tname: the name of the target forum.
    :returns: the internal ID of the corresponding avatar.

    """
    info = { 'name': tname }
    
    res = requests.get('https://tieba.baidu.com/f', params={'kw': tname})
    soup = bs4.BeautifulSoup(res.text, 'html.parser')

    elems = soup.select('#forum-card-head')
    info['avatar'] = extract_image_name(elems[0]['src'])

    footer = soup.select('.th_footer_l')[0]
    stat_elems = footer.findAll('span', {'class': 'red_text'}, recursive=False)
    stats = list(map(lambda x: int(x.text), stat_elems))

    info |= { 'topic': stats[0], 'thread': stats[1], 'member': stats[2] }

    slogan = soup.select('.card_slogan')[0]
    info['desc'] = slogan.text
    
    return info
