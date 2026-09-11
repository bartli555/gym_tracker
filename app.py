import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. ustawienia strony
st.set_page_config(page_title='Gym Tracker App', layout='wide')
st.title('Interaktywny Dashboard Treningowy')

# 2. wczytanie i szybkie przeliczenie danych
# używam st.cache_data, żeby serwer nie musiał wczytywać pliku od nowa przy każdym kliknięciu
@st.cache_data
def load_data():
    df = pd.read_csv('gym_tracker_export.csv', sep=';', encoding='utf-8-sig')
    # oczyszczanie daty
    df['Data'] = df['Data'].astype(str).str.extract(r'(\d{4}-\d{2}-\d{2})')[0]
    # szybki wzór na siłe
    df['e1RM'] = df['Ciezar_kg'] * (1 + df['Powtorzenia'] / 30)
    return df

df = load_data()

# 3. interfejs - menu rozwijane
st.subheader('Analiza wybranego ćwiczenia')
lista_cwiczen = df['Cwiczenie'].unique() # pobiera unikalne cwiczenia z bazy
wybrane_cwiczenie = st.selectbox('Wybierz ćwiczenie do analizy:', lista_cwiczen)

# 4. filtrowanie i rysowanie
df_plot = df[df['Cwiczenie'] == wybrane_cwiczenie]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x = df_plot['Data'],
    y = df_plot['e1RM'],
    mode = 'lines+markers',
    name = 'e1RM (Epley)',
    line=dict(color='blue', width=3)
))

fig.update_layout(
    title_text = f'Progres siłowy: {wybrane_cwiczenie}',
    hovermode = 'x unified'
)

# 5. zamiast fig.show() lub zapisu do HTML, wrzucamy wykres na stronę
st.plotly_chart(fig, use_container_width=True)
