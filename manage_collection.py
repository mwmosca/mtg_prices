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
            quantity         = int(input('How many? '))

            # Set flags for foiling/etching
            if foil_or_etched == 'f':
                foil   = 1
                etched = 0
            elif foil_or_etched == 'e':
                foil   = 0
                etched = 1
            else:
                foil   = 0
                etched = 0

            # Get the card
            response = session.get(url + set_code + '/' + collector_number + '/' + language_code)
            # Check for valid response
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                print(e)
                print()
                continue
            response_body = response.json()

            # Let the user manually inspect the card
            webbrowser_open(response_body['scryfall_uri'])
            user_input = input('Does this look right? [y/N]:').lower()
            if user_input != 'y':
                print('-- CARD SKIPPED --')
                print()
                continue

            # Check if the card already exists in the collection.
            locator_df = collection_df.loc[
                  (collection_df.id     == response_body['id'])
                & (collection_df.foil   == foil)
                & (collection_df.etched == etched)
            ]
            records = len(locator_df)
            if records == 1: # The card already exists in the collection.
                print(f'Adding {quantity} {response_body['name']}')
                collection_df.loc[locator_df.index[0], 'quantity'] += quantity
            elif records == 0: # The card does not yet exist in the collection, so create a record for it.
                print(f'Creating a new record for {response_body['name']}')
                print(f'Adding {quantity} copies.')
                collection_df = pd.concat([collection_df, pd.DataFrame([{
                    'id'               : response_body['id'],
                    'name'             : response_body['name'],
                    'set_name'         : response_body['set_name'],
                    'collector_number' : response_body['collector_number'],
                    'url'              : response_body['uri'],
                    'foil'             : foil,
                    'etched'           : etched,
                    'quantity'         : quantity
                }])])
            else: # This should never happen.
                raise ValueError(f'Why are there {records} records for {response_body["id"]}?')

            done_flag = input('Done yet? [y/N]: ').lower()
            print()

    collection_df.to_csv(collection_file, index=False)

if __name__ == '__main__':
    main()
