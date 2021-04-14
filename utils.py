import pandas as pd
import streamlit as st

@st.cache
def check_uploaded_files(uploaded_files):
    list_of_uploaded_files = [file.name for file in uploaded_files]
    required_files = ['Account.csv', 'Transactions.csv']
    if not set(list_of_uploaded_files)^set(required_files):
        return True

def load_data(filename):
    df = pd.read_csv(filename)
    return df

def show_formatted_dataframe(df):
    st.dataframe(df.style.format({'Date':lambda t: t.strftime('%d-%m-%Y')}).set_precision(2))

