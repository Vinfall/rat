from flask_caching import Cache
from quart import Quart

app = Quart(__name__)

######################################################################

host = "localhost"
port = 8885

# 楼中楼获取，如果浏览性能不佳可以关闭
should_fetch_comments = True
# 用户头像和等级，默认显示
app.config["SHOW_AVATAR"] = True

app.config["DEBUG"] = False
app.config["TESTING"] = False

######################################################################

app.config["CACHE_DEFAULT_TIMEOUT"] = 60
app.config["CACHE_TYPE"] = "SimpleCache"  # "RedisCache"

cache = Cache(app)  # ty:ignore[invalid-argument-type]
