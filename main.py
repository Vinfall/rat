import multiprocessing

from app import app

from urllib.parse import quote as urlquote, urlparse, urlunparse
from twisted.web.http import _QUEUED_SENTINEL, HTTPChannel, HTTPClient, Request
from twisted.web.resource import Resource
from twisted.web import proxy, server
from twisted.web.static import File
from twisted.internet.protocol import ClientFactory
from twisted.internet import reactor, utils

plain_cookies = {}

################################################################################
# Modified Dynamic Proxy (from twisted)
################################################################################

class ProxyClient(HTTPClient):
    _finished = False

    def __init__(self, command, rest, version, headers, data, father):
        self.father = father
        self.command = command
        self.rest = rest
        if b"proxy-connection" in headers:
            del headers[b"proxy-connection"]
        headers[b"connection"] = b"close"
        headers.pop(b"keep-alive", None)
        self.headers = headers
        self.data = data

    def connectionMade(self):
        self.sendCommand(self.command, self.rest)
        for header, value in self.headers.items():
            self.sendHeader(header, value)
        self.endHeaders()
        self.transport.write(self.data)

    def handleStatus(self, version, code, message):
        self.father.setResponseCode(int(code), message)

    def handleHeader(self, key, value):
        if key.lower() in [b"server", b"date", b"content-type"]:
            self.father.responseHeaders.setRawHeaders(key, [value])
        else:
            self.father.responseHeaders.addRawHeader(key, value)

    def handleResponsePart(self, buffer):
        self.father.write(buffer)

    def handleResponseEnd(self):
        if not self._finished:
            self._finished = True
            self.father.notifyFinish().addErrback(lambda x: None)
            self.transport.loseConnection()

class ProxyClientFactory(ClientFactory):
    protocol = ProxyClient

    def __init__(self, command, rest, version, headers, data, father):
        self.father = father
        self.command = command
        self.rest = rest
        self.headers = headers
        self.data = data
        self.version = version

    def buildProtocol(self, addr):
        return self.protocol(
            self.command, self.rest, self.version, self.headers, self.data, self.father
        )

    def clientConnectionFailed(self, connector, reason):
        self.father.setResponseCode(501, b"Gateway error")
        self.father.responseHeaders.addRawHeader(b"Content-Type", b"text/html")
        self.father.write(b"<H1>Could not connect</H1>")
        self.father.finish()

class ReverseProxyResource(Resource):
    def __init__(self, path, reactor=reactor):
        Resource.__init__(self)
        self.path = path
        self.reactor = reactor

    def getChild(self, path, request):
        return ReverseProxyResource(
            self.path + b'/' + urlquote(path, safe=b'').encode("utf-8"),
            self.reactor
        )

    def render_proxy_avatar(self, request, req_path):
        portrait = req_path[14:]

        request.requestHeaders.setRawHeaders(b'host', [b'tb.himg.baidu.com'])
        request.content.seek(0, 0)

        clientFactory = ProxyClientFactory(
            b'GET', ('http://tb.himg.baidu.com/sys/portraith/item/' + portrait).encode('utf-8'),
            request.clientproto,
            request.getAllHeaders(),
            request.content.read(),
            request,
        )
        
        self.reactor.connectTCP('tb.himg.baidu.com', 80, clientFactory)
        return server.NOT_DONE_YET
    
    def render_proxy_pic(self, request, req_path):
        pic = req_path[11:]

        request.requestHeaders.setRawHeaders(b'host', [b'imgsa.baidu.com'])
        request.content.seek(0, 0)

        clientFactory = ProxyClientFactory(
            b'GET', ('http://imgsa.baidu.com/forum/pic/item/' + pic).encode('utf-8'),
            request.clientproto,
            request.getAllHeaders(),
            request.content.read(),
            request,
        )
        
        self.reactor.connectTCP('imgsa.baidu.com', 80, clientFactory)
        return server.NOT_DONE_YET
        
    def render(self, request):
        # Justify the request path.
        req_path = self.path.decode('utf-8')
        if req_path.startswith('/proxy/avatar/'):
            return self.render_proxy_avatar(request, req_path)
        elif req_path.startswith('/proxy/pic/'):
            return self.render_proxy_pic(request, req_path)
        else:
            request.setResponseCode(418, b'I\'m a teapot')
            return

################################################################################

# To start this function for testing: python -c 'import main; main.twisted_start()'
def twisted_start():
    flask_port = int(app.config['SERVER_NAME'].split(':')[1])
    flask_res = proxy.ReverseProxyResource('127.0.0.1', flask_port, b'')
    flask_res.putChild(b'proxy', ReverseProxyResource(b'/proxy'))
    flask_res.putChild(b'static', File('static'))

    print(f' *** SERVER IS RUNNING ON PORT {flask_port-1} ***')
    
    site = server.Site(flask_res)
    reactor.listenTCP(flask_port-1, site)
    reactor.run()

# To start this function for testing: python -c 'import main; main.flask_start()'
def flask_start():
    app.run()

# If we're executed directly, also start the flask daemon.
if __name__ == '__main__':
    flask_task = multiprocessing.Process(target=flask_start)
    flask_task.daemon = True # Exit the child if the parent was killed :-(
    flask_task.start()
    twisted_start()
