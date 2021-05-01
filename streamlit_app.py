import login
import upload
import summary
import account
import individual_stocks
import returns
import utils
import SessionState
import streamlit as st
import json
from google.oauth2 import service_account
from google.cloud import firestore


def get_data():
    option_placeholder = st.sidebar.empty()
    if not session_state.list_of_df:
        option = option_placeholder.radio(
                'Choose option',
                ['Upload Files', 'Login'])
        if option == 'Login':
            session_state.list_of_df = login.login(db)
        else:
            session_state.list_of_df = upload.upload_files(db)
    if session_state.list_of_df:
        reload = option_placeholder.button('Reload Data?')
        if reload:
            session_state.list_of_df = False
            option_placeholder.empty()
            get_data()


def rejected_tickers_confirm():
    if not session_state.button:
        st.markdown("""Error fetching data from the follwing products:\n
         - %s""" % (" ".join(rejected_tickers)))
        if st.button("Click to Continue"):
            session_state.button = True
            rejected_tickers_confirm()
        st.stop()


key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds)

session_state = SessionState.get(
        button=False,
        list_of_df=False)

st.title("Degiro Interactive Visual Tool")
st.write('---')

get_data()

st.sidebar.write("""
    ## Disclaimer
    Some products might not be available on Yahoo Finance (tracking tool used)

    Most graphs allow:

    1. Drag
    2. Zoom

    Stock Returns Line Graph allows:

    - Select individual stocks with shift+click on legend""")

account_dataframe = session_state.list_of_df[0]
account_dataframe = utils.process_account_dataframe(account_dataframe)
transactions_dataframe = session_state.list_of_df[1]
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

rejected_tickers_confirm()

transactions_dataframe = utils.process_splits_data(
        dict_of_available_tickers,
        transactions_dataframe)

merged_data = utils.merge_historical_data_with_transactions(
        dict_of_available_tickers,
        transactions_dataframe)

general_data = utils.get_general_data(
        dict_of_available_tickers,
        transactions_dataframe)

st.write("## Summary")
summary.get_summary_data(general_data)

st.write("---")
st.write("## Account Balance")
account.account_balance_graph(account_dataframe)

st.write("---")
st.write("## Historical Data")
individual_stocks.individual_stocks_graphs(
        dict_of_available_tickers,
        transactions_dataframe)

st.write("---")
st.write("## Stock Returns")
returns.combined_returns_line_graph(merged_data)
returns.owned_sold_returns_bar_graph(merged_data)
