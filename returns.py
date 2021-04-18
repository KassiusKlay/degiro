import pandas as pd
import streamlit as st
import altair as alt


def get_returns_data(df):
    returns_data = pd.DataFrame()
    for ticker in df.Ticker.unique():
        close = df.loc[(df.Ticker == ticker)].Close
        returns = (close / close.iloc[0] * 100 - 100) / 100
        returns_data = pd.concat([returns_data, returns])

    df['Returns'] = returns_data
    return df


def combined_returns_line_graph(merged_data):
    combined_returns = get_returns_data(merged_data)

    highlight = alt.selection(type='single', on='mouseover',
                              fields=['Ticker'], nearest=True)

    base = alt.Chart(combined_returns).encode(
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

    # LEGEND SELECTION

    selection = alt.selection_multi(fields=['Ticker'], bind='legend')

    chart = alt.Chart(combined_returns).mark_line().encode(
        alt.X('Date:T', axis=alt.Axis(tickSize=0)),
        alt.Y('Returns:Q', axis=alt.Axis(format='.0%')),
        alt.Color('Ticker:N', scale=alt.Scale(scheme='category20')),
        opacity=alt.condition(selection, alt.value(0.8), alt.value(0.1))
    ).add_selection(
        selection
    ).interactive()

    st.altair_chart(chart, use_container_width=True)

    # RULER TOOLTIP

# Create a selection that chooses the nearest point & selects based on x-value
    nearest = alt.selection(type='single', nearest=True, on='mouseover',
                            fields=['Date'], empty='none')

# The basic line
    line = alt.Chart(combined_returns).mark_line(interpolate='basis').encode(
            alt.X('Date:T'),
        alt.Y('Returns:Q', axis=alt.Axis(format='.0%')),
        alt.Color('Ticker:N', scale=alt.Scale(scheme='category20'))
    )

# Transparent selectors across the chart. This is what tells us
# the x-value of the cursor
    selectors = alt.Chart(combined_returns).mark_point().encode(
        x='Date:T',
        opacity=alt.value(0),
    ).add_selection(
        nearest
    )

# Draw points on the line, and highlight based on selection
    points = line.mark_point().encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    ).transform_filter(
            selection
            )

# Draw text labels near the points, and highlight based on selection
    text = line.mark_text(align='left', dx=5, dy=-5).encode(
        text=(alt.condition(nearest, 'Returns:Q', alt.value(' '), format='.0%'))
    ).transform_filter(
            selection
            )

# Draw a rule at the location of the selection
    rules = alt.Chart(combined_returns).mark_rule(color='gray').encode(
        x='Date:T',
    ).transform_filter(
        nearest
    )

# Put the five layers into a chart and bind the data
    chart2 = alt.layer(
        chart, selectors, points, rules, text
    )

    st.altair_chart(chart2, use_container_width=True)

def owned_sold_returns_bar_graph(merged_data):

    owned_returns = get_returns_data(merged_data[merged_data.Number != 0])
    if not merged_data[merged_data.Number == 0].empty:
        sold_returns = get_returns_data(merged_data[merged_data.Number == 0])

    bars_owned = pd.DataFrame(columns=['Ticker', 'Date', 'Returns'])
    for ticker in owned_returns.Ticker.unique():
        x = owned_returns.loc[owned_returns.Ticker == ticker]
        x = x.loc[x.Date == x.Date.max()]
        bars_owned = pd.merge(bars_owned, x, how='outer')

    bars_owned = bars_owned.drop('Date', axis=1)

    chart_owned = alt.Chart(bars_owned).mark_bar().encode(
            x=alt.X('Ticker', sort='-y'),
            y='Returns',
            color=alt.Color('Ticker', sort='-y'))

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
