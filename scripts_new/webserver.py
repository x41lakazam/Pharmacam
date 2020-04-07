import flask
import socket

class SocketStream:

    def __init__(self, stream, host='0.0.0.0', port=8687):
        self.stream     = stream
        self.socket     = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_add = (host, port)
        self.connections = []
        self.alive = True
   
    def run(self):
        self.socket.listen(1)

        while self.alive:
            conn, client_add = self.socket.accept()
            self.connections.append(conn)
            frame = self.stream.read()
            self.socket.sendall(frame)

        self.socket.close()

    def close():
        print("[Webserver] Socket closed.")
        self.alive = False

class WebServerStream:

    def __init__(self, stream, name='WebCam', host='0.0.0.0', port=8686):
        self.stream = stream

        self.name = name
        self.host = host
        self.port = port

        self.app = flask.Flask(self.name)

        @self.app.route('/read')
        def read():
            frame = self.stream.read()
            response = flask.make_response(frame.tobytes())
            response.headers.set('Content-Type', 'application/octet-stream')
            
            return response

        @self.app.route('/')
        def home():
            msg = 'To read the stream, fetch: <a href="{0}">{0}</a>'.format(flask.url_for('read'))
            return msg

    def run(self): 
        self.app.run(host=self.host, port=self.port)
