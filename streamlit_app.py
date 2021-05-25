from state import _get_state
import streamlit as st
import db
import login
import process
import raw
import summary

APP = 'degiro'
CREDS = 'user_credentials.xlsx'


def show_pages(state):
    pages = {
        'Raw Data': raw.show,
        'Summary': summary.show
    }
    page = st.sidebar.radio('', tuple(pages.keys()))
    pages[page](state)


def main():
    st.set_page_config(layout='wide')
    state = _get_state()

    if st.sidebar.button('Restart'):
        state.clear()

    dbx = db.get_dropbox_client()
    state.user_credentials = db.download_dataframe(dbx, APP, CREDS)

    st.sidebar.title("Degiro Visual Tool")

    if not state.user:
        option = st.sidebar.radio('', ['Login', 'Create Account'])
        if option == 'Login':
            login.login(state)
        else:
            login.create_account(dbx, state)
    else:
        if state.account is None and state.transactions is None:
            login.get_df(dbx, state)
        else:
            if not state.processed_data:
                process.process_data(state)
            else:
                show_pages(state)

    # side_instructions()
    state.sync()


def side_instructions():
    st.sidebar.markdown(r'''
    ## Instrucções:

    1. Fazer Login ou Criar Conta
    2. Ver ficheiro\* ou Guardar Ficheiro\*

    *Ficheiro Excel dos honorários
    ''')


if __name__ == "__main__":
    main()
