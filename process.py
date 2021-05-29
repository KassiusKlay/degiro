import streamlit as st
import concurrent.futures
import time
from itertools import repeat
import degiroapi
import pandas as pd
from datetime import datetime, timedelta


def process_splits_data(df):
    splits = df.loc[df.transactionTypeId == 101].groupby('date')
    for split, split_df in splits:
        split_factor = (
                split_df.loc[split_df.buysell == 'S'].price.iloc[0]
                / split_df.loc[split_df.buysell == 'B'].price.iloc[0])
        df.price.where(
                ~(df.date < split_df.date.iloc[0]),
                other=(df.price / split_factor),
                inplace=True)
        df = df.merge(
                split_df,
                how='outer',
                indicator=True).loc[
                        lambda x: x['_merge'] == 'left_only'
                        ]
        df.drop(df.columns[-1], axis=1, inplace=True)
        return df


def get_transactions_data(state):
    df = pd.DataFrame(
            state.degiro.transactions(datetime(2010, 1, 1), datetime.now()))
    df.date = pd.to_datetime(
            df.date.astype(str), utc=True).dt.tz_convert('Europe/Copenhagen')
    return df


def get_account_data(state):
    df = pd.DataFrame.from_dict(state.degiro.account_overview(
        datetime(2010, 1, 1), datetime.now())['cashMovements'])
    df.date = pd.to_datetime(
            df.date.astype(str), utc=True).dt.tz_convert('Europe/Copenhagen')
    return df


def get_products_data(state, product):
    info = state.degiro.product_info(product['id'])
    transactions = state.transactions.loc[
            state.transactions.productId.astype(str) == product['id']]
    if any(transactions.transactionTypeId == 101):
        transactions = process_splits_data(transactions)
    transactions = transactions.reset_index(drop=True)
    try:
        realprice = state.degiro.real_time_price(
            info['id'], degiroapi.Interval.Type.Max)
        last_price = realprice[0]['data']['lastPrice']
        low52 = realprice[0]['data']['lowPriceP1Y']
        high52 = realprice[0]['data']['highPriceP1Y']
        historical_data = realprice[1]['data']
        historical_data = pd.DataFrame(
                historical_data, columns=['date', 'price'])
        historical_data.date = pd.to_datetime(
                historical_data.date.astype(int),
                unit='D',
                origin=realprice[0]['data']['windowStart'])
    except Exception:
        last_price = low52 = high52 = historical_data = None

    return {
            'id': product['id'],
            'name': info['name'],
            'transactions': transactions,
            'historical_data': historical_data,
            'last_price': last_price,
            'low52': low52,
            'high52': high52}


def get_data(state):
    st.warning('Processing Data... Please Wait')
    portfolio = state.degiro.getdata(degiroapi.Data.Type.PORTFOLIO)
    product_list = [
            product for product in portfolio
            if product['positionType'] == 'PRODUCT']

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future1 = executor.submit(get_transactions_data, state)
        state.transactions = future1.result()

        future2 = executor.submit(get_account_data, state)
        state.account = future2.result()

        results = executor.map(
                get_products_data, repeat(state), product_list)
        state.products = []
        for result in results:
            state.products.append(result)
