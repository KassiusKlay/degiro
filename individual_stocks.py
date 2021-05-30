import streamlit as st
import altair as alt


def percentage(val):
    if val > 0:
        color = 'green'
    elif val < 0:
        color = 'red'
    else:
        color = 'black'
    return 'color: %s' % color


def show_general_data(df):
    df = df.set_index('name')
    df = df.style.applymap(
            percentage, subset=['fromHigh52', 'profit']).format(
                    {
                        'lastPrice': '{:,.0f}',
                        'low52': '{:,.0f}',
                        'high52': '{:,.0f}',
                        'fromHigh52': '{:+.1%}',
                        'buyAverage': '{:,.0f}',
                        'buyCost': '{:,.0f}',
                        'sellAverage': '{:,.0f}',
                        'sellCost': '{:,.0f}',
                        'currentValue': '{:,.0f}',
                        'profit': '{:+.1%}'})
    st.dataframe(df)


def plot_stocks(state, list_of_stocks):
    for stock in list_of_stocks:
        i = [i for i, _ in enumerate(state.products) if _['name'] == stock][0]
        name = state.products[i]['name']
        transactions = state.products[i]['transactions'].copy()
        historical_data = state.products[i]['historical_data']
        general_data = state.products[i]['general_data']

        st.write(f'## {name}')
        st.write('### General Data')
        show_general_data(general_data)
        st.write('### Transactions')
        st.write(transactions)
        st.write('### Historical Data')

        if historical_data is None:
            st.warning('Couldn\'t get historical data')
        else:
            transactions.totalPlusFeeInBaseCurrency = (
                    transactions.totalPlusFeeInBaseCurrency.abs())
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
