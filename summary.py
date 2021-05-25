import streamlit as st


@st.cache
def percentage(val):
    if val > 0:
        color = 'green'
    elif val < 0:
        color = 'red'
    else:
        color = 'black'
    return 'color: %s' % color


def get_summary_data(general_data):
    portfolio = general_data[[
        'Ticker',
        'Total BUY',
        'Total SELL',
        'SELL %',
        'Current Value',
        'Value %']].sort_values(by='Current Value', ascending=False)

    portfolio_total_buy = portfolio['Total BUY'].sum()
    portfolio_total_sell = portfolio['Total SELL'].sum()
    portfolio_total_buy_from_sell = portfolio.loc[
            portfolio['Total SELL'].notnull()]['Total BUY'].sum()
    portfolio_sell_percentage = (
            portfolio_total_buy_from_sell - portfolio_total_sell
            ) / portfolio_total_sell
    portfolio_value_percentage = (
            portfolio['Current Value'].sum() - portfolio_total_buy
            - portfolio_total_sell) / (
                    portfolio_total_buy - portfolio_total_sell)
    total_row = {
            'Ticker': 'TOTAL',
            'Total BUY': portfolio_total_buy,
            'Total SELL': portfolio_total_sell,
            'SELL %': portfolio_sell_percentage,
            'Current Value': portfolio['Current Value'].sum(),
            'Value %': portfolio_value_percentage}

    portfolio = portfolio.append(total_row, ignore_index=True)

    portfolio = portfolio.style.applymap(
            percentage, subset=['SELL %', 'Value %']).format(
                    {
                        'Total BUY': '{:,.0f} EUR',
                        'Total SELL': '{:,.0f} EUR',
                        'Current Value': '{:,.0f} EUR',
                        'SELL %': '{:+.0%}',
                        'Value %': '{:+.0%}'}, na_rep='-')

    st.write(portfolio)


def show(state):
    st.write(' ## Processed Account')
    st.write(state.processed_account)
    st.write(' ## Processed Transactions')
    st.write(state.processed_transactions)
