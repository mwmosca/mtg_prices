import pandas as pd
import requests
from dotenv import load_dotenv
from os import getenv
from pathlib import Path
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

    # Import collection
    collection_file = Path('data', 'collection.csv')
    collection_df = pd.read_csv(collection_file)

    with requests.Session() as session:
        session.headers.update(headers)

        done_flag = ''
        while done_flag != 'y':
            set_code         = input('Gimme the set code: ')
            collector_number = input('Gimme the collector number: ')
            language_code    = input('Gimme the language code: ')
            foil_or_etched   = input('Is it [f]oil or [e]tched? ').lower()

            response = session.get(url + set_code + '/' + collector_number + '/' + language_code)

            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                print(e)
                print()
                continue

            response_body = response.json()
            webbrowser_open(response_body['scryfall_uri'])

            user_input = input('Does this look right? [y/N]:').lower()
            if user_input != 'y':
                print()
                continue

            locator_df = collection_df.loc[
                  (collection_df.id     == response_body['id'])
                & (collection_df.foil   == (foil_or_etched == 'f'))
                & (collection_df.etched == (foil_or_etched == 'e'))
            ]
            if len(locator_df) == 1:
                collection_df.loc[locator_df.index[0], 'quantity'] += 1

            done_flag = input('Done yet? [y/N]: ').lower()

    collection_df.to_csv(collection_file)

if __name__ == '__main__':
    main()
