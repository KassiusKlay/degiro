import pandas as pd
import streamlit as st
import altair as alt


def get_returns_data(df):
    returns_data = pd.DataFrame()
    for ticker in df.Ticker.unique():
        close = df.loc[(df.Ticker == ticker)].Close
        returns = (close / close.iloc[0] * 100 - 100) / 100
        returns_data = pd.concat([returns_data, returns])

    df = df.assign(Returns=returns_data)
    return df


def combined_returns_line_graph(merged_data):
    combined_returns = get_returns_data(merged_data)

    selection = alt.selection_multi(fields=['Ticker'], bind='legend')

    chart = alt.Chart(combined_returns).mark_line().encode(
        alt.X('Date:T', axis=alt.Axis(tickSize=0)),
        alt.Y('Returns:Q', axis=alt.Axis(format='.0%')),
        alt.Color('Ticker:N', scale=alt.Scale(scheme='category20')),
        opacity=alt.condition(selection, alt.value(0.8), alt.value(0.05))
    ).add_selection(
        selection
    ).interactive()

    nearest = alt.selection(type='single', nearest=True, on='mouseover',
                            fields=['Date'], empty='none')
    base = alt.Chart(combined_returns).encode(
            alt.X('Date:T'),
            alt.Y('Returns:Q', axis=alt.Axis(format='.0%')),
            alt.Color('Ticker:N', scale=alt.Scale(scheme='category20'))
    ).transform_filter(selection)

    selectors = alt.Chart(combined_returns).mark_point().encode(
        x='Date:T',
        opacity=alt.value(0),
    ).add_selection(
        nearest
    )

    points = base.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )

    text = base.mark_text(align='left', dx=5, dy=-5).encode(
        text=(
            alt.condition(nearest, 'Returns:Q', alt.value(' '), format='.0%')))

    rules = alt.Chart(combined_returns).mark_rule(color='gray').encode(
        x='Date:T',
    ).transform_filter(
        nearest
    )

    chart2 = alt.layer(
        chart, selectors, points, rules, text
    )

    st.altair_chart(chart2, use_container_width=True)


def owned_sold_returns_bar_graph(merged_data):

    owned_returns = get_returns_data(merged_data[merged_data.Shares != 0])
    if not merged_data[merged_data.Shares == 0].empty:
        sold_returns = get_returns_data(merged_data[merged_data.Shares == 0])

    bars_owned = pd.DataFrame(columns=['Ticker', 'Date', 'Returns'])
    for ticker in owned_returns.Ticker.unique():
        x = owned_returns.loc[owned_returns.Ticker == ticker]
        x = x.loc[x.Date == x.Date.max()]
        bars_owned = pd.merge(bars_owned, x, how='outer')

    bars_owned = bars_owned.drop('Date', axis=1)

    chart_owned = alt.Chart(bars_owned).mark_bar().encode(
            alt.X('Ticker', sort='-y'),
            alt.Y('Returns:Q', axis=alt.Axis(format='.0%')),
            alt.Color('Ticker', sort='-y'))

    bars_sold = pd.DataFrame(columns=['Ticker', 'Date', 'Returns'])
    for ticker in sold_returns.Ticker.unique():
        x = sold_returns.loc[sold_returns.Ticker == ticker]
        x = x.loc[x.Date == x.Date.max()]
        bars_sold = pd.merge(bars_sold, x, how='outer')

    bars_sold = bars_sold.drop('Date', axis=1)

    chart_sold = alt.Chart(bars_sold).mark_bar(opacity=0.1).encode(
            x=alt.X('Ticker', sort='-y'),
            y='Returns',
            color=alt.value('black')).interactive()

    combo = chart_owned + chart_sold

    st.altair_chart(combo, use_container_width=True)
