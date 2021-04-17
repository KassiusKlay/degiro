import re
import requests
import yfinance as yf
import pandas as pd
import streamlit as st


@st.cache
def check_uploaded_files(uploaded_files):
    list_of_uploaded_files = [file.name for file in uploaded_files]
    required_files = ['Account.csv', 'Transactions.csv']
    if not set(list_of_uploaded_files) ^ set(required_files):
        return True


@st.cache
def load_data(filename):
    df = pd.read_csv(filename)
    return df


def show_formatted_dataframe(df):
    st.dataframe(
            df.style.format(
                {'Date': lambda t: t.strftime('%d-%m-%Y')}).set_precision(2))


@st.cache
def process_account_dataframe(df):
    df = df.drop(df.columns[[1, 2, 4, 6, 9, 11]], axis=1)
    df.columns = [
            'Date',
            'Product',
            'Description',
            'Currency',
            'Movement',
            'Balance']
    df = df.dropna(how="all")
    df = df.dropna(subset=['Currency'])
    df['Movement'] = df['Movement'].str.replace(
            ',',
            '.',
            regex=True).astype(float)
    df['Balance'] = df['Balance'].str.replace(
            ',',
            '.',
            regex=True).astype(float)
    df.Date = pd.to_datetime(df.Date, format='%d-%m-%Y', utc=True)
    return df


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


def merge_historical_data_with_transactions(
        dict_of_available_tickers,
        transactions_dataframe):
    merged_data = pd.DataFrame()
    for ticker in dict_of_available_tickers.keys():
        df = transactions_dataframe.loc[
            (transactions_dataframe.ISIN
                == dict_of_available_tickers[ticker]['ISIN'])]
        data = dict_of_available_tickers[ticker]['Data'].copy()
        data.drop(
                ['High', 'Low', 'Open', 'Volume', 'Dividends', 'Stock Splits'],
                axis=1,
                inplace=True)
        data = data.loc[data.Date.dt.date >= df.Date.min()]
        data = pd.merge(
                data,
                df[['Date', 'Number', 'Price', 'Total Cost']], how='outer')
        data.Number.fillna(0, inplace=True)
        data.Number = data.Number.cumsum()
        data['Ticker'] = ticker
        merged_data = pd.concat(
                [merged_data, data])
    return merged_data


@st.cache
def process_splits_data(dict_of_available_tickers, transactions_dataframe):
    for ticker, value in dict_of_available_tickers.items():
        if not value['Splits'].empty:
            for i in value['Splits'].index:
                transactions_dataframe.Number.loc[
                    (transactions_dataframe.Date.dt.date <= i.date())
                    & (transactions_dataframe.ISIN
                        == value['ISIN'])] = transactions_dataframe.Number.loc[
                    (transactions_dataframe.Date.dt.date <= i.date())
                    & (transactions_dataframe.ISIN
                        == value['ISIN'])] * value['Splits'].loc[i]
                transactions_dataframe.Price.loc[
                    (transactions_dataframe.Date.dt.date <= i.date())
                    & (transactions_dataframe.ISIN
                        == value['ISIN'])] = transactions_dataframe.Price.loc[
                    (transactions_dataframe.Date.dt.date <= i.date())
                    & (transactions_dataframe.ISIN
                        == value['ISIN'])] / value['Splits'].loc[i]
                transactions_dataframe = transactions_dataframe[
                    (transactions_dataframe.Date.dt.date != i.date())
                    | (transactions_dataframe.ISIN != value['ISIN'])
                    | (transactions_dataframe.Currency.isnull())]
    return transactions_dataframe
