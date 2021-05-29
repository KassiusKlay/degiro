import streamlit as st
import concurrent.futures
from itertools import repeat
import degiroapi
import pandas as pd
from datetime import datetime
from currency_converter import CurrencyConverter


def process_splits_data(df):
    df = df.copy()
    splits = df.loc[df.transactionTypeId == 101].groupby('date')
    for split, split_df in splits:
        split_factor = (
                split_df.loc[split_df.buysell == 'S'].price.iloc[0]
                / split_df.loc[split_df.buysell == 'B'].price.iloc[0])
        df = df.price.where(
                ~(df.date < split_df.date.iloc[0]),
                other=(df.price / split_factor))
        df = df.quantity.where(
                ~(df.date < split_df.date.iloc[0]),
                other=(df.quantity * split_factor))
        df = df.merge(
                split_df,
                how='outer',
                indicator=True).loc[
                        lambda x: x['_merge'] == 'left_only'
                        ]
        df = df.drop(df.columns[-1], axis=1)
    return df


def get_general_data(realprice, transactions, info):
    name = info['name']
    currency = info['currency']
    c = CurrencyConverter()

    last_price = realprice[0]['data']['lastPrice']
    low52 = realprice[0]['data']['lowPriceP1Y']
    high52 = realprice[0]['data']['highPriceP1Y']
    from_high52 = (1 - high52 / last_price) * 100

    buy = transactions.loc[transactions.buysell == 'B']
    shares_buy = abs(buy.quantity.sum())
    total_buy = abs(buy.totalPlusFeeInBaseCurrency.sum())
    avg_buy = abs(buy.total.sum() / buy.quantity.sum())

    sell = transactions.loc[transactions.buysell == 'S']
    shares_sell = abs(sell.quantity.sum())
    total_sell = abs(sell.totalPlusFeeInBaseCurrency.sum())
    avg_sell = abs(sell.total.sum() / sell.quantity.sum())

    shares_owned = transactions.quantity.sum()
    flag = 0
    if currency == 'GBX':
        currency = 'GBP'
        flag = 1
    fx_rate = c.convert(1, currency)
    current_value = round(shares_owned * last_price * fx_rate, 2)
    if flag:
        current_value /= 100
    profit = round(((((
        current_value + total_sell) / total_buy) - 1) * 100), 2)

    df = pd.DataFrame([[
                name,
                last_price,
                low52,
                high52,
                from_high52,
                shares_buy,
                avg_buy,
                total_buy,
                shares_sell,
                avg_sell,
                total_sell,
                shares_owned,
                current_value,
                profit
                ]],
            columns=[
                'name',
                'lastPrice',
                'low52',
                'high52',
                'fromHigh52',
                'buyShares',
                'buyAverage',
                'buyCost',
                'sellShares',
                'sellAverage',
                'sellCost',
                'currentShares',
                'currentValue',
                'Profit'
                ])
    return df


def get_products_data(state, product):
    info = state.degiro.product_info(product['id'])
    transactions = state.transactions.loc[
            state.transactions.productId.astype(str) == product['id']]
    if transactions.empty:
        return None
    if any(transactions.transactionTypeId == 101):
        transactions = process_splits_data(transactions)
    return
    transactions = transactions.reset_index(drop=True)
    try:
        realprice = state.degiro.real_time_price(
            info['id'], degiroapi.Interval.Type.Max)
        general_data = get_general_data(
                realprice, transactions, info)
        historical_data = realprice[1]['data']
        historical_data = pd.DataFrame(
                historical_data, columns=['date', 'price'])
        historical_data.date = pd.to_datetime(
                historical_data.date.astype(int),
                unit='D',
                origin=realprice[0]['data']['windowStart'])
    except Exception:
        historical_data = general_data = None

    return {
            'id': product['id'],
            'name': info['name'],
            'currency': info['currency'],
            'transactions': transactions,
            'historical_data': historical_data,
            'general_data': general_data}


def get_transactions_data(state):
    df = pd.DataFrame(
            state.degiro.transactions(datetime(2010, 1, 1), datetime.now()))
    df.date = pd.to_datetime(
            df.date.astype(str), utc=True).dt.tz_convert('Europe/Copenhagen')
    df = process_replaced_products(df)
    return df


def get_account_data(state):
    df = pd.DataFrame.from_dict(state.degiro.account_overview(
        datetime(2010, 1, 1), datetime.now())['cashMovements'])
    df.date = pd.to_datetime(
            df.date.astype(str), utc=True).dt.tz_convert('Europe/Copenhagen')
    return df


def process_replaced_products(df):
    replaced_products_id = df.loc[
            (df.transactionTypeId == 106) & (df.buysell == 'S')
            ].id.unique().tolist()
    for i in replaced_products_id:
        to_replace = df.loc[df.id == i + 1].productId.iloc[0]
        df.productId.where(
                ~(df.productId == df.loc[df.id == i].iloc[0].productId),
                other=to_replace,
                inplace=True)
    return df.loc[df.transactionTypeId != 106].reset_index(drop=True)


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
        # state.products = []
        # for result in results:
            # state.products.append(result)
    st.write('OK')
    st.stop()
    state.products = list(filter(None, state.products))
