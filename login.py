import streamlit as st
import pandas as pd
import utils


def get_data_from_db(db, user):
    user_ref = db.collection('degiro').document(user)
    user_data = user_ref.get().to_dict()
    account_dataframe = pd.DataFrame.from_dict(user_data['account_dict'])
    account_columns = user_data['account_columns']
    transactions_dataframe = pd.DataFrame.from_dict(
            user_data['transactions_dict'])
    transactions_columns = user_data['transactions_columns']

    account_dataframe = account_dataframe[account_columns]
    account_dataframe.index = account_dataframe.index.astype(int)
    account_dataframe = account_dataframe.sort_index()

    transactions_dataframe = transactions_dataframe[transactions_columns]
    transactions_dataframe.index = transactions_dataframe.index.astype(int)
    transactions_dataframe = transactions_dataframe.sort_index()
    return [account_dataframe, transactions_dataframe]


def login(db):
    user_placeholder = st.sidebar.empty()
    pass_placeholder = st.sidebar.empty()
    login_placeholder = st.sidebar.empty()
    user = user_placeholder.text_input('User', value='')
    password = pass_placeholder.text_input('Password', value='')
    login_button = login_placeholder.button('Login')
    if login_button and utils.check_valid_credentials(db, user, password):
        user_placeholder.empty()
        pass_placeholder.empty()
        login_placeholder.empty()
        stored_data = get_data_from_db(db, user)
        return stored_data
    else:
        st.stop()
