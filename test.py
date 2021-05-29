import streamlit as st
from state import _get_state
import degiroapi
import process
import account
import individual_stocks
import pandas as pd


def main():
    # st.set_page_config(layout='wide')
    state = _get_state()

    if state.degiro is None:
        with st.form('2FA'):
            username = st.text_input('Username', '')
            password = st.text_input('Password', '', type='password')
            totp = st.text_input('2FA - Leave empty if not needed', '')
            if st.form_submit_button('Submit'):
                state.degiro = degiroapi.DeGiro()
                try:
                    state.degiro.login(username, password, totp)
                except Exception:
                    st.warning('Wrong credentials')
                    state.degiro = None
                    st.stop()

    if state.degiro and state.products is None:
        process.get_data(state)

    if state.products is not None:
        show_page(state)

    state.sync()


def show_page(state):
    st.write(' ## Account Overview')
    account.show(state)
    st.write(' ## Portfolio Stock Data')
    individual_stocks.show(state)
    st.stop()
    # st.write(state.transactions)
    # df = state.transactions.copy()
    # df = df.loc[df.counterParty.notna()]

    portfolio = state.degiro.getdata(degiroapi.Data.Type.PORTFOLIO)
    product_list = [
            product for product in portfolio
            if product['positionType'] == 'PRODUCT']
    info = state.degiro.product_info(product_list[0]['id'])
    st.write(info)
    info = state.degiro.product_info(product_list[1]['id'])
    st.write(info)
    info = state.degiro.product_info(product_list[2]['id'])
    st.write(info)
    st.stop()
    for i in product_list[2:]:
        try:
            realprice = state.degiro.real_time_price(
                i['id'], degiroapi.Interval.Type.Max)
        except Exception:
            last_price = low52 = high52 = historical_data = None
        else:
            st.write(realprice)
            last_price = realprice[0]['data']['lastPrice']
            low52 = realprice[0]['data']['lowPriceP1Y']
            high52 = realprice[0]['data']['highPriceP1Y']
            historical_data = realprice[1]['data']
            historical_data = pd.DataFrame(
                    historical_data, columns=['date', 'price'])
            historical_data.date = pd.to_datetime(
                    historical_data.date.astype(int), unit='D')

    # for i in state.product.keys():
        # if 'tesla' in state.products[i]['name'].lower():
            # start = state.products[i]['transactions'].date.min()
            # st.write(start)
            # st.write(state.product[i]['historical_data'])
            # interest = state.products[i]['historical_data'].loc[
                # state.products[i]['historical_data'].date >= '2020-09-01']
            # st.write(interest)
    st.stop()


if __name__ == '__main__':
    main()
