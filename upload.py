import streamlit as st
import utils


def get_list_of_df_from_uploaded_files(uploaded_files):
    account_dataframe = utils.load_data(
            sorted(uploaded_files, key=lambda x: x.name)[0])
    transactions_dataframe = utils.load_data(
            sorted(uploaded_files, key=lambda x: x.name)[1])
    return [account_dataframe, transactions_dataframe]


def save_data_in_db(list_of_df, db, user, password):
    account_dataframe = list_of_df[0]
    transactions_dataframe = list_of_df[1]
    account_columns = account_dataframe.columns.tolist()
    transactions_columns = transactions_dataframe.columns.tolist()
    account_dict = account_dataframe.to_dict(orient='list')
    transactions_dict = transactions_dataframe.to_dict(orient='list')

    db.collection('degiro').document(user).set({
        'password': password,
        'account_dict': account_dict,
        'account_columns': account_columns,
        'transactions_dict': transactions_dict,
        'transactions_columns': transactions_columns})


def check_new_account_credentials(db, user, password):
    if not user and not password:
        st.sidebar.warning('Please choose a username and password')
        return 0
    if user:
        if utils.check_user_exists(db, user):
            st.sidebar.warning(
                    'User already exists. \
                            Choose another one or Update Account')
            return 0
    if password:
        if len(password) < 8:
            st.sidebar.warning(
                    'Password must have minimum 8 characters')
            return 0
    return 1


def upload_files(db):
    warning_placeholder = st.empty()
    upload_files = st.sidebar.empty()
    uploaded_files = upload_files.file_uploader(
            "", type='.csv', accept_multiple_files=True)
    if not utils.check_uploaded_files(uploaded_files):
        warning_placeholder.markdown("""
        Upload the **Account.csv** and **Transaction.csv**
        files from Degiro.
        Instructions [here](https://github.com/KassiusKlay/degiro)
        """)
        st.warning("Please upload the correct files")
        st.stop()

    list_of_df = get_list_of_df_from_uploaded_files(uploaded_files)

    store_placeholder = st.sidebar.empty()
    user_placeholder = st.sidebar.empty()
    pass_placeholder = st.sidebar.empty()
    confirm_placeholder = st.sidebar.empty()

    store_selection = store_placeholder.radio(
            'Want to store data for future use?',
            ['Update account', 'New account', 'No'])
    confirm = confirm_placeholder.button('Confirm')

    if store_selection == 'New account':
        user = user_placeholder.text_input(
                'Choose a new Username',
                value='')
        password = pass_placeholder.text_input(
                'Choose a Password',
                value='')
        if confirm and check_new_account_credentials(db, user, password):
            save_data_in_db(list_of_df, db, user, password)
            user_placeholder.empty()
            pass_placeholder.empty()
        else:
            st.stop()
    elif store_selection == 'Update account':
        user = user_placeholder.text_input(
                'User',
                value='')
        password = pass_placeholder.text_input(
                'Password',
                value='')
        if confirm and utils.check_valid_credentials(db, user, password):
            save_data_in_db(list_of_df, db, user, password)
            user_placeholder.empty()
            pass_placeholder.empty()
        else:
            st.stop()
    if not confirm:
        st.stop()

    store_placeholder.empty()
    confirm_placeholder.empty()
    upload_files.empty()

    return list_of_df
