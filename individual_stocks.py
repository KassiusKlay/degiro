import streamlit as st
import altair as alt


def line_chart_between_selected_dates(df, start_date, end_date):
    df = df.loc[
            (df.Date.dt.year >= start_date)
            & (df.Date.dt.year <= end_date)]
    chart = alt.Chart(df).mark_line().encode(
            alt.X('Date:T'),
            alt.Y('Close:Q', title='Price'))
    return chart


def cross_chart_between_selected_dates(
        transactions_dataframe,
        ISIN,
        start_date,
        end_date):

    df = transactions_dataframe.loc[
        (transactions_dataframe.Date.dt.year >= start_date)
        & (transactions_dataframe.Date.dt.year <= end_date)
        & (transactions_dataframe.ISIN == ISIN)]
    chart = alt.Chart(df).mark_circle().encode(
            x='Date:T',
            y='Price:Q', size=alt.Size('Price:Q', legend=None),
            tooltip=['Number', 'Total Cost'],
            color=alt.Color(
                'Number:O',
                scale=alt.Scale(scheme='reds'))).interactive()
    return chart


def individual_stocks_graphs(
        dict_of_available_tickers,
        transactions_dataframe):

    stock_selection = st.multiselect(
            "Select stocks", list(dict_of_available_tickers.keys()))
    for stock in stock_selection[::-1]:
        st.write("**%s**" % stock)
        start_date = st.slider(
            "Select start date",
            key=stock,
            min_value=dict_of_available_tickers[stock]['Data'].Date.min().year,
            max_value=dict_of_available_tickers[stock]['Data'].Date.max().year)
        end_date = st.slider(
            "Select end date",
            key=stock,
            min_value=dict_of_available_tickers[stock]['Data'].Date.min().year,
            max_value=dict_of_available_tickers[stock]['Data'].Date.max().year,
            value=dict_of_available_tickers[stock]['Data'].Date.max().year)
        if (start_date > end_date):
            st.warning("Start Date > End Date")
            st.stop()
        line_chart = line_chart_between_selected_dates(
                dict_of_available_tickers[stock]['Data'],
                start_date, end_date)

        cross_chart = cross_chart_between_selected_dates(
            transactions_dataframe,
            dict_of_available_tickers[stock]['ISIN'],
            start_date,
            end_date)

        combo = line_chart + cross_chart

        st.altair_chart(combo, use_container_width=True)
