import matplotlib.pyplot as plt
import pandas as pd
from math import ceil
from matplotlib.ticker import StrMethodFormatter
from pathlib import Path

def main() -> None:
    PROJECT_DIRECTORY  = Path(__file__).resolve().parent
    PRICE_HISTORY_PATH = Path(PROJECT_DIRECTORY, 'data',    'price_history.csv')
    COLLECTION_PATH    = Path(PROJECT_DIRECTORY, 'data',    'collection.csv')
    CHART_PATH         = Path(PROJECT_DIRECTORY, 'charts')

    MAX_X_TICKS = 10

    ILLEGAL_FILENAME_CHARACTERS = ':/'

    price_history_df = pd.read_csv(PRICE_HISTORY_PATH)
    price_history_df['id2'] = price_history_df.id + '-' + price_history_df.foil.astype(str) + '-' + price_history_df.etched.astype(str)

    collection_df = pd.read_csv(COLLECTION_PATH)
    collection_df['id2'] = collection_df.id + '-' + collection_df.foil.astype(str) + '-' + collection_df.etched.astype(str)
    collection_df.drop(columns=['id', 'url', 'foil', 'etched'], inplace=True)

    df = price_history_df.merge(collection_df, how='left', on='id2')
    df = df[df.quantity > 0]
    df.sort_values('date', inplace=True)

    latest_prices_df = df.loc[df.groupby('id2')['date'].idxmax()].sort_values('price', ascending=False).reset_index(drop=True)

    table = str.maketrans(ILLEGAL_FILENAME_CHARACTERS, '_' * len(ILLEGAL_FILENAME_CHARACTERS))

    for id in latest_prices_df[latest_prices_df.price > 5]['id2']:
        card_df = df[df.id2 == id]

        chart_title = ''
        if card_df.iloc[0]['foil']   == 1: chart_title = f'{chart_title}Foil '
        if card_df.iloc[0]['etched'] == 1: chart_title = f'{chart_title}Etched'
        chart_title = f'{chart_title}{card_df.iloc[0]["name"]} -- {card_df.iloc[0]["set_name"]}'

        num_dates   = len(card_df)
        x_tick_step = ceil(num_dates / MAX_X_TICKS)
        date_ticks  = card_df.iloc[range(num_dates - 1, -1, -x_tick_step)].date[::-1]

        fig, ax = plt.subplots()
        ax.plot(card_df.date, card_df.price)
        ax.set_title(chart_title)
        ax.set_xticks(date_ticks)
        ax.set_xticklabels(date_ticks, rotation=45, ha='right')
        ax.yaxis.set_major_formatter(StrMethodFormatter('${x:,.2f}'))
        ax.grid(True)

        fig.tight_layout()
        fig.savefig(Path(CHART_PATH, chart_title.translate(table)))
        plt.close()

if __name__ == '__main__':
    main()