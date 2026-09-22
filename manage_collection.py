import requests
from dotenv import load_dotenv
from os import getenv
from scryfall_utils import HOSTNAME, SCHEME
from webbrowser import open as webbrowser_open

def main() -> None:
    load_dotenv()
    USER_AGENT = getenv('USER_AGENT') # REQUIRED - must be accurate to your usage context
    ACCEPT     = 'application/json'   # REQUIRED - must be present, but you can provide a generic preference.

    headers = {
        'User-Agent'   : USER_AGENT,
        'Accept'       : ACCEPT,
    }

    url = f'{SCHEME}://{HOSTNAME}/cards/'
    # https://scryfall.com/docs/api/cards/collector

    with requests.Session() as session:
        session.headers.update(headers)

        while True:
            set_code         = input('Gimme the set code: ')
            collector_number = input('Gimme the collector number: ')
            language_code    = input('Gimme the language code: ')
            response         = session.get(url + set_code + '/' + collector_number + '/' + language_code)

            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                print(e)
                print()
                continue

            response_body = response.json()
            webbrowser_open(response_body['uri'])

            user_input = input('Does this look right? [y/N]:')
            if user_input.lower() != 'y':
                print()
                continue

            # Processing code to be implemented

if __name__ == '__main__':
    main()
