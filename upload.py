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


def upload_files(db):
    warning_placeholder = st.empty()
    upload_files = st.sidebar.empty()
    uploaded_files = upload_files.file_uploader(
            "", type='.csv', accept_multiple_files=True)
    if not utils.check_uploaded_files(uploaded_files):
        warning_placeholder.markdown("""
        Please upload the **Account.csv** and **Transaction.csv**
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
    invalid_user = True
    invalid_password = True
    store_selection = store_placeholder.radio(
            'Want to store data for future use?',
            ['Yes', 'No'])
    if store_selection == 'Yes':
        user = user_placeholder.text_input(
                'Choose a new Username',
                value='')
        if user:
            if utils.check_user_exists(db, user):
                st.sidebar.warning(
                        'User already exists. Choose another one or Login')
            else:
                invalid_user = False
        password = pass_placeholder.text_input(
                'Choose a Password',
                value='')
        if password:
            if len(password) < 8:
                st.sidebar.warning(
                        'Password must have minimum 8 characters')
            else:
                invalid_password = False
        if not invalid_user and not invalid_password:
            confirm = confirm_placeholder.button('Confirm')
            if not confirm:
                st.stop()
            save_data_in_db(list_of_df, db, user, password)
            user_placeholder.empty()
            pass_placeholder.empty()
        else:
            st.stop()
    else:
        confirm = confirm_placeholder.button('Confirm')
        if not confirm:
            st.stop()
    store_placeholder.empty()
    confirm_placeholder.empty()
    upload_files.empty()
    return list_of_df
