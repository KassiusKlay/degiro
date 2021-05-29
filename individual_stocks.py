import streamlit as st
import altair as alt
import pandas as pd
import datetime
import degiroapi


def plot_stocks(state, list_of_stocks):
    for stock in list_of_stocks:
        i = [i for i, _ in enumerate(state.products) if _['name'] == stock][0]
        product_id = state.products[i]['id']
        name = state.products[i]['name']
        transactions = state.products[i]['transactions'].copy()
        historical_data = state.products[i]['historical_data']
        last_price = state.products[i]['last_price']
        low52 = state.products[i]['low52']
        high52 = state.products[i]['high52']

        from_52high = round((1 - high52 / last_price) * 100, 2)
        st.write(from_52high)

        st.write(f' ## {name}')
        st.write(transactions)

        transactions.totalPlusFeeInBaseCurrency = (
                transactions.totalPlusFeeInBaseCurrency.abs())
        if historical_data is None:
            st.warning('Couldn\'t get historical data')
        else:
            st.write(
                    'Last Price: ',  last_price, ' Low52: ', low52,
                    ' High52: ', high52)
            line = alt.Chart(historical_data).mark_line().encode(
                x='date:T', y='price:Q')
            circle = alt.Chart(transactions).mark_circle().encode(
                    x=alt.X('date:T', title='Date'),
                    y=alt.Y('price:Q', title='Price'),
                    size=alt.Size(
                        'totalPlusFeeInBaseCurrency',
                        legend=None),
                    tooltip=['quantity', 'totalPlusFeeInBaseCurrency'],
                    color=alt.Color(
                        'buysell',
                        legend=alt.Legend(title='Buy/Sell'),
                        scale=alt.Scale(scheme='dark2')
                        )).interactive()

            st.altair_chart(line + circle, use_container_width=True)


def show(state):
    option = st.radio('', ['Select Stocks', 'All'])
    list_of_stocks = sorted(
            [product['name'] for product in state.products])
    if option == 'All':
        plot_stocks(state, list_of_stocks)
    else:
        selection = st.multiselect('', list_of_stocks)
        plot_stocks(state, selection)
