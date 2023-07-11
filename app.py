import asyncio
import aiotieba

from aioflask import render_template, request, escape
from flask_caching import Cache
from urllib.parse import quote_plus
from datetime import datetime

from aiotieba.api.get_posts._classdef import *
from aiotieba.api._classdef.contents import *

from shared import *
from extra import *

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

# Format fragments to its equiviant HTML.
@app.template_filter('translate')
def _jinja2_filter_translate(frags):
    htmlfmt = ''
    
    for frag in frags:
        if isinstance(frag, FragText):
            subfrags = frag.text.split('\n')
            for subfrag in subfrags:
                htmlfmt += '<p>' + str(escape(subfrag)) + '</p>'
        elif isinstance(frag, FragImage_p):
            htmlfmt += \
                f'<a target="_blank" href="/proxy/pic/{ extract_image_name(frag.origin_src) }">' \
                f'<img width="{ frag.show_width}" height="{ frag.show_height }" '\
                f'src="/proxy/pic/{ extract_image_name(frag.src) }"></a>'
        elif isinstance(frag, FragEmoji_p):
            clear_leading = False
            if htmlfmt.endswith('</p>'):
                clear_leading = True
                htmlfmt = htmlfmt.rstrip('</p>')
            htmlfmt += f'<img class="emoticons" alt="[{ frag.desc }]" src="/static/emoticons/{ quote_plus(frag.desc) }.png">'
            if clear_leading:
                htmlfmt += '</p>'
            
    return htmlfmt

######################################################################

@app.route('/p/<tid>')
async def thread_view(tid):
    tid = int(tid)
    pn = int(request.args.get('pn') or 1)

    async with aiotieba.Client() as tieba:
        # Default to 15 posts per page, confirm to tieba.baidu.com
        thread_info = await tieba.get_posts(tid, rn=15, pn=pn)

    for post in thread_info:
        print(post.comments)
    
    return await render_template('thread.html', info=thread_info)

@app.route('/f')
async def forum_view():
    fname =  request.args['kw']
    pn = int(request.args.get('pn') or 1)

    async with aiotieba.Client() as tieba:
        forum_info, threads = await asyncio.gather(awaitify(find_tieba_info)(fname),
                                                   tieba.get_threads(fname, rn=50, pn=pn))

    return await render_template('bar.html', info=forum_info, threads=threads)

if __name__ == '__main__':
    app.run(debug=True)
