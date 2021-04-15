import re
import requests
import yfinance as yf
import pandas as pd
import streamlit as st
import altair as alt


def process_transactions_dataframe(df):
    df = df.drop(df.columns[[1, 5, 18]], axis=1)
    df.columns = [
            'Date',
            'Product',
            'ISIN',
            'Exchange',
            'Number',
            'Price',
            'Currency',
            'Cost (Exchange)',
            'Currency (Exchange)',
            'Cost (Local)',
            'Currency (Local)',
            'Exchange Rate',
            'Commission',
            'Currency (Comission)',
            'Total Cost',
            'Currency (Total)']
    df = df.dropna(how="all")
    df = df.dropna(subset=['Currency'])
    df.Date = pd.to_datetime(df.Date, format='%d-%m-%Y')
    return df


@st.cache
def get_ticker_from_ISIN(ISIN):
    url = 'https://api.openfigi.com/v1/mapping'
    headers = {'Content-Type': 'text/json', 'X-OPENFIGI-APIKEY': ''}
    payload = '[{"idType":"ID_ISIN","idValue":"' + ISIN + '"}]'
    r = requests.post(url, headers=headers, data=payload)
    pattern = re.compile(r'ticker":"(\w+)')
    ticker = re.search(pattern, r.text).groups()[0]
    return ticker


@st.cache
def check_valid_ticker_data(tickers, ticker):
    hist = tickers.tickers[ticker].history(period='max')
    if (
            not hist.empty
            and hist.Close.value_counts().max() < 30
            and len(hist) > 200
            and len(tickers.tickers[ticker].info) > 10
            and len(tickers.tickers[ticker].isin) > 10):
        return 1
    else:
        return 0


@st.cache
def get_ticker_list_data(ticker_list):
    dict_of_available_tickers = {}
    tickers = yf.Tickers(ticker_list)
    for ticker in tickers.tickers:
        if check_valid_ticker_data(tickers, ticker):
            valid_entry = {
                'Data':
                tickers.tickers[ticker].history(period='max').reset_index(),
                'ISIN': tickers.tickers[ticker].isin,
                'Splits': tickers.tickers[ticker].splits,
                'Dividends': tickers.tickers[ticker].dividends
                }
            dict_of_available_tickers[ticker] = valid_entry
    return dict_of_available_tickers


def plot_selected_stock_and_start_date(df, start_date, end_date):
    df = df.loc[
            (df.Date.dt.year >= start_date)
            & (df.Date.dt.year <= end_date)]
    chart = alt.Chart(df).mark_line().encode(
            alt.X('Date:T'),
            alt.Y('Close:Q', title='Price'))
    return chart
