import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path

PROJECT_DIRECTORY  = Path(__file__).resolve().parent
PRICE_HISTORY_PATH = Path(PROJECT_DIRECTORY, 'data', 'price_history.csv')

df = pd.read_csv(PRICE_HISTORY_PATH, parse_dates=['date'])

st.title('My Dashboard')
card = st.selectbox('Select a card', df['id'].unique())

sub = df[df['id'] == card].sort_values('date')
fig = px.line(sub, x='date', y='price', title=f'{card} price')
st.plotly_chart(fig, use_container_width=True)
