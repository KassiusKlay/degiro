import numpy as np
import re
import requests
import yfinance as yf
import pandas as pd
import streamlit as st
from forex_python.converter import CurrencyRates


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
            'Shares',
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


@st.cache(suppress_st_warning=True)
def get_ticker_list_data(ticker_list):
    bar = st.empty()
    progress_bar = bar.progress(0)
    steps = int(round((100 / len(ticker_list)), 0))
    progress = 0
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
        progress_bar.progress(progress)
        progress += steps
    bar.empty()
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
                df[['Date', 'Shares', 'Price', 'Total Cost']], how='outer')
        data.Shares.fillna(0, inplace=True)
        data.Shares = data.Shares.cumsum()
        data['Ticker'] = ticker
        merged_data = pd.concat(
                [merged_data, data])
    return merged_data


@st.cache
def process_splits_data(dict_of_available_tickers, transactions_dataframe):
    for ticker, value in dict_of_available_tickers.items():
        if not value['Splits'].empty:
            for i in value['Splits'].index:
                transactions_dataframe.Shares.loc[
                    (transactions_dataframe.Date.dt.date <= i.date())
                    & (transactions_dataframe.ISIN
                        == value['ISIN'])] = transactions_dataframe.Shares.loc[
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


@st.cache
def get_general_data(dict_of_available_tickers, transactions_dataframe):
    c = CurrencyRates()
    general_data = pd.DataFrame(columns=[
        'Ticker',
        'Shares BUY',
        'BUY price',
        'Total BUY',
        'Shares SELL',
        'SELL price',
        'SELL %',
        'Total SELL',
        'Current price',
        'Current %',
        'Current Value',
        'Value %'])

    for ticker in dict_of_available_tickers.keys():
        ticker_transactions = transactions_dataframe.loc[
                transactions_dataframe.ISIN
                == dict_of_available_tickers[ticker]['ISIN']]
        buy = ticker_transactions.loc[ticker_transactions.Shares > 0]
        sell = ticker_transactions.loc[ticker_transactions.Shares < 0]

        currency_exchange = buy.Currency.unique()[0]
        currency_local = buy['Currency (Local)'].unique()[0]

        shares_buy = buy.Shares.sum()
        average_buy_price = buy[
                'Cost (Exchange)'
                ].sum() * -1 / buy.Shares.sum()
        total_buy = buy['Cost (Local)'].sum() * -1

        current_price = dict_of_available_tickers[
                ticker]['Data']['Close'].iloc[-1]
        percentage_current = (
                current_price - average_buy_price) / average_buy_price

        shares_owned = ticker_transactions.Shares.sum()
        current_exchange_rate = c.get_rate(
                currency_exchange, currency_local)
        current_value = shares_owned * (
                current_price * current_exchange_rate)
        percentage_value = (current_value - total_buy) / total_buy

        if not sell.empty:
            total_sell = sell['Total Cost'].sum()
            tmp = sell['Shares'] * sell['Price']
            average_sell_price = tmp.sum() / sell['Shares'].sum()
            percentage_sell = (
                    average_sell_price - average_buy_price) / average_buy_price
            shares_sell = shares_buy - shares_owned

        new_row = {
                'Ticker': ticker,
                'Shares BUY': shares_buy,
                'BUY price': average_buy_price,
                'Total BUY': total_buy,
                'Shares SELL': np.nan if sell.empty else shares_sell,
                'SELL price': np.nan if sell.empty else average_sell_price,
                'SELL %': np.nan if sell.empty else percentage_sell,
                'Total SELL': np.nan if sell.empty else total_sell,
                'Current price': current_price,
                'Current %': percentage_current,
                'Current Value': current_value if sell.empty else np.nan,
                'Value %': percentage_value if sell.empty else np.nan}

        general_data = general_data.append(new_row, ignore_index=True)

    return general_data


def check_user_exists(db, user):
    user_ref = db.collection('degiro').document(user)
    if user_ref.get().exists:
        return 1
    return 0


def check_same_password(password, user_password):
    if password == user_password:
        return 1
    else:
        return 0


def check_valid_credentials(db, user, password):
    if not check_user_exists(db, user):
        return 0
    user_ref = db.collection('degiro').document(user)
    user_data = user_ref.get().to_dict()
    user_password = user_data['password']
    if not check_same_password(password, user_password):
        return 0
    return 1
