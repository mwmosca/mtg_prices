import csv
from dotenv import load_dotenv
from os import getenv
from pathlib import Path
from scryfall_utils import card_collection_post_request, modify_card_name

def main() -> None:
    load_dotenv()

    PROJECT_DIRECTORY = Path(__file__).resolve().parent

    USER_AGENT = getenv('USER_AGENT') # REQUIRED - must be accurate to your usage context
    ACCEPT     = 'application/json'   # REQUIRED - must be present, but you can provide a generic preference.

    cards   = [] # A list cards from Scryfall.
    missing = [] # A list of identifiers that failed to return a card from Scryfall.

    # Import the identifiers for querying the new cards. *****************************************
    with open(Path(PROJECT_DIRECTORY, 'data', 'cards.csv'), 'r', encoding='utf-8-sig') as f:
        r = csv.DictReader(f)
        missing_card_fieldnames = r.fieldnames # This will be used later when writing the missing cards report.
        identifiers = [{k: v for k, v in row.items() if v != ''} for row in r] # Filter out unused identifiers.
        
    # Query Scryfall *****************************************************************
    cards, missing = card_collection_post_request(identifiers, USER_AGENT, ACCEPT)

    # Modify the card name to be more descriptive to the human eye. **************************
    for c in cards:
        c['name_'] = modify_card_name(c)

    # Write local reports ********************************************************************************************************
    with open(Path(PROJECT_DIRECTORY, 'reports', 'card_report.csv'), mode='w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=['id', 'name_', 'set_name', 'collector_number', 'uri'], extrasaction='ignore')
        w.writeheader()
        w.writerows(cards)
        
    with open(Path(PROJECT_DIRECTORY, 'reports', 'missing_card_report.csv'), mode='w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=missing_card_fieldnames)
        w.writeheader()
        w.writerows(missing)

if __name__ == '__main__':
    main()
