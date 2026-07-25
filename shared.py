from functools import wraps

from flask_caching import Cache
from quart import Quart


def awaitify(sync_func):
    """Wrap a synchronous callable to allow ``await``'ing it."""

    @wraps(sync_func)
    async def async_func(*args, **kwargs):
        return sync_func(*args, **kwargs)

    return async_func


app = Quart(__name__)

######################################################################

host = "localhost"
port = 8885

should_fetch_comments = True

app.config["DEBUG"] = False
app.config["TESTING"] = False

######################################################################

app.config["CACHE_DEFAULT_TIMEOUT"] = 60

app.config["CACHE_TYPE"] = "SimpleCache"  # "RedisCache"

cache = Cache(app)
