from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Shanghai")


def init_filters(app):

    # Convert a timestamp to its simplest readable date format.
    @app.template_filter("simpledate")
    def _jinja2_filter_simpledate(ts):
        t = datetime.fromtimestamp(ts, tz=TZ)
        now = datetime.now(tz=TZ)

        if t.date() == now.date():
            return t.strftime("%H:%M")
        elif t.year == now.year:
            return t.strftime("%m-%d")
        else:
            return t.strftime("%Y-%m-%d")

    # Convert a timestamp to a human readable date format.
    @app.template_filter("date")
    def _jinja2_filter_datetime(ts, fmt="%Y-%m-%d %H:%M"):
        return datetime.fromtimestamp(ts, tz=TZ).strftime(fmt)

    # Convert a integer to the one with separator like 1,000,000.
    @app.template_filter("intsep")
    def _jinja2_filter_intsep(i):
        return f"{int(i):,}"

    # Convert a duration in seconds to human readable duration
    @app.template_filter("secdur")
    def __jinja2_filter_secdur(delta_t):
        return str(timedelta(seconds=int(delta_t)))

    # Reduce the text to a shorter form.
    @app.template_filter("trim")
    def _jinja2_filter_trim(text):
        return text[:78] + "……" if len(text) > 78 else text
