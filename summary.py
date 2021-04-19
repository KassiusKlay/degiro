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

    portfolio = portfolio.style.applymap(
            percentage, subset=['SELL %', 'Value %']).format(
                    {
                        'Total BUY': '{:.0f} EUR',
                        'Total SELL': '{:.0f} EUR',
                        'Current Value': '{:.0f} EUR',
                        'SELL %': '{:+.0%}',
                        'Value %': '{:+.0%}'}, na_rep='-')

    return portfolio
