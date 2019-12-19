from saltToTaste import create_app
from cheroot.wsgi import Server as WSGIServer

app = create_app()
host = "0.0.0.0"
port = 8100
server = WSGIServer((host, port), app)

def main():
    try:
        print (f"Starting Salt to Taste on {host}:{port}")
        server.start()
    except KeyboardInterrupt:
       server.stop()
       print ("Server stopped")

if __name__ == '__main__':
  main()
