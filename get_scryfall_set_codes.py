import csv
import requests
from datetime import datetime
from dotenv import load_dotenv
from os import getenv
from pathlib import Path

load_dotenv()

SCHEME     = 'https'              # API requests are only served over HTTPS, using TLS 1.2 or better. Requests will not be honored over plaintext HTTP.
HOSTNAME   = 'api.scryfall.com'
USER_AGENT = getenv('USER_AGENT') # REQUIRED - must be accurate to your usage context
ACCEPT     = 'application/json'   # REQUIRED - must be present, but you can provide a generic preference.

url = f'{SCHEME}://{HOSTNAME}/sets'
headers = {
    'User-Agent' : USER_AGENT,
    'Accept'     : ACCEPT
}

response = requests.get(url, headers=headers)
response.raise_for_status()
mtg_sets = response.json()['data']

# The API uses UTF-8 character encoding for all responses. Many fields will include characters that are not in the ASCII range.
with open(Path('reports', f'scryfall_set_codes_{datetime.now().strftime("%Y%m%d")}.csv'), mode='w', newline='', encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=['name', 'code'], extrasaction='ignore')
    w.writeheader()
    w.writerows(mtg_sets)
