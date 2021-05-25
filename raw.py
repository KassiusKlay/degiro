import streamlit as st


def show(state):
    st.write('## Account')
    st.write(state.account)
    st.write(' ## Transactions')
    st.write(state.transactions)
