from account import account_balance_graph
from individual_stocks import individual_stocks_graphs
from returns import combined_returns_line_graph, owned_sold_returns_bar_graph
from summary import get_summary_data
import streamlit as st
import SessionState
import utils

session_state = SessionState.get(button='')

st.title("Degiro Interactive Dashboard")
import numpy as np
import time

# for i in range(100):
    # # Update progress bar.
    # progress_bar.progress(i + 1)

    # new_rows = np.random.randn(10, 2)

    # # Update status text.
    # status_text.text(
        # 'The latest random number is: %s' % new_rows[-1, 1])

    # # Append data to the chart.
    # chart.add_rows(new_rows)

    # # Pretend we're doing some computation that takes time.
    # time.sleep(0.1)

# status_text.text('Done!')
# status_text.empty()
# bar.empty()
# st.balloons()

placeholder = st.empty()
uploaded_files = st.sidebar.file_uploader(
        "", type='.csv', accept_multiple_files=True)

st.sidebar.write("""
    ## Disclaimer
    Some products might not be available on Yahoo Finance (tracking tool used)

    Most graphs allow:

    1. Drag
    2. Zoom

    Stock Returns Line Graph allows:

    - Select individual stocks with shift+click on legend""")

if not utils.check_uploaded_files(uploaded_files):
    placeholder.markdown(
        """
        Please upload the **Account.csv** and **Transaction.csv**
        files from Degiro.
        Instructions [here](https://github.com/KassiusKlay/degiro#Instructions)
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
bar = st.empty()
progress_bar = bar.progress(0)
steps = int(round((100 / len(transactions_dataframe.ISIN.unique())), 0))
progress = 0
for ISIN in transactions_dataframe.ISIN.unique():
    date_checker = transactions_dataframe.loc[
            transactions_dataframe.ISIN == ISIN]
    if date_checker.Shares.sum() < 0:
        st.warning("""
        **Incorrect Time Period**

        Please Upload **Transactions.csv** from the beginning of your account
        creation

        Instructions [here](https://github.com/KassiusKlay/degiro)
        """)
        st.stop()
    ticker_list.append(utils.get_ticker_from_ISIN(ISIN))
    progress_bar.progress(progress)
    progress += steps
bar.empty()

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

general_data = utils.get_general_data(
        dict_of_available_tickers,
        transactions_dataframe)

st.write("---")
st.write("## Summary")
summary = get_summary_data(general_data)
summary

st.write("---")
st.write("## Account Balance")
account_balance_graph(account_dataframe)

st.write("---")
st.write("## Historical Data")
individual_stocks_graphs(dict_of_available_tickers, transactions_dataframe)

st.write("---")
st.write("## Stock Returns")
combined_returns_line_graph(merged_data)
owned_sold_returns_bar_graph(merged_data)


