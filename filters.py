from datetime import datetime, timedelta


def init_filters(app):
    # Convert a timestamp to a humand readable date format
    @app.template_filter("date")
    def _jinja2_filter_datetime(ts, fmt="%Y年%m月%d日 %H点%M分"):
        return datetime.fromtimestamp(ts).strftime(fmt)

    # Convert a integer to the one with separator like 1,000,000
    @app.template_filter("intsep")
    def _jinja2_filter_intsep(i):
        return f"{int(i):,}"

    # Convert a duration in seconds to human readable duration
    @app.template_filter("secdur")
    def __jinja2_filter_secdur(delta_t):
        return str(timedelta(seconds=int(delta_t)))
