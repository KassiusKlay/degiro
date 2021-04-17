import streamlit as st
import altair as alt


def get_deposits_dataframe(df):
    unique_years = df.Date.dt.year.unique()
    start_date = st.slider(
            "Select start date",
            min_value=int(unique_years.min()),
            max_value=int(unique_years.max()))
    end_date = st.slider(
            "Select end date",
            min_value=int(unique_years.min()),
            max_value=int(unique_years.max()),
            value=int(unique_years.max()))
    if (start_date > end_date):
        st.warning("Start Date > End Date")
        st.stop()
    deposits_dataframe = df.loc[
            (df.Date.dt.year >= start_date)
            & (df.Date.dt.year <= end_date)]
    deposits_dataframe = deposits_dataframe[
            df.Description.str.contains('Dep|With')]
    deposits_dataframe.Description.replace(
            'flatex Deposit',
            'Deposit',
            inplace=True)
    deposits_dataframe.Description.replace(
            'Depósito',
            'Deposit',
            inplace=True)
    return deposits_dataframe


def get_total_deposits(df):
    total_deposits = df.Movement.sum()
    deposited_currency = df.Currency.value_counts().idxmax()
    return str(total_deposits) + ' ' + deposited_currency


def account_balance_graph(account_dataframe):
    deposits_dataframe = get_deposits_dataframe(account_dataframe)
    total_deposits = get_total_deposits(deposits_dataframe)
    st.markdown(
            "Net Account Balance (for the selected period): **%s**"
            % total_deposits)

    deposits_chart = alt.Chart(deposits_dataframe).mark_bar().encode(
            alt.Column('year(Date):T', title='Year'),
            alt.Y('sum(Movement):Q', title='Deposits'),
            alt.X('Description:O', title=None)).properties(width=alt.Step(50))
    st.altair_chart(deposits_chart)
