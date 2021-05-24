import streamlit as st
import pandas as pd
import db
import process

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
                '', ['Check saved files', 'Upload new files'])
        button_placeholder = st.sidebar.empty()
        if button_placeholder.button('OK'):
            button_placeholder.empty()
            if option == 'Check saved files':
                open_file(dbx, state)
            else:
                state.uploading_file = True
    else:
        upload_file(dbx, state)


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


def check_uploaded_files(uploaded_files):
    list_of_uploaded_files = [file.name for file in uploaded_files]
    required_files = ['Account.csv', 'Transactions.csv']
    if not set(list_of_uploaded_files) ^ set(required_files):
        return True


def upload_file(dbx, state):
    placeholder = st.sidebar.empty()
    button_placeholder = st.sidebar.empty()
    if not state.uploaded_files:
        uploaded_files = st.sidebar.file_uploader(
            '', type='.csv', accept_multiple_files=True)
        if uploaded_files and check_uploaded_files(uploaded_files):
            state.uploaded_files = uploaded_files
        elif uploaded_files:
            placeholder.warning('Please upload the correct files')
            st.stop()
    else:
        placeholder.warning('Saving files...')
        try:
            state.account = pd.read_csv(
                sorted(state.uploaded_files, key=lambda x: x.name)[0])
            state.transactions = pd.read_csv(
                sorted(state.uploaded_files, key=lambda x: x.name)[1])
        except Exception:
            st.sidebar.warning('Error opening files')
            state.uploading_file = False
            state.uploaded_files = None
            if button_placeholder.button('OK'):
                pass
            st.stop()
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
        placeholder.warning('Ficheiro guardado')
        if st.sidebar.button('OK'):
            pass
