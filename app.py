import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from datetime import datetime

# 1. ustawienia strony
st.set_page_config(page_title='Gym Tracker App', layout='wide')
st.title('Interaktywny Dashboard Treningowy')

# 2. wczytanie danych
@st.cache_data
def load_data():
    df = pd.read_csv('gym_tracker_export.csv', sep=';', encoding='utf-8-sig')
    # oczyszczanie daty do formatu liczbowego zrozumiałego dla algorytmów
    df['Data'] = pd.to_datetime(df['Data'].astype(str).str.extract(r'(\d{4}-\d{2}-\d{2})')[0])
    df['e1RM'] = df['Ciezar_kg'] * (1 + df['Powtorzenia'] / 30)

    # Grupowanie dzienne (najlepszy wynik z danego dnia)
    df_dzienne = df.groupby(['Data'], ['Cwiczenie']).agg(
        Max_e1RM = ('e1RM', 'max')
    ).reset_index()
    return df_dzienne

df = load_data()

# 3. interfejs - menu
st.markdown('---')
lista_cwiczen = df['Cwiczenie'].unique()
wybrane_cwiczenie = st.selectbox('Wybierz ćwiczenie do analizy:', lista_cwiczen)

df_plot = df[df['Cwiczenie'] == wybrane_cwiczenie].copy()
# średnia krocząca (wygładzony trend)
df_plot['Trend_1RM'] = df_plot['Max_e1RM'].rolling(window = 2, min_periods = 1).mean()

# 4. ARCHITEKTURA FRONT-ENDU: podział na kolumny
# col1 dostaje 75% szerokości ekranu, col2 dostaje 25%
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader('Wykres progresu')
    fig = go.Figure()
    # Folia 1:  surowy 1RM
    fig.add_trace(go.Scatter(x=df_plot['Data'], y=df_plot['Max_e1RM'], mode = 'lines+markers', name = '1eRM (Epley)',line=dict(color='blue', width = 2)))
    # Folia 2: Trend
    fig.add_trace(go.Scatter(x=df_plot['Data'], y=df_plot['Trend_1RM'], mode = 'lines', name = '1RM Trend',line=dict(color='cyan', dash = 'dash', width = 2)))

    fig.update_layout(hovermode = 'x unified')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader('Raport Maszin Lerning (ML)')
    st.write('Moduł predykcyjny Scikit-learn')

    # interaktywne pole tekstowe dla celu - można to zmieniać na żywo
    cel_kg = st.number_input('Wpisz swój cel (kg):', min_value=0.0, value = 100.0, step = 1.25)

    # ZABEZPIECZENIE: model ML zadziała tylko, jeśli mamy minimum 2 treningi
    if len(df_plot) > 1:
        df_ml = df_plot.dropna(subset = ['Max_e1RM', 'Data']).copy()
        df_ml['Data_liczbowo'] = df_ml['Data'].apply(lambda x: x.toordinal())

        X = df_ml[['Data_liczbowo']]
        y = df_ml['Max_e1RM']

        model = LinearRegression()
        model.fit(X, y)

        wspolczynnik_wzrostu = model.coef_[0]
        punkt_startowy = model.intercept_

        if wspolczynnik_wzrostu > 0:
            przewidywany_dzien = 