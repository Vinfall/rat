import asyncio
import aiotieba

from aioflask import Flask, render_template, request
from datetime import datetime

from extra import *

app = Flask(__name__)

######################################################################

# Convert a timestamp to its simpliest readable date format.
@app.template_filter('simpledate')
def _jinja2_filter_simpledate(ts):
    t = datetime.fromtimestamp(ts)
    now = datetime.now()

    if t.date() == now.date():
        return t.strftime('%H:%m')
    elif t.year == now.year:
        return t.strftime('%m-%d')
    else:
        return t.strftime('%Y-%m-%d')
    
# Convert a timestamp to a humand readable date format.
@app.template_filter('date')
def _jinja2_filter_datetime(ts, fmt='%Y年%m月%d日 %H点%m分'):
	return datetime.fromtimestamp(ts).strftime(fmt)

# Convert a integer to the one with separator like 1,000,000.
@app.template_filter('intsep')
def _jinja2_filter_intsep(i):
        return f'{int(i):,}'

# Reduce the text to a shorter form.
@app.template_filter('trim')
def _jinja2_filter_trim(text):
    return text[:78] + '……' if len(text) > 78 else text

######################################################################

@app.route('/p/<tid>')
async def thread_view(tid):
    tid = int(tid)
    pn = int(request.args.get('pn') or 1)

    async with aiotieba.Client() as tieba:
        # Default to 15 posts per page, confirm to tieba.baidu.com
        thread_info = await tieba.get_posts(tid, rn=15, pn=pn)

    for fragment in thread_info[0].contents:
        print(fragment)
    
    return await render_template('thread.html', info=thread_info)

@app.route('/f')
async def forum_view():
    fname =  request.args['kw']
    pn = int(request.args.get('pn') or 1)

    async with aiotieba.Client() as tieba:
        forum_info, threads = await asyncio.gather(find_tieba_info(fname),
                                                   tieba.get_threads(fname, rn=50, pn=pn))

    return await render_template('bar.html', info=forum_info, threads=threads)

if __name__ == '__main__':
    app.run(debug=True)
