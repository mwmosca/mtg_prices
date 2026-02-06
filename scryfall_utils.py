import requests
from time import sleep

BATCH_SIZE_MAX = 75      # A collection request may contain a maximum of 75 cards
COOLDOWN_MIN   = 0.1     # Limit requests to 10/second on average
HOSTNAME       = 'api.scryfall.com'
SCHEME         = 'https' # API requests are only served over HTTPS, using TLS 1.2 or better. Requests will not be honored over plaintext HTTP.

def card_collection_post_request(
        identifiers: list,       # An array of JSON objects, each one a card identifier. 
        user_agent:  str,        # REQUIRED - must be accurate to your usage context
        accept:      str = '*/*' # REQUIRED - must be present, but you can provide a generic preference.
    ) -> tuple[list, list]:
    
    cards   = []
    missing = []

    url = f'{SCHEME}://{HOSTNAME}/cards/collection'
    headers = {
        'User-Agent'   : user_agent,
        'Accept'       : accept,
        'Content-Type' : 'application/json;charset=utf-8' # REQUIRED - /cards/collection requests must be posted with Content-Type as application/json.
    }

    print('Querying Scryfall... ')
    with requests.Session() as session:
        session.headers.update(headers)
        # A maximum of 75 card references may be submitted per /cards/collection request. Larger collections must be batched.
        for i in range(0, len(identifiers), BATCH_SIZE_MAX):
            print(f'Processing batch {i // BATCH_SIZE_MAX} ')
            payload = {
                'identifiers' : identifiers[i : i + BATCH_SIZE_MAX]
            }
            response = session.post(url, json=payload)
            response.raise_for_status()
            response_body = response.json()
            cards.extend(response_body['data'])
            missing.extend(response_body['not_found'])
            sleep(COOLDOWN_MIN) # Don't exceed the rate limit!!!
    print('Done! ')
    return cards, missing
