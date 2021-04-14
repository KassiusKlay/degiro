import yfinance as yf
import streamlit as st
import pandas as pd
import altair as alt
from account import process_account_dataframe, get_deposits_dataframe, get_total_deposits
from transactions import process_transactions_dataframe, get_ticker_from_ISIN, check_valid_ticker_data, get_ticker_list_data, plot_selected_stock_and_start_date
from utils import check_uploaded_files, load_data, show_formatted_dataframe
import SessionState

session_state = SessionState.get(button='', yfinance='')


st.title("Degiro Interactive Analyser")
placeholder = st.empty()
uploaded_files = st.sidebar.file_uploader("", type='.csv', accept_multiple_files=True)

if  not check_uploaded_files(uploaded_files):
    placeholder.markdown("Please upload the **Account.csv** and **Transaction.csv** files from Degiro. Instructions [here](https://www.github.com)")
    st.warning("Please upload the correct files")
    st.stop()
placeholder.empty()

account_dataframe = load_data(sorted(uploaded_files, key=lambda x: x.name)[0])
account_dataframe = process_account_dataframe(account_dataframe)
transactions_dataframe = load_data(sorted(uploaded_files, key=lambda x: x.name)[1])
transactions_dataframe = process_transactions_dataframe(transactions_dataframe)
show_formatted_dataframe(account_dataframe)

st.write("## Deposits / Withdrawls")

deposits_dataframe = get_deposits_dataframe(account_dataframe)
total_deposits = get_total_deposits(deposits_dataframe)
st.markdown("Net Account Movements (for the selected period): **%s**" %total_deposits)

deposits_chart = alt.Chart(deposits_dataframe).mark_bar().encode(
        alt.Column('year(Date):T', title='Year'),
        alt.Y('sum(Movement):Q', title='Deposits'),
        alt.X('Description:O', title=None)).properties(width=alt.Step(50))
st.altair_chart(deposits_chart)

st.write("---")
st.write("## Stocks in Portfolio")

ticker_list = []
for ISIN in transactions_dataframe.ISIN.unique():
    ticker_list.append(get_ticker_from_ISIN(ISIN))

dict_of_available_tickers = get_ticker_list_data(ticker_list)
rejected_tickers = ticker_list - dict_of_available_tickers.keys()

if not session_state.button:
    st.markdown("""Error fetching data from the follwing products:\n
     - %s""" %(" ".join(rejected_tickers)))
    if st.button("Click to Continue"):
        session_state.button = True
    st.stop()

for ticker, value in dict_of_available_tickers.items():
    if not value['Splits'].empty:
        for i in value['Splits'].index:
            transactions_dataframe.Number.loc[(transactions_dataframe.Date.dt.date < i.date()) & (transactions_dataframe.ISIN == value['ISIN'])] = transactions_dataframe.Number.loc[(transactions_dataframe.Date.dt.date < i.date()) & (transactions_dataframe.ISIN == value['ISIN'])] * value['Splits'].loc[i]
            transactions_dataframe.Price.loc[(transactions_dataframe.Date.dt.date < i.date()) & (transactions_dataframe.ISIN == value['ISIN'])] = transactions_dataframe.Price.loc[(transactions_dataframe.Date.dt.date < i.date()) & (transactions_dataframe.ISIN == value['ISIN'])] / value['Splits'].loc[i]
transactions_dataframe =  transactions_dataframe.dropna(subset=['Commission'])

stock_selection = st.multiselect("Select stocks", list(dict_of_available_tickers.keys()))
for stock in stock_selection[::-1]:
    st.write("**%s**" %stock)
    start_date = st.slider("Select start date", key=stock, min_value=dict_of_available_tickers[stock]['Data'].Date.min().year, max_value=dict_of_available_tickers[stock]['Data'].Date.max().year)
    end_date = st.slider("Select end date", key=stock, min_value=dict_of_available_tickers[stock]['Data'].Date.min().year, max_value=dict_of_available_tickers[stock]['Data'].Date.max().year, value=dict_of_available_tickers[stock]['Data'].Date.max().year)
    if (start_date > end_date):
        st.warning("Start Date > End Date")
        st.stop()
    chart = plot_selected_stock_and_start_date(dict_of_available_tickers[stock]['Data'], start_date, end_date)
    just_the_stock_dataframe = transactions_dataframe.loc[(transactions_dataframe.Date.dt.year >= start_date) & (transactions_dataframe.Date.dt.year <= end_date) & (transactions_dataframe.ISIN == dict_of_available_tickers[stock]['ISIN'])]
    cross = alt.Chart(just_the_stock_dataframe).mark_circle().encode(
            x='Date:T',
            y='Price:Q', size='Price:Q', tooltip=['Number', 'Total Cost']).interactive()

    combo = chart + cross

    st.altair_chart(combo, use_container_width=True)

