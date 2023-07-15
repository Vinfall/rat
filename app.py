import asyncio
import aiotieba

from aioflask import render_template, request, escape
from urllib.parse import quote_plus
from datetime import datetime

from aiotieba.api.get_posts._classdef import *
from aiotieba.api._classdef.contents import *

from shared import *
from extra import *

######################################################################

# Clean a leading part and append the text.
def append_with_leading_clean(orig, content):
    if orig.endswith('<br>'):
        return orig[:-4] + content
    else:
        return orig + content

# Return the corresponding user name for an id.
async def cache_name_from_id(c, i):
    if not cache.get(i):
        r = await c.get_user_info(i, require=aiotieba.enums.ReqUInfo.USER_NAME)
        cache.set(i, r)

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
async def _jinja2_filter_translate(frags, reply_id=0):
    htmlfmt = ''

    if reply_id:
        htmlfmt += f'<a href="/home/main?id={reply_id}">@{ cache.get(reply_id) }</a> '
    
    for i in range(len(frags)):
        frag = frags[i]
        if isinstance(frag, FragText):
            subfrags = frag.text.split('\n')
            for subfrag in subfrags:
                htmlfmt += str(escape(subfrag)) + '<br>'
        elif isinstance(frag, FragImage_p):
            htmlfmt += \
                f'<a target="_blank" href="/proxy/pic/{ extract_image_name(frag.origin_src) }">' \
                f'<img width="{ frag.show_width}" height="{ frag.show_height }" '\
                f'src="/proxy/pic/{ extract_image_name(frag.src) }"></a>'
        elif isinstance(frag, FragEmoji_p):
            htmlfmt = append_with_leading_clean(htmlfmt,
                                                f'<img class="emoticons" alt="[{ frag.desc }]"'
                                                f'src="/static/emoticons/{ quote_plus(frag.desc) }.png">')
            if i+1 < len(frags) and isinstance(frags[i+1], FragImage_p):
                htmlfmt += '<br>'
        elif isinstance(frag, FragLink):
            markup = '<a '; url = frag.raw_url
            if frag.is_external:
                markup += 'style="text-color: #ff0000;" '
            else:
                url = frag.raw_url.lstrip('https://tieba.baidu.com')
            markup += f'href="{ url }">{ frag.title }</a>'
            htmlfmt = append_with_leading_clean(htmlfmt, markup)
        elif isinstance(frag, FragAt):
            htmlfmt = append_with_leading_clean(htmlfmt,
                                                f'<a href="/home/main?id={ frag.user_id }">{ frag.text }</a>')
        else:
            print('Unhandled: ', type(frag))
            print(frag)

    return htmlfmt

######################################################################

@app.route('/p/<tid>')
async def thread_view(tid):
    tid = int(tid)
    pn = int(request.args.get('pn') or 1)
    ao = int(request.args.get('ao') or 0)

    async with aiotieba.Client() as tieba:
        # Default to 15 posts per page, confirm to tieba.baidu.com
        thread_info = await tieba.get_posts(tid, rn=15, pn=pn,
                                            with_comments=should_fetch_comments,
                                            only_thread_author=ao)

        available_users = []
        for floor in thread_info:
            for comment in floor.comments:
                available_users.append(comment.author_id)
                cache.set(comment.author_id, comment.user.user_name)
        
        all_users = {}
        for floor in thread_info:
            for comment in floor.comments:
                if comment.reply_to_id and not comment.reply_to_id in available_users:
                    all_users[comment.reply_to_id] = ''
        all_users = list(all_users.keys())
        
        await asyncio.gather(*(cache_name_from_id(tieba, i) for i in all_users))
    
    return await render_template('thread.html', info=thread_info, ao=ao)

@app.route('/f')
async def forum_view():
    fname =  request.args['kw'][:-1] if request.args['kw'][-1] == '吧' else request.args['kw']
    pn = int(request.args.get('pn') or 1)
    sort = int(request.args.get('sort') or 0)

    async with aiotieba.Client() as tieba:
        if only_use_native_api:
            forum_info, threads = await asyncio.gather(tieba.get_forum_detail(fname),
                                                       tieba.get_threads(fname, pn=pn, sort=sort))
            if hasattr(forum_info, 'slogan'):
                forum_info = { 'avatar': extract_image_name(forum_info.origin_avatar),
                               'topic': forum_info.post_num, 'thread': forum_info.post_num,
                               'member': forum_info.member_num, 'desc': forum_info.slogan,
                               'name': forum_info.fname }
            else:
                forum_info = { 'avatar': 'a6efce1b9d16fdfa6291460ab98f8c5495ee7b51.jpg',
                               'topic': forum_info.post_num, 'thread': forum_info.post_num,
                               'member': forum_info.member_num, 'desc': '贴吧描述暂不可用', 'name': forum_info.fname }
        else:
            forum_info, threads = await asyncio.gather(awaitify(find_tieba_info)(fname),
                                                       tieba.get_threads(fname, pn=pn, sort=sort))
        
        if threads.page.current_page > threads.page.total_page or pn < 1:
            return await render_template('error.html', msg = \
                                         f'请求越界，本贴吧共有 { threads.page.total_page } 页'
                                         f'而您查询了第 { threads.page.current_page} 页')
    return await render_template('bar.html', info=forum_info, threads=threads, sort=sort,
                                 tp = ((115 if threads.page.total_page > 115 else threads.page.total_page) if sort == 0 else threads.page.total_page))

@app.route('/home/main')
async def user_view():
    pn = int(request.args.get('pn') or 1)
    i = request.args.get('id')
    try: # try converting it to user_id, otherwise using the string.
        i = int(i)
    except:
        pass
    
    async with aiotieba.Client() as tieba:
        try:
            hp = await tieba.get_homepage(i, pn)
        except ValueError:
            return await render_template('error.html', msg='您已超过最后页')

    if len(hp[1]) == 0 and pn > 1:
        return await render_template('error.html', msg='您已超过最后页')
    
    return await render_template('user.html', hp=hp, pn=pn)

@app.route('/')
async def main_view():
    return await render_template('index.html')

######################################################################

@app.errorhandler(RuntimeError)
async def runtime_error_view(e):
    if hasattr(e, 'msg'):
        return await render_template('error.html', msg=e.msg)
    return await render_template('error.html', msg='错误信息不可用')

@app.errorhandler(Exception)
async def general_error_view(e):
    return await render_template('error.html', msg=e)

if __name__ == '__main__':
    app.run(debug=True)
