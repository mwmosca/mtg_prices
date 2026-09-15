from dotenv import load_dotenv
from os import getenv
import requests
from scryfall_utils import HOSTNAME, SCHEME

def main() -> None:
    load_dotenv()
    USER_AGENT = getenv('USER_AGENT') # REQUIRED - must be accurate to your usage context
    ACCEPT     = 'application/json'   # REQUIRED - must be present, but you can provide a generic preference.
    url = f'{SCHEME}://{HOSTNAME}/cards/'
    headers = {
        'User-Agent'   : USER_AGENT,
        'Accept'       : ACCEPT,
        'Content-Type' : 'application/json;charset=utf-8' # REQUIRED - /cards/collection requests must be posted with Content-Type as application/json.
    }

    with requests.Session() as session:
        session.headers.update(headers)

        set_code         = input('Gimme the set code: ')
        collector_number = input('Gimme the collector number: ')
        response = session.get(url + set_code + '/' + collector_number)
        response.raise_for_status()
        response_body = response.json()
        print(response_body)


if __name__ == '__main__':
    main()
