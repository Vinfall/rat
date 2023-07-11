from aioflask import Flask
from flask_caching import Cache

from functools import wraps

def awaitify(sync_func):
    """Wrap a synchronous callable to allow ``await``'ing it"""
    @wraps(sync_func)
    async def async_func(*args, **kwargs):
        return sync_func(*args, **kwargs)
    return async_func

app = Flask(__name__)

app.config['SERVER_NAME'] = ':6666'

app.config['CACHE_TYPE'] = 'SimpleCache'
cache = Cache(app)
