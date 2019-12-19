import os
from saltToTaste.parser_handler import argparser_results
from saltToTaste.file_handler import create_api_key

argument = argparser_results()
DATA_DIR = os.path.abspath(argument['DATA_DIR'])

# Create the DATA_DIR if it doesn't exist
if not os.path.exists(DATA_DIR):
    try:
        os.makedirs(DATA_DIR)
    except OSError:
        raise SystemExit(f'Could not create data directory: {DATA_DIR}. Exiting....')
# Make sure the DATA_DIR is writeable
if not os.access(DATA_DIR, os.W_OK):
    raise SystemExit(f'Cannot write to the data directory: {DATA_DIR}. Exiting...')

# Make DATA_DIR subfolders if they don't exist
subfolders = ['_recipes', '_images']
for folder in subfolders:
    if not os.path.exists(f'{DATA_DIR}/{folder}'):
        try:
            os.makedirs(f'{DATA_DIR}/{folder}')
        except OSError:
            raise SystemExit(f'Could not create data directory: {DATA_DIR}/{folder}. Exiting....')
    # Make sure the subfolder is writeable
    if not os.access(f'{DATA_DIR}/{folder}', os.W_OK):
        raise SystemExit(f'Cannot write to the data directory: {DATA_DIR}/{folder}. Exiting...')

# Create API key if it doesn't exist
try:
    api_key = open(f'{DATA_DIR}/saltToTaste.key', 'r', encoding='utf-16').readline()
except:
    if not os.path.isfile(f'{DATA_DIR}/saltToTaste.key'):
        create_api_key(DATA_DIR)
        api_key = open(f'{DATA_DIR}/saltToTaste.key', 'r', encoding='utf-16').readline()
