import asyncio
import aiohttp

class AsgiproxifyHandler():
    def __init__(self, scope):
        self.scope = scope
    
    def make_request_url(self):
        return 'http://example.org/'

    def make_request_cookies(self):
        return {}

    def make_request_headers(self):
        req_headers = {k.decode(): v.decode() for k, v in self.scope['headers']}
        req_headers.pop('host', None)
        return req_headers

    def make_response_headers(self, upstream_headers):
        headers = dict(upstream_headers)
        headers.pop('Server', None)
        headers.pop('Date', None)
        
        resp_headers = [(k, v) for k, v in headers.items()]
        return resp_headers
    
    def make_request(self, session):
        return session.request('GET',  self.make_request_url(),
                               cookies=self.make_request_cookies(),
                               headers=self.make_request_headers(),)

class Asgiproxify():
    app = None
    reg = {}

    def __init__(self, app=None):
        self.to(app)
    
    def to(self, app):
        self.app = app

    def install(self, leading_path, handler):
        self.reg[leading_path] = handler

    def register(self, leading_path):
        def decorator(c):
            self.install(leading_path, c)
        return decorator
    
    async def handle_proxy(self, scope, receive, send, handler):
        handler_i = handler(scope)
        request = await receive()

        async def reverse_proxy_task():
            async with aiohttp.ClientSession(auto_decompress=False) as session:
                async with handler_i.make_request(session) as resp:
                    await send({
                        'type': 'http.response.start',
                        'status': resp.status,
                        'headers': handler_i.make_response_headers(resp.headers),
                    })
                    async for chunk, end_of_resp in resp.content.iter_chunks():
                        await send({
                            'type': 'http.response.body',
                            'body': chunk,
                            'more_body': True,
                        })
                    await send({ 'type': 'http.response.body' })
                
        task = asyncio.create_task(reverse_proxy_task())
        while True:
            ev = await receive()
            if ev['type'] == 'http.disconnect':
                task.cancel()
                return

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)
        
        handler = None

        for leading_path, proxy_handler in self.reg.items():
            if scope['path'].startswith(leading_path):
                handler = proxy_handler

        if not handler:
            return await self.app(scope, receive, send)
        else:
            return await self.handle_proxy(scope, receive, send, handler)
