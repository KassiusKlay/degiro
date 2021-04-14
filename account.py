import streamlit as st
import pandas as pd

@st.cache
def process_account_dataframe(df):
    df = df.drop(df.columns[[1,2,4,6,9,11]], axis=1)
    df.columns = ['Date', 'Product', 'Description', 'Currency', 'Movement', 'Balance']
    df = df.dropna(how="all")
    df = df.dropna(subset=['Currency'])
    df['Movement'] = df['Movement'].str.replace(',', '.', regex=True).astype(float)
    df['Balance'] = df['Balance'].str.replace(',', '.', regex=True).astype(float)
    df.Date = pd.to_datetime(df.Date, format='%d-%m-%Y', utc=True)
    return df

def get_deposits_dataframe(df):
    unique_years = df.Date.dt.year.unique()
    if not st.checkbox("Plot entire data?", value=True):
        selected_years = st.multiselect('Select Year', unique_years)
        if not selected_years:
            st.warning("Please select year")
            st.stop()
        deposits_dataframe = df[df.Date.dt.year.isin(selected_years)]
        deposits_dataframe = deposits_dataframe[df.Description.str.contains('Dep|With')]
    else:
        deposits_dataframe = df[df.Description.str.contains('Dep|With')]
    deposits_dataframe.Description.replace('flatex Deposit', 'Deposit', inplace = True)
    deposits_dataframe.Description.replace('Depósito', 'Deposit', inplace = True)
    return deposits_dataframe

def get_total_deposits(df):
    total_deposits = df.Movement.sum()
    deposited_currency = df.Currency.value_counts().idxmax()
    return str(total_deposits) + ' ' + deposited_currency
