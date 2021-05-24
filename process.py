import pandas as pd
import xlrd
import datetime as dt


def from_excel_datetime(x):
    return dt.datetime(*xlrd.xldate_as_tuple(x, datemode=0))


def process_clinic_df(df, unidade):
    df = df.dropna(how='all')
    df.columns = df.iloc[0]
    df = df.dropna(subset=['Entrada'])
    df = df.loc[df.Ano != 'Ano']
    df = df.loc[df['Entrada'].astype(str).str.len() <= 5]
    df['Entrada'] = df['Entrada'].map(from_excel_datetime)
    df['Expedido'] = df['Expedido'].map(from_excel_datetime)
    df['Exame'].loc[df['Exame'].str.contains(
        'citologia',
        case=False,
        regex=True)] = 'Citologia'
    df['Unidade'] = unidade
    df['Entrada'] = pd.to_datetime(
            df['Entrada'],
            errors='coerce').dt.strftime('%d-%m-%Y')
    df['Expedido'] = pd.to_datetime(
            df['Expedido'],
            errors='coerce').dt.strftime('%d-%m-%Y')
    if unidade != 'HBA':
        df.loc[df['Exame'].str.contains(
            'HBA', case=False, regex=True)] = 'Aditamento Imunocitoquímica'
        df = df.loc[~df['Exame'].str.contains(
            'Revis', case=False, regex=True)]
        df = df.loc[~df['Plano SS'].str.contains(
            'Aditamento', case=False, regex=True)]
    df = df.rename(columns={'Exame': 'Tipo de Exame', 'Nº Exame': 'Exame'})
    df['Exame'] = df['Exame'].astype(str).str.pad(5, fillchar='0')
    df['Exame'] = df['Ano'].astype(str).str.slice(
            start=2) + '/' + df['Exame']
    df = df.iloc[1:].reset_index(drop=True)
    df = df[[
        'Entrada',
        'Expedido',
        'NHC',
        'Episódio',
        'Exame',
        'Tipo de Exame',
        'Plano SS',
        'Honorários',
        'Unidade']]
    return df


def process_file(file):
    hluz = process_clinic_df(file['Actividade HLUZ'], 'HLUZ')
    hba = process_clinic_df(file['Actividade HBA'], 'HBA')
    cca = process_clinic_df(file['Actividade CCA'], 'CCA')
    cpp = process_clinic_df(file['Actividade CPP'], 'CPP')
    df = pd.concat(
            [hluz, hba, cca, cpp],
            ignore_index=False
            ).sort_values(by='Entrada').reset_index(drop=True)
    return df
