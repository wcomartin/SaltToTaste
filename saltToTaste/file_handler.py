import os
import logging

def create_flask_secret(DATA_DIR):
    # if not os.path.isfile('saltToTaste.secret'):
    logging.info(f' * Creating Flask secret')
    f = open(f'{DATA_DIR}/saltToTaste.secret', 'w+', encoding='utf-16')
    secret = os.urandom(24).hex()
    f.write(f'{secret}')
    f.close()

def create_api_key(DATA_DIR):
    print (f' * Creating API key')
    f = open(f'{DATA_DIR}/saltToTaste.key', 'w+', encoding='utf-16')
    api_key = os.urandom(24).hex()
    f.write(f'{api_key}')
    f.close()
