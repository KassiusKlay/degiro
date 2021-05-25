import streamlit as st
import db
import pandas as pd

APP = 'degiro'


def check_files(df, state):
    if 'ISIN' not in df.columns:
        st.warning('Wrong file')
        st.stop()
    number_of_columns = df.shape[1]
    if number_of_columns != 12:
        check_transactions_date(df)
        if state.transactions is None:
            state.transactions = df
        else:
            st.warning('Duplicated files')
            state.transactions = None
            st.stop()
    else:
        if state.account is None:
            state.account = df
        else:
            st.warning('Duplicated files')
            state.account = None
            st.stop()


def check_transactions_date(df):
    grouped = df.groupby('ISIN')
    for ISIN, df in grouped:
        if df.iloc[:, 6].astype(int).sum() < 0:
            st.warning("""
            **Incorrect Time Period**

            Upload **Transactions.csv** from the beginning of
            your account creation
            """)
            st.stop()


def check_uploaded_files(state, uploaded_files):
    test1 = pd.read_csv(uploaded_files[0])
    test2 = pd.read_csv(uploaded_files[1])
    check_files(test1, state)
    check_files(test2, state)


def upload_file(dbx, state):
    placeholder = st.empty()
    uploaded_files = st.sidebar.file_uploader(
        '', type='.csv', accept_multiple_files=True)
    if len(uploaded_files) == 2:
        check_uploaded_files(state, uploaded_files)
        placeholder.warning('Saving files...')
        db.upload_dataframe(
                dbx,
                APP,
                state.account,
                f'{state.user}_account.xlsx'
                )
        db.upload_dataframe(
                dbx,
                APP,
                state.transactions,
                f'{state.user}_transactions.xlsx'
                )
        placeholder.success('Files saved')
    elif uploaded_files:
        st.warning('Please upload the correct files')
        st.stop()
