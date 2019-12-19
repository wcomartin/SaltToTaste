import os
import logging
from cheroot.wsgi import Server as WSGIServer
from saltToTaste import create_app
from saltToTaste.parser_handler import argparser_results

argument = argparser_results()
DATA_DIR = os.path.abspath(argument['DATA_DIR'])

logging.basicConfig(filename=f'{DATA_DIR}/logs/saltToTaste.log',level=logging.DEBUG, format='%(asctime)s - %(levelname)s : %(message)s')
app = create_app()
host = "0.0.0.0"
port = 8100
server = WSGIServer((host, port), app)

def main():
    try:
        logging.info(f"Starting server on {host}:{port}")
        server.start()
    except KeyboardInterrupt:
       server.stop()
       logging.info("Server stopped")

if __name__ == '__main__':
  main()
