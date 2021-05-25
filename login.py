import streamlit as st
import pandas as pd
import db
import process
import upload

APP = 'degiro'
CREDS = 'user_credentials.xlsx'


def login(state):
    with st.sidebar.form(key='login'):
        user = st.text_input('User', '')
        password = st.text_input('Password', '', type='password')
        submit_button = st.form_submit_button(label='Login')
    if submit_button:
        if not state.user_credentials.loc[
                (state.user_credentials.user == user) &
                (state.user_credentials.password == password)].empty:
            state.user = user
        else:
            st.sidebar.warning('Wrong User / Password')


def create_account(dbx, state):
    with st.sidebar.form(key='create_account'):
        user = st.text_input('Select a Username', '')
        password = st.text_input('Password', '', type='password')
        submit_button = st.form_submit_button(label='Create Account')
    if submit_button:
        if not password:
            st.sidebar.warning('Please pick a valid password')
            st.stop()
        if any(state.user_credentials.user == user):
            st.sidebar.warning('User already registered')
            st.stop()
        else:
            st.sidebar.warning('Creating account...')
            state.user_credentials = state.user_credentials.append(
                    {'user': user, 'password': password},
                    ignore_index=True).sort_values(by='user', axis=0)
            db.upload_dataframe(
                    dbx, APP, state.user_credentials, CREDS)
            state.user = user


def get_df(dbx, state):
    if not state.uploading_file:
        radio_placeholder = st.sidebar.empty()
        option = radio_placeholder.radio(
                '', ['Open saved files', 'Upload new files'])
        button_placeholder = st.sidebar.empty()
        if button_placeholder.button('OK'):
            button_placeholder.empty()
            if option == 'Open saved files':
                open_file(dbx, state)
            else:
                state.uploading_file = True
    else:
        upload.upload_file(dbx, state)


def open_file(dbx, state):
    try:
        state.account = db.download_dataframe(
                dbx,
                APP,
                f'{state.user}_account.xlsx'
                )
        state.transactions = db.download_dataframe(
                dbx,
                APP,
                f'{state.user}_transactions.xlsx'
                )
    except Exception:
        warning_placeholder = st.sidebar.empty()
        warning_placeholder.warning(
                'There aren\'t any files saved on this account')
