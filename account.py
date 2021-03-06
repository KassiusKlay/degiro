import streamlit as st
import altair as alt
import pandas as pd
import degiroapi


def get_deposits_dataframe(df):
    df = df.copy()
    df = df.loc[
            df.description.str.contains('Dep|With')]
    df.description = df.description.where(
            ~df.description.str.contains('Dep'), 'Deposit')
    return df


def account_balance(state, df):
    state.account_balance = df.change.sum()
    state.local_currency = df.currency.value_counts().idxmax()
    st.write(f'**Net Account Balance (deposits - withdrawals):** \
            {state.account_balance} {state.local_currency}')


def account_value(state):
    portfolio = state.degiro.getdata(degiroapi.Data.Type.PORTFOLIO, True)
    state.account_value = sum(
            [stock['value']
                for stock in portfolio
                if stock['positionType'] == 'PRODUCT'])
    st.write(f'**Current Account Value:** {round(state.account_value, 2)} \
            {state.local_currency}')


def free_cash(state):
    cashfunds = state.degiro.getdata(degiroapi.Data.Type.CASHFUNDS)
    ammount = cashfunds[0].split()[1]
    currency = cashfunds[0].split()[0]
    st.write(f'**Current Free Cash:** {ammount} {currency}')


def last_movement(df):
    df.date = pd.to_datetime(df.date)
    latest_movement = df.iloc[0].change
    currency = df.currency.value_counts().idxmax()
    date = df.iloc[0].date.strftime('%d-%m-%y')
    type_of_movement = 'DEPOSIT' if df.iloc[0].change > 0 else 'WITHDRAWAL'
    st.write(f'**Last Movement ({date}):** {type_of_movement} \
            {latest_movement} {currency}')


def last_order(state):
    df = state.transactions.iloc[-1]
    date = df.date.strftime('%d-%m-%y')
    local_currency = state.account.loc[
            (state.account.orderId.notna()) &
            (state.account.change < 0)].iloc[0].currency
    exchange_currency = state.account.loc[
            (state.account.orderId.notna()) &
            (state.account.change > 0)].iloc[0].currency
    type_of_order = 'BUY' if df.buysell == 'B' else 'SELL'
    name = state.degiro.product_info(df.productId)['name']
    value = abs(df.totalInBaseCurrency) + abs(df.feeInBaseCurrency)
    st.write(f'**Last Order ({date}):** {type_of_order} {abs(df.quantity)} \
            shares of {name} for {round(value, 2)} {local_currency} \
            at {df.price} {exchange_currency} each')


def deposits_chart(df):
    chart = alt.Chart(df).mark_bar().encode(
            alt.Column('year(date):T', title='Year'),
            alt.Y('sum(change):Q', title='Ammount'),
            alt.X('description:O', title=None)).properties(width=alt.Step(50))
    st.altair_chart(chart)


def percentage(val):
    if val > 0:
        color = 'green'
    elif val < 0:
        color = 'red'
    else:
        color = 'black'
    return 'color: %s' % color


def general_data(state):
    df = pd.DataFrame()
    for product in state.products:
        df = pd.concat([df, product['general_data']])
    df = df.set_index('name')
    df = df.sort_values(by=['currentValue'], ascending=False)
    styler = df.style.applymap(
            percentage, subset=['change', 'fromHigh52', 'profit']).format(
                    {
                        'lastPrice': '{:,.2f}',
                        'change': '{:+.1%}',
                        'low52': '{:,.2f}',
                        'high52': '{:,.2f}',
                        'fromHigh52': '{:+.1%}',
                        'buyAverage': '{:,.2f}',
                        'buyCost': '{:,.2f}',
                        'sellAverage': '{:,.2f}',
                        'sellCost': '{:,.2f}',
                        'currentValue': '{:,.2f}',
                        'profit': '{:+.1%}'})
    st.write(styler)


def show(state):
    deposits_dataframe = get_deposits_dataframe(state.account)
    account_balance(state, deposits_dataframe)
    account_value(state)
    free_cash(state)
    last_movement(deposits_dataframe)
    last_order(state)
    options = ['General Portfolio Data', 'Account Movements']
    selection = st.radio('', options)
    if selection == 'Account Movements':
        deposits_chart(deposits_dataframe)
    else:
        general_data(state)
