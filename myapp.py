from individual_stocks import individual_stocks_graphs
from returns import combined_returns_line_graph, owned_sold_returns_bar_graph
from account import account_balance_graph
import streamlit as st
import SessionState
import utils

session_state = SessionState.get(button='')

st.title("Degiro Interactive Dashboard")
placeholder = st.empty()
uploaded_files = st.sidebar.file_uploader(
        "", type='.csv', accept_multiple_files=True)

if not utils.check_uploaded_files(uploaded_files):
    placeholder.markdown(
        """
        Please upload the **Account.csv** and **Transaction.csv**
        files from Degiro.
        Instructions [here](https://www.github.com)
        """)
    st.warning("Please upload the correct files")
    st.stop()
placeholder.empty()

account_dataframe = utils.load_data(
        sorted(uploaded_files, key=lambda x: x.name)[0])
account_dataframe = utils.process_account_dataframe(account_dataframe)
transactions_dataframe = utils.load_data(
        sorted(uploaded_files, key=lambda x: x.name)[1])
transactions_dataframe = utils.process_transactions_dataframe(
        transactions_dataframe)

ticker_list = []
for ISIN in transactions_dataframe.ISIN.unique():
    ticker_list.append(utils.get_ticker_from_ISIN(ISIN))

dict_of_available_tickers = utils.get_ticker_list_data(ticker_list)
rejected_tickers = ticker_list - dict_of_available_tickers.keys()

if not session_state.button:
    st.markdown("""Error fetching data from the follwing products:\n
     - %s""" % (" ".join(rejected_tickers)))
    if st.button("Click to Continue"):
        session_state.button = True
    st.stop()

transactions_dataframe = utils.process_splits_data(
        dict_of_available_tickers,
        transactions_dataframe)

merged_data = utils.merge_historical_data_with_transactions(
        dict_of_available_tickers,
        transactions_dataframe)

st.write("## Account Balance")

account_balance_graph(account_dataframe)


st.write("---")
st.write("## Stocks in Portfolio")

individual_stocks_graphs(dict_of_available_tickers, transactions_dataframe)


st.write("---")
st.write("## Stock Returns")

combined_returns_line_graph(merged_data)
owned_sold_returns_bar_graph(merged_data)
