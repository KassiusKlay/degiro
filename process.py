import streamlit as st
import concurrent.futures
from itertools import repeat
import degiroapi
import pandas as pd
from datetime import datetime
from currency_converter import CurrencyConverter


def get_general_data(realprice, transactions, historical_data, info):
    name = info['name']
    currency = info['currency']
    c = CurrencyConverter()

    if realprice:
        last_price = realprice[0]['data']['lastPrice']
        change = historical_data.price.pct_change().iloc[-1]
        low52 = realprice[0]['data']['lowPriceP1Y']
        high52 = realprice[0]['data']['highPriceP1Y']
        from_high52 = - (high52 - last_price) / high52
    else:
        last_price = info['closePrice']
        change = low52 = high52 = from_high52 = False

    buy = transactions.loc[transactions.buysell == 'B']
    shares_buy = abs(buy.quantity.sum())
    total_buy = abs(buy.totalPlusFeeInBaseCurrency.sum())
    avg_buy = abs(buy.total.sum() / buy.quantity.sum())

    sell = transactions.loc[transactions.buysell == 'S']
    if not sell.empty:
        shares_sell = abs(sell.quantity.sum())
        total_sell = abs(sell.totalPlusFeeInBaseCurrency.sum())
        avg_sell = abs(sell.total.sum() / sell.quantity.sum())
    else:
        shares_sell = total_sell = avg_sell = 0

    shares_owned = transactions.quantity.sum()
    flag = 0
    if currency == 'GBX':
        currency = 'GBP'
        flag = 1
    fx_rate = c.convert(1, currency)
    current_value = shares_owned * last_price * fx_rate
    if flag:
        current_value /= 100
    profit = ((current_value + total_sell) / total_buy) - 1

    df = pd.DataFrame([[
                name,
                last_price,
                change,
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
                'change',
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
                'profit'
                ])
    return df


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


def get_info_and_real_price(state, product):
    info = state.degiro.product_info(product['id'])
    try:
        realprice = state.degiro.real_time_price(
            info['id'], degiroapi.Interval.Type.Max)
    except Exception:
        realprice = None
    else:
        if 'error' in realprice[0].keys():
            realprice = None
    return [info, realprice]


def process_splits_data(df):
    df = df.copy()
    splits = df.loc[df.transactionTypeId == 101].groupby('date')
    for split, split_df in splits:
        split_factor = (
                split_df.loc[split_df.buysell == 'S'].price.iloc[0]
                / split_df.loc[split_df.buysell == 'B'].price.iloc[0])
        df.price = df.price.where(
                ~(df.date < split_df.date.iloc[0]),
                other=(df.price / split_factor))
        df.quantity = df.quantity.where(
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


def get_returns_data(transactions, historical_data):
    df = historical_data.loc[
            historical_data.date.dt.date >= transactions.date.min()]
    daily_returns = df.price.pct_change().iloc[1:]
    cum_daily_returns = (1 + daily_returns).cumprod() - 1
    cum_daily_returns.name = 'returns'
    returns = pd.concat([df.date, cum_daily_returns], axis=1)
    return returns


def get_products_data(df, info_real_price):
    info = info_real_price[0]
    realprice = info_real_price[1]
    transactions = df.loc[
            df.productId.astype(str) == info['id']]
    if any(transactions.transactionTypeId == 101):
        transactions = process_splits_data(transactions)
    transactions = transactions.reset_index(drop=True)

    if realprice:
        historical_data = realprice[1]['data']
        historical_data = pd.DataFrame(
                historical_data, columns=['date', 'price'])
        historical_data.date = pd.to_datetime(
                historical_data.date.astype(int),
                unit='D',
                origin=realprice[0]['data']['windowStart'])
        if info['name'] == 'Tesla':
            historical_data = historical_data.iloc[2:]
        returns = get_returns_data(transactions, historical_data)
    else:
        historical_data = returns = None

    general_data = get_general_data(
            realprice, transactions, historical_data, info)

    return {
            'id': info['id'],
            'name': info['name'],
            'currency': info['currency'],
            'transactions': transactions,
            'historical_data': historical_data,
            'returns': returns,
            'general_data': general_data}


def get_data(state):
    placeholder = st.empty()
    placeholder.warning('Processing Data... Please Wait')
    portfolio = state.degiro.getdata(degiroapi.Data.Type.PORTFOLIO)
    if state.info is None:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future1 = executor.submit(get_transactions_data, state)
            state.transactions = future1.result()

            future2 = executor.submit(get_account_data, state)
            state.account = future2.result()
            unique = state.transactions.productId.unique().tolist()
            product_list = [
                    product for product in portfolio
                    if product['positionType'] == 'PRODUCT'
                    if int(product['id']) in unique]

            state.info = list(executor.map(
                    get_info_and_real_price, repeat(state), product_list))
    else:
        with concurrent.futures.ProcessPoolExecutor() as executor:
            state.products = list(executor.map(
                    get_products_data,
                    repeat(state.transactions), state.info))
        placeholder.empty()
