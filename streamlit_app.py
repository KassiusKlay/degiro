from state import _get_state
import streamlit as st
import pandas as pd
import db
import login
import altair as alt

APP = 'degiro'
CREDS = 'user_credentials.xlsx'


def show_page(state):
    if st.sidebar.button('Recomecar'):
        state.clear()
    df = state.df
    df['Expedido'] = pd.to_datetime(df['Expedido'], dayfirst=True)

    st.write('## Análises por Mês (exclui Aditamentos)')

    totais = df.loc[~df['Tipo de Exame'].isin([
                'Aditamento Imunocitoquímica',
                'HBA - Aditamento de Imunocitoquímica'])]

    number_of_months = (totais.Expedido.max().to_period('M') -
                        totais.Expedido.min().to_period('M')).n
    bar = alt.Chart(totais).mark_bar().encode(
            x=alt.X('yearmonth(Expedido):T', axis=alt.Axis(
                title='Data', tickCount=number_of_months, grid=False)),
            y=alt.Y('count(Exame)', axis=alt.Axis(title='Número de Análises'))
            )

    text = alt.Chart(totais).mark_text(dx=12, dy=-5, color='black').encode(
            x=alt.X('yearmonth(Expedido):T', axis=alt.Axis(title='Data')),
            y=alt.Y('count(Exame)', axis=alt.Axis(title='Número de Análises')),
            text=alt.Text('count(Exame)'))

    st.altair_chart(bar + text, use_container_width=True)

    cols = st.beta_columns(2)
    cols[0].write(' ## Total de Exames e Honorários - HLUZ')
    hluz = df.loc[df.Unidade != 'HBA'].groupby('Tipo de Exame').agg(
            Totais=('Tipo de Exame', 'size'),
            Média=('Honorários', 'mean'),
            Mínimo=('Honorários', 'min'),
            Máximo=('Honorários', 'max')
            ).sort_values(by='Totais', ascending=False)
    cols[0].table(hluz)

    cols[1].write(' ## Total de Exames e Honorários - HBA')
    hba = df.loc[df.Unidade == 'HBA'].groupby('Tipo de Exame').agg(
            Totais=('Tipo de Exame', 'size'),
            Média=('Honorários', 'mean'),
            Mínimo=('Honorários', 'min'),
            Máximo=('Honorários', 'max')
            ).sort_values(by='Totais', ascending=False)
    cols[1].table(hba)

    st.write('# Média de Honorários e Total de Exames por Plano de Saúde')
    hluz = df.loc[df.Unidade != 'HBA'].groupby('Tipo de Exame')
    for name, group in hluz:
        st.write(name)
        base = alt.Chart(group).mark_bar().encode(
                y=alt.Y('Plano SS:N', sort='x', axis=alt.Axis(title='')))
        chart = alt.hconcat(base.encode(x=alt.X(
            'mean(Honorários):Q',
            axis=alt.Axis(title='Média de Honorários')), color=alt.Color(
                'Plano SS:N',
                sort='x',
                legend=None,
                scale=alt.Scale(scheme='category20c'))
            ), base.encode(
                x=alt.X('count():Q', axis=alt.Axis(title='Total de Exames'))))
        st.altair_chart(chart, use_container_width=True)


def main():
    st.set_page_config(layout='wide')
    state = _get_state()

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
            st.write('## Account')
            st.write(state.account)
            st.write(' ## Transactions')
            st.write(state.transactions)
            # show_page(state)

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
