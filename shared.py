from aioflask import Flask
from flask_caching import Cache

from functools import wraps

from proxify import Asgiproxify

def awaitify(sync_func):
    """Wrap a synchronous callable to allow ``await``'ing it"""
    @wraps(sync_func)
    async def async_func(*args, **kwargs):
        return sync_func(*args, **kwargs)
    return async_func

app = Flask(__name__)
proxified = Asgiproxify(app)

######################################################################

host = 'localhost'
port = 8885

should_fetch_comments = True

app.config['DEBUG'] = False
app.config['TESTING'] = False

######################################################################

app.config['CACHE_TYPE'] = 'SimpleCache'
cache = Cache(app)
