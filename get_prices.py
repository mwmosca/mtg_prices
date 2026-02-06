import csv
from datetime import datetime
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from os import getenv
from pathlib import Path
from scryfall_utils import card_collection_post_request

def main() -> None:
    load_dotenv()

    TODAY = datetime.now().strftime('%Y-%m-%d')

    PROJECT_DIRECTORY        = Path(__file__).resolve().parent
    COLLECTION_PATH          = Path(PROJECT_DIRECTORY, 'data',    'collection.csv')
    PRICE_REPORT_PATH        = Path(PROJECT_DIRECTORY, 'reports', 'price_report.csv')
    PRICE_HISTORY_PATH       = Path(PROJECT_DIRECTORY, 'data',    'price_history.csv')
    MISSING_CARD_REPORT_PATH = Path(PROJECT_DIRECTORY, 'reports', 'missing_card_report.csv')

    USER_AGENT = getenv('USER_AGENT') # REQUIRED - must be accurate to your usage context
    ACCEPT     = 'application/json'   # REQUIRED - must be present, but you can provide a generic preference.

    collection        = []   # A list of my cards.
    identifiers       = []   # A list of dictionaries containing card properties. It is used to query Scryfall.
    IDENTIFIER_SCHEMA = 'id' # Finds a card with the specified Scryfall ID (UUID format).

    card_prices = {} # A dictionary of card prices from Scryfall using the Scryfall IDs as keys.
    missing     = [] # A list of identifiers that failed to return a card from Scryfall.

    # Google Sheets information
    SCOPES               = ['https://www.googleapis.com/auth/spreadsheets']                       # Limits the access token to only Google Sheets
    SERVICE_ACCOUNT_FILE = Path(PROJECT_DIRECTORY, 'credentials', getenv('SERVICE_ACCOUNT_FILE')) # Contains credentials to access Google APIs
    SPREADSHEET_ID       = getenv('SPREADSHEET_ID')                                               # The ID of our Expeditions Google Sheet
    TARGET_SHEET_NAME    = getenv('TARGET_SHEET_NAME')                                            # The tab that will be edited

    # Import my collection. **************************************************************************************
    with open(COLLECTION_PATH, 'r', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            collection.append(row)
            identifiers.append({IDENTIFIER_SCHEMA : row[IDENTIFIER_SCHEMA]})

    # Query Scryfall *********************************************************************************************
    cards, missing = card_collection_post_request(identifiers, USER_AGENT, ACCEPT)
    card_prices.update({c['id']: c['prices'] for c in cards})

    # Assign prices to the collection. ***************************************************************************
    for c in collection:
        if   c['foil']   == '1': p = 'usd_foil'
        elif c['etched'] == '1': p = 'usd_etched'
        else:                    p = 'usd'
        c['price'] = card_prices[c['id']][p]

    # Update the price history. **********************************************************************************
    # Get a set of dates already present in the price history.
    dates = set()
    with open(PRICE_HISTORY_PATH, mode='r', newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f): dates.add(row['date'])
    # Update the price history only if today's date is not already present in the history.
    if TODAY not in dates: 
        with open(PRICE_HISTORY_PATH, mode='a', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=['id', 'foil', 'etched', 'price', 'date'], extrasaction='ignore')
            for c in collection:
                temp = dict(c) # Create a shallow copy to avoid modifying the collection list.
                temp['date'] = TODAY
                w.writerow(temp)
    else:
        input(f'Prices for {TODAY} have already been recorded.')

    # Write local reports ****************************************************************************************
    # Filter out cards that I don't own.
    collection = [c for c in collection if c['quantity'] != '0']
    
    ignore_keys = ['id']
    headers     = [k for k in collection[0] if k not in ignore_keys]

    with open(PRICE_REPORT_PATH, mode='w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=headers, extrasaction='ignore')
        w.writeheader()
        w.writerows(collection)

    with open(MISSING_CARD_REPORT_PATH, mode='w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=[IDENTIFIER_SCHEMA])
        w.writeheader()
        w.writerows(missing)

    # Update the Google Sheet ************************************************************************************
    # Authenticate the Google Sheets API interaction. 
    creds   = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)

    # Clear any outdated price data from the sheet. 
    print(service.spreadsheets().values().clear(
        spreadsheetId = SPREADSHEET_ID,
        range         = TARGET_SHEET_NAME,
        body          = {} # The body parameter is required, but empty.
    ).execute())
    
    # Upload the new price data. 
    starting_cell = f'{TARGET_SHEET_NAME}!A1'
    rows = [[c[h] for h in headers] for c in collection]
    body = {
        'values' : [headers] + rows
    }
    print(service.spreadsheets().values().update(
        spreadsheetId    = SPREADSHEET_ID,
        range            = starting_cell,
        valueInputOption = 'USER_ENTERED', # Unlike RAW, USER_ENTERED auto-parses numbers. 
        body             = body
    ).execute())

if __name__ == '__main__':
    main()
