import yfinance as yf
from account import process_account_dataframe, get_deposits_dataframe, get_total_deposits
from transactions import process_transactions_dataframe, get_ticker_from_ISIN, check_valid_ticker_data, get_ticker_list_data, plot_selected_stock_and_start_date
from utils import check_uploaded_files, load_data, show_formatted_dataframe
from altair import datum
import pandas as pd
import streamlit as st
import altair as alt
import SessionState

session_state = SessionState.get(button='', yfinance='')

st.title("Degiro Interactive Analyser")
placeholder = st.empty()
uploaded_files = st.sidebar.file_uploader(
        "", type='.csv', accept_multiple_files=True)

if not check_uploaded_files(uploaded_files):
    placeholder.markdown(
        """
        Please upload the **Account.csv** and **Transaction.csv**
        files from Degiro.
        Instructions [here](https://www.github.com)
        """)
    st.warning("Please upload the correct files")
    st.stop()
placeholder.empty()

account_dataframe = load_data(sorted(uploaded_files, key=lambda x: x.name)[0])
account_dataframe = process_account_dataframe(account_dataframe)
transactions_dataframe = load_data(
        sorted(uploaded_files, key=lambda x: x.name)[1])
transactions_dataframe = process_transactions_dataframe(transactions_dataframe)

ticker_list = []
for ISIN in transactions_dataframe.ISIN.unique():
    ticker_list.append(get_ticker_from_ISIN(ISIN))

dict_of_available_tickers = get_ticker_list_data(ticker_list)
rejected_tickers = ticker_list - dict_of_available_tickers.keys()

if not session_state.button:
    st.markdown("""Error fetching data from the follwing products:\n
     - %s""" % (" ".join(rejected_tickers)))
    if st.button("Click to Continue"):
        session_state.button = True
    st.stop()

for ticker, value in dict_of_available_tickers.items():
    if not value['Splits'].empty:
        for i in value['Splits'].index:
            transactions_dataframe.Number.loc[
                (transactions_dataframe.Date.dt.date <= i.date())
                & (transactions_dataframe.ISIN
                    == value['ISIN'])] = transactions_dataframe.Number.loc[
                (transactions_dataframe.Date.dt.date <= i.date())
                & (transactions_dataframe.ISIN
                    == value['ISIN'])] * value['Splits'].loc[i]
            transactions_dataframe.Price.loc[
                (transactions_dataframe.Date.dt.date <= i.date())
                & (transactions_dataframe.ISIN
                    == value['ISIN'])] = transactions_dataframe.Price.loc[
                (transactions_dataframe.Date.dt.date <= i.date())
                & (transactions_dataframe.ISIN
                    == value['ISIN'])] / value['Splits'].loc[i]
            transactions_dataframe = transactions_dataframe[
                (transactions_dataframe.Date.dt.date != i.date())
                | (transactions_dataframe.ISIN != value['ISIN'])]

st.write("## Deposits / Withdrawls")

deposits_dataframe = get_deposits_dataframe(account_dataframe)
total_deposits = get_total_deposits(deposits_dataframe)
st.markdown(
        "Net Account Movements (for the selected period): **%s**"
        % total_deposits)

deposits_chart = alt.Chart(deposits_dataframe).mark_bar().encode(
        alt.Column('year(Date):T', title='Year'),
        alt.Y('sum(Movement):Q', title='Deposits'),
        alt.X('Description:O', title=None)).properties(width=alt.Step(50))
st.altair_chart(deposits_chart)


st.write("---")
st.write("## Stocks in Portfolio")


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
    chart = plot_selected_stock_and_start_date(
            dict_of_available_tickers[stock]['Data'],
            start_date, end_date)
    just_the_stock_dataframe = transactions_dataframe.loc[
            (transactions_dataframe.Date.dt.year >= start_date)
            & (transactions_dataframe.Date.dt.year <= end_date)
            & (transactions_dataframe.ISIN
                == dict_of_available_tickers[stock]['ISIN'])]
    cross = alt.Chart(just_the_stock_dataframe).mark_circle().encode(
            x='Date:T',
            y='Price:Q', size=alt.Size('Price:Q', legend=None),
            tooltip=['Number', 'Total Cost'],
            color=alt.Color(
                'Number:O',
                scale=alt.Scale(scheme='reds'))).interactive()

    combo = chart + cross

    st.altair_chart(combo, use_container_width=True)

st.write("---")
st.write("## Stock Returns")

joined = pd.DataFrame()
for ticker in dict_of_available_tickers.keys():
    df = transactions_dataframe.loc[
        transactions_dataframe.ISIN
        == dict_of_available_tickers[ticker]['ISIN']]
    data = dict_of_available_tickers[ticker]['Data'].copy()
    data = data.loc[data.Date.dt.date >= df.Date.min()]
    close = data.Close
    returns = (close / close.iloc[0] * 100 - 100) / 100
    data['Returns'] = returns
    data['Ticker'] = ticker
    joined = pd.concat([joined, data[['Ticker', 'Date', 'Returns']]])

highlight = alt.selection(type='single', on='mouseover',
                          fields=['Ticker'], nearest=True)

base = alt.Chart(joined).encode(
    x='Date:T',
    y=alt.Y('Returns:Q', axis=alt.Axis(format='.0%')),
    color=alt.Color(
            'Ticker:N',
            scale=alt.Scale(scheme='category20')))

points = base.mark_circle().encode(
    opacity=alt.value(0)
).add_selection(
    highlight
)

lines = base.mark_line().encode(
    size=alt.condition(~highlight, alt.value(1), alt.value(2.5))
).interactive()

st.altair_chart(points + lines, use_container_width=True)


st.write('---')
st.write('## Tests')

final = pd.DataFrame(columns=['Ticker', 'Date', 'Returns', 'Number'])
for ticker in dict_of_available_tickers.keys():
    df_from_joined = joined.loc[joined.Ticker == ticker]
    numbers = transactions_dataframe.loc[
        transactions_dataframe.ISIN
            == dict_of_available_tickers[ticker]['ISIN']][['Date', 'Number']]
    tmp = pd.merge(df_from_joined, numbers, how='outer')
    tmp.Number = tmp.Number.fillna(0)
    tmp.Number = tmp.Number.cumsum()
    final = pd.merge(final, tmp, how='outer')

final
teste = final.groupby(['Date'])
a = teste.get_group(final.Date.max())
a

chart = alt.Chart(a).mark_bar().encode(
        x=alt.X('Ticker', sort='-y'),
        y='Returns',
        color=alt.condition(alt.datum.Number > 0, alt.Color('Ticker:N', sort='-y'), alt.value('red')))
st.altair_chart(chart, use_container_width=True)


bars = pd.DataFrame(columns = ['Ticker', 'Date', 'Returns'])
for ticker in dict_of_available_tickers.keys():
    x = joined.loc[(joined.Date == joined.Date.max()) & (joined.Ticker == ticker)]
    bars = pd.merge(bars, x, how='outer')

bars = bars.drop('Date', axis=1)

chart = alt.Chart(bars).mark_bar().encode(
        x=alt.X('Ticker', sort='-y'),
        y='Returns',
        color=alt.Color('Ticker', sort='-y'))
st.altair_chart(chart, use_container_width=True)


