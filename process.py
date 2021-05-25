import numpy as np
import re
import requests
import yfinance as yf
import pandas as pd
import streamlit as st
from forex_python.converter import CurrencyRates


def process_account_dataframe(df):
    df = df.drop(df.columns[[1, 2, 4, 6, 9, 11]], axis=1)
    df.columns = [
            'Date',
            'Product',
            'Description',
            'Currency',
            'Movement',
            'Balance']
    df = df.dropna(how="all")
    df = df.dropna(subset=['Currency'])
    df['Movement'] = df['Movement'].str.replace(
            ',',
            '.',
            regex=True).astype(float)
    df['Balance'] = df['Balance'].str.replace(
            ',',
            '.',
            regex=True).astype(float)
    df.Date = pd.to_datetime(df.Date, format='%d-%m-%Y', utc=True)
    return df


def process_transactions_dataframe(df):
    df = df.drop(df.columns[[1, 5, 18]], axis=1)
    df.columns = [
            'Date',
            'Product',
            'ISIN',
            'Exchange',
            'Shares',
            'Price',
            'Currency',
            'Cost (Exchange)',
            'Currency (Exchange)',
            'Cost (Local)',
            'Currency (Local)',
            'Exchange Rate',
            'Commission',
            'Currency (Comission)',
            'Total Cost',
            'Currency (Total)']
    df = df.dropna(how="all")
    df = df.dropna(subset=['Currency'])
    df.Date = pd.to_datetime(df.Date, format='%d-%m-%Y')
    return df

def process_data(state):
    state.processed_account = process_account_dataframe(
            state.account)
    state.processed_transactions = process_transactions_dataframe(
            state.transactions)


