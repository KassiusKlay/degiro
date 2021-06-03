import streamlit as st
from state import _get_state
import degiroapi
import process
import account
import individual_stocks


def main():
    st.set_page_config(layout='wide')
    state = _get_state()

    placeholder = st.empty()
    if state.degiro is None:
        with placeholder.form('2FA'):
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
        placeholder.empty()
        process.get_data(state)

    if state.products is not None:
        show_page(state)

    state.sync()


def show_page(state):
    st.write(' # Account Overview')
    account.show(state)
    st.write(' # Individual Stock Data')
    individual_stocks.show(state)


if __name__ == '__main__':
    main()
