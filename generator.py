

# %%
import plotly.graph_objects as go
print("Silnik Plotly gotowy do akcji!")


# %%
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
# Wczytujemy nasz plik do głównego obiektu DataFrame
df = pd.read_csv('gym_tracker_export.csv', sep=';', encoding='utf-8-sig')

# Wyświetlamy strukturę danych i wykryte typy zmiennych
print('Struktura zbioru')
df.info()

# Podglądamy pierwsze 5 wierszy, żeby ocenić jakość wczytania
print('Próbka danych')
df.head()

# %%
# 1. Wczytujemy plik z pomiarami do nowej zmiennej
df_pomiary = pd.read_csv('measurement_data.csv')

# 2. Wycinamy z niej tylko dwie interesujące nas kolumny (podwójne nawiasy kwadratowe!)
df_waga = df_pomiary[['date', 'weight_kg']]

# 3. Podglądamy pierwsze 5 wierszy naszej nowej, czystej tabelki
print(df_waga.head())

# %%
# 1. Wczytujemy plik
df = pd.read_csv('gym_tracker_export.csv', sep=';', encoding='utf-8-sig')

# 2. BRUTALNE CZYSZCZENIA DANYCH
# Wyciągamy na siłę tylko wzorzec daty (4 cyfry-2 cyfry-2 cyfry) i odrzucamy resztę
df['Data'] = df['Data'].astype(str).str.extract(r'(\d{4}-\d{2}-\d{2})')[0]

# Teraz bezpiecznie konwertujemy czysty już tekst na format daty
df['Data'] = pd.to_datetime(df['Data']).dt.normalize()
# Używamy format='mixed', żeby Pandas nie wywalał się na skrótach miesięcy typu "Jun" vs "May"
df_waga['date'] = pd.to_datetime(df_waga['date'], format='mixed').dt.normalize()

# 3. Wielka Fuzja 
df_merged = pd.merge(df, df_waga, left_on='Data', right_on='date', how='left')
df_merged = df_merged.sort_values(by='Data', ascending=True).reset_index(drop=True)

# 4. Wyświetlamy wyniki
print(df_merged[['Data', 'Cwiczenie', 'Ciezar_kg', 'weight_kg']].tail(10))

# %%
import matplotlib.pyplot as plt

# 1. Liczymy Tonaż i szacowany 1RM dla KAŻDEJ serii w bazie
df_merged['Tonaz_serii'] = df_merged['Ciezar_kg'] * df_merged['Powtorzenia']
df_merged['e1RM'] = df_merged['Ciezar_kg'] * (1 + df_merged['Powtorzenia'] / 30)

# 2. Aktualizujemy nasze GRUPOWANIE o nowe statystyki
df_dzienne_podsumowanie = df_merged.groupby(['Data', 'Cwiczenie', 'weight_kg'], dropna=False).agg(
    Max_Ciezar_kg=('Ciezar_kg', 'max'),       
    Calkowity_Tonaz=('Tonaz_serii', 'sum'),
    Max_e1RM=('e1RM', 'max') 
).reset_index()

df_dzienne_podsumowanie = df_dzienne_podsumowanie.sort_values(by=['Data', 'Cwiczenie'])
print("Grupowanie zakończone sukcesem!")

# %%
import matplotlib.pyplot as plt

# 1. Filtrujemy dane dla płaskiej
df_bench = df_dzienne_podsumowanie[df_dzienne_podsumowanie['Cwiczenie'] == 'Bench Press (Barbell)']

# 2. Inicjujemy główny wykres (fig) i lewą oś Y (ax1)
fig, ax1 = plt.subplots(figsize=(12, 6))

# --- LEWA OŚ (SIŁA) ---
ax1.set_xlabel('Data treningu')
ax1.set_ylabel('Ciężar sztangi (kg)', color='blue', fontweight='bold')
line1 = ax1.plot(df_bench['Data'], df_bench['Max_Ciezar_kg'], marker='o', linestyle='--', color='gray', alpha=0.6, label='Max Ciężar (Surowy)')
line2 = ax1.plot(df_bench['Data'], df_bench['Max_e1RM'], marker='s', linestyle='-', color='blue', linewidth=2, label='Szacowany 1RM (Epley)')
ax1.tick_params(axis='y', labelcolor='blue')
ax1.grid(True, linestyle='--', alpha=0.7)

# --- PRAWA OŚ (MASA CIAŁA) ---
ax2 = ax1.twinx()  # Tworzymy brata bliźniaka dla osi Y!
ax2.set_ylabel('Masa ciała (kg)', color='red', fontweight='bold')

# DYNAMICZNY ZAKRES: Szukamy najmniejszej wagi w tabeli i odejmujemy od niej 2 kg luzu
min_waga = df_bench['weight_kg'].min() - 2
max_waga = df_bench['weight_kg'].max() + 2
ax2.set_ylim(min_waga, max_waga) # Wymuszamy nowe granice wykresu!

# Wyciągamy (filtrujemy) tylko te dni, w których waga NIE JEST pusta
maska_wagi = df_bench['weight_kg'].notna()

# Rysujemy linię tylko dla przefiltrowanych dni!
line3 = ax2.plot(df_bench['Data'][maska_wagi], df_bench['weight_kg'][maska_wagi], 
                 marker='o', linestyle='-', color='red', alpha=0.5, linewidth=2, label='Masa ciała')

# 3. Zbieramy legendy z obu osi w jedno miejsce, żeby był porządek
lines = line1 + line2 + line3
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='lower center') # Przesunąłem w dolne centrum, żeby nie zasłaniać linii

# 4. Tytuł i wyświetlenie
plt.title('Korelacja Szczytowej Siły i Masy Ciała: Wyciskanie Sztangi Leżąc', fontsize=14, fontweight='bold')

# 1. Wymuszamy, żeby podziałka (ticks) wypadała DOKŁADNIE w dniach treningowych
ax1.set_xticks(df_bench['Data'])

# 2. Obracamy napisy o 45 stopni i formatujemy je czysto (RRRR-MM-DD), żeby się nie zlewały
ax1.set_xticklabels(df_bench['Data'].dt.strftime("%Y-%m-%d"), rotation=45)


# %%
import matplotlib.pyplot as plt

# 1. ŁATAMY DZIURY (ffill musi być użyty ZANIM odfiltrujemy ćwiczenie)
df_dzienne_podsumowanie['weight_kg'] = df_dzienne_podsumowanie['weight_kg'].ffill()

# 2. FILTRUJEMY
df_front = df_dzienne_podsumowanie[df_dzienne_podsumowanie['Cwiczenie'] == 'Front Squat']

# 3. RYSUJEMY
fig, ax1 = plt.subplots(figsize=(12, 6))

# --- LEWA OŚ (TONAŻ) ---
ax1.set_xlabel('Data treningu')
ax1.set_ylabel('Całkowity Tonaż (kg)', color='blue', fontweight='bold')
line1 = ax1.plot(df_front['Data'], df_front['Calkowity_Tonaz'], marker='s', linestyle='-', color='blue', linewidth=2, label='Całkowity Tonaż')
ax1.tick_params(axis='y', labelcolor='blue')
ax1.grid(True, linestyle='--', alpha=0.7)

# Wymuszamy etykiety dat na osi X, żeby znowu nie zniknęły
ax1.set_xticks(df_front['Data'])
ax1.set_xticklabels(df_front['Data'].dt.strftime("%Y-%m-%d"), rotation=45)

# --- PRAWA OŚ (MASA CIAŁA) ---
ax2 = ax1.twinx()
ax2.set_ylabel('Masa ciała (kg)', color='red', fontweight='bold')

# Dynamiczny zakres wagi
min_waga = df_front['weight_kg'].min() - 2
max_waga = df_front['weight_kg'].max() + 2
ax2.set_ylim(min_waga, max_waga) 

# Rysujemy wagę (teraz już czysto, bez żadnych masek!)
line2 = ax2.plot(df_front['Data'], df_front['weight_kg'], marker='o', linestyle='-', color='red', linewidth=2, label='Masa ciała')
ax2.tick_params(axis='y', labelcolor='red')

# --- LEGENDA I TYTUŁ ---
lines = line1 + line2
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='lower center') 

plt.title('Korelacja Tonażu i Masy Ciała: Przysiad Przedni', fontsize=14, fontweight='bold')
plt.tight_layout() # Zabezpiecza przed ucinaniem dat na dole ekranu


# %%
import matplotlib.pyplot as plt

# 1. Lista ćwiczeń do analizy (możesz tu dodawać kolejne!)
wielka_czworka = ['Bench Press (Barbell)', 'Front Squat'] 

for cwiczenie in wielka_czworka:
    # 2. Dynamiczne filtrowanie dla konkretnego ćwiczenia
    df_plot = df_dzienne_podsumowanie[df_dzienne_podsumowanie['Cwiczenie'] == cwiczenie]
    
    # Zabezpieczenie: jeśli na liście jest ćwiczenie, którego jeszcze nie robiłeś, pętla je pominie
    if df_plot.empty:
        continue

    # 3. Rysujemy wykres (logika z piątku)
    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.set_xlabel('Data treningu')
    ax1.set_ylabel('Szacowany 1RM (kg)', color='blue', fontweight='bold')
    line1 = ax1.plot(df_plot['Data'], df_plot['Max_e1RM'], marker='s', linestyle='-', color='blue', linewidth=2, label='1RM (Epley)')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.grid(True, linestyle='--', alpha=0.7)
    
    ax1.set_xticks(df_plot['Data'])
    ax1.set_xticklabels(df_plot['Data'].dt.strftime("%Y-%m-%d"), rotation=45)

    ax2 = ax1.twinx()
    ax2.set_ylabel('Masa ciała (kg)', color='red', fontweight='bold')
    min_waga = df_plot['weight_kg'].min() - 2
    max_waga = df_plot['weight_kg'].max() + 2
    ax2.set_ylim(min_waga, max_waga) 
    
    line2 = ax2.plot(df_plot['Data'], df_plot['weight_kg'], marker='o', linestyle='-', color='red', linewidth=2, label='Masa ciała')
    ax2.tick_params(axis='y', labelcolor='red')

    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='lower center') 

    plt.title(f'Progres vs Masa Ciała: {cwiczenie}', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # 4. Automatyczny zapis na dysk zamiast wyświetlania w notatniku
    # Podmieniamy spacje na podłogi, żeby pliki miały ładne nazwy (np. raport_Front_Squat.png)
    nazwa_pliku = f"raport_{cwiczenie.replace(' ', '_')}.png"
    plt.savefig(nazwa_pliku)
    print(f"Sukces: Wygenerowano {nazwa_pliku}")
    
    # Zamykamy obiekt wykresu, żeby zwolnić RAM
    plt.close()

# %%
import matplotlib.pyplot as plt

# 1. Lista ćwiczeń do analizy (możesz tu dodawać kolejne!)
wielka_czworka = ['Bench Press (Barbell)', 'Front Squat'] 

for cwiczenie in wielka_czworka:
    # 2. Dynamiczne filtrowanie dla konkretnego ćwiczenia
    df_plot = df_dzienne_podsumowanie[df_dzienne_podsumowanie['Cwiczenie'] == cwiczenie]
    
    # Zabezpieczenie: jeśli na liście jest ćwiczenie, którego jeszcze nie robiłeś, pętla je pominie
    if df_plot.empty:
        continue

    # 3. Rysujemy wykres (logika z piątku)
    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.set_xlabel('Data treningu')
    ax1.set_ylabel('Szacowany 1RM (kg)', color='blue', fontweight='bold')
    line1 = ax1.plot(df_plot['Data'], df_plot['Max_e1RM'], marker='s', linestyle='-', color='blue', linewidth=2, label='1RM (Epley)')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.grid(True, linestyle='--', alpha=0.7)
    
    ax1.set_xticks(df_plot['Data'])
    ax1.set_xticklabels(df_plot['Data'].dt.strftime("%Y-%m-%d"), rotation=45)

    ax2 = ax1.twinx()
    ax2.set_ylabel('Masa ciała (kg)', color='red', fontweight='bold')
    min_waga = df_plot['weight_kg'].min() - 2
    max_waga = df_plot['weight_kg'].max() + 2
    ax2.set_ylim(min_waga, max_waga) 
    
    line2 = ax2.plot(df_plot['Data'], df_plot['weight_kg'], marker='o', linestyle='-', color='red', linewidth=2, label='Masa ciała')
    ax2.tick_params(axis='y', labelcolor='red')

    #Zadanie treningowe 1: Analityczny Cel (Poziom: Rozgrzewka)
    cel_kg = 0
    line_cel = [] # Pusta lista, na wypadek gdyby ćwiczenie nie miało ustawionego celu

    if cwiczenie == 'Bench Press (Barbell)':
        cel_kg = 140
    elif cwiczenie == 'Front Squat':
        cel_kg = 160

    # Rysujemy linię i zapisujemy ją do zmiennej (w nawiasach kwadratowych, tak jak line1 i line2)
    if cel_kg > 0:
        line_cel = [ax1.axhline(y = cel_kg, color = 'green', linestyle = '--', linewidth = 2, alpha = 0.7, label = f'Cel {cel_kg} kg')]

    ax1.set_xlabel('Data treningu')
    
    lines = line1 + line2 + line_cel
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='lower center') 

    plt.title(f'Progres vs Masa Ciała: {cwiczenie}', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # 4. Automatyczny zapis na dysk zamiast wyświetlania w notatniku
    # Podmieniamy spacje na podłogi, żeby pliki miały ładne nazwy (np. raport_Front_Squat.png)
    nazwa_pliku = f"raport_{cwiczenie.replace(' ', '_')}.png"
    plt.savefig(nazwa_pliku)
    print(f"Sukces: Wygenerowano {nazwa_pliku}")
    
    # Zamykamy obiekt wykresu, żeby zwolnić RAM
    plt.close()

# %%
import matplotlib.pyplot as plt
from datetime import datetime

# 1. Lista ćwiczeń do analizy (możesz tu dodawać kolejne!)
wielka_czworka = ['Bench Press (Barbell)', 'Front Squat'] 

dzisiejsza_data = datetime.now().strftime("%Y-%m-%d")

for cwiczenie in wielka_czworka:
    # 2. Dynamiczne filtrowanie dla konkretnego ćwiczenia
    df_plot = df_dzienne_podsumowanie[df_dzienne_podsumowanie['Cwiczenie'] == cwiczenie]
    
    # Zabezpieczenie: jeśli na liście jest ćwiczenie, którego jeszcze nie robiłeś, pętla je pominie
    if df_plot.empty:
        continue

    # 3. Rysujemy wykres (logika z piątku)
    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.set_xlabel('Data treningu')
    ax1.set_ylabel('Szacowany 1RM (kg)', color='blue', fontweight='bold')
    line1 = ax1.plot(df_plot['Data'], df_plot['Max_e1RM'], marker='s', linestyle='-', color='blue', linewidth=2, label='1RM (Epley)')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.grid(True, linestyle='--', alpha=0.7)
    
    ax1.set_xticks(df_plot['Data'])
    ax1.set_xticklabels(df_plot['Data'].dt.strftime("%Y-%m-%d"), rotation=45)

    ax2 = ax1.twinx()
    ax2.set_ylabel('Masa ciała (kg)', color='red', fontweight='bold')
    min_waga = df_plot['weight_kg'].min() - 2
    max_waga = df_plot['weight_kg'].max() + 2
    ax2.set_ylim(min_waga, max_waga) 
    
    line2 = ax2.plot(df_plot['Data'], df_plot['weight_kg'], marker='o', linestyle='-', color='red', linewidth=2, label='Masa ciała')
    ax2.tick_params(axis='y', labelcolor='red')

    #Zadanie treningowe 1: Analityczny Cel (Poziom: Rozgrzewka)
    cel_kg = 0
    line_cel = [] # Pusta lista, na wypadek gdyby ćwiczenie nie miało ustawionego celu

    if cwiczenie == 'Bench Press (Barbell)':
        cel_kg = 140
    elif cwiczenie == 'Front Squat':
        cel_kg = 160

    # Rysujemy linię i zapisujemy ją do zmiennej (w nawiasach kwadratowych, tak jak line1 i line2)
    if cel_kg > 0:
        line_cel = [ax1.axhline(y = cel_kg, color = 'green', linestyle = '--', linewidth = 2, alpha = 0.7, label = f'Cel {cel_kg} kg')]

    ax1.set_xlabel('Data treningu')
    
    lines = line1 + line2 + line_cel
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='lower center') 

    plt.title(f'Progres vs Masa Ciała: {cwiczenie}', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # 4. Automatyczny zapis na dysk zamiast wyświetlania w notatniku
    # Podmieniamy spacje na podłogi, żeby pliki miały ładne nazwy (np. raport_Front_Squat.png)
    nazwa_pliku = f"raport_{cwiczenie.replace(' ', '_')}_{dzisiejsza_data}.png"
    plt.savefig(nazwa_pliku)
    print(f"Sukces: Wygenerowano {nazwa_pliku}")
    
    # Zamykamy obiekt wykresu, żeby zwolnić RAM
    plt.close()

# %%
import matplotlib.pyplot as plt
from datetime import datetime

# 1. Lista ćwiczeń do analizy (możesz tu dodawać kolejne!)
wielka_czworka = ['Bench Press (Barbell)', 'Front Squat']

df_dzienne_podsumowanie = df_dzienne_podsumowanie[df_dzienne_podsumowanie['Data'] >= '2026-08-01']

dzisiejsza_data = datetime.now().strftime("%Y-%m-%d")

for cwiczenie in wielka_czworka:
    # 2. Dynamiczne filtrowanie dla konkretnego ćwiczenia
    df_plot = df_dzienne_podsumowanie[df_dzienne_podsumowanie['Cwiczenie'] == cwiczenie]
    
    # Zabezpieczenie: jeśli na liście jest ćwiczenie, którego jeszcze nie robiłeś, pętla je pominie
    if df_plot.empty:
        continue

    # 3. Rysujemy wykres (logika z piątku)
    fig, ax1 = plt.subplots(figsize=(12, 6))

    ax1.set_xlabel('Data treningu')
    ax1.set_ylabel('Szacowany 1RM (kg)', color='blue', fontweight='bold')
    line1 = ax1.plot(df_plot['Data'], df_plot['Max_e1RM'], marker='s', linestyle='-', color='blue', linewidth=2, label='1RM (Epley)')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.grid(True, linestyle='--', alpha=0.7)
    
    ax1.set_xticks(df_plot['Data'])
    ax1.set_xticklabels(df_plot['Data'].dt.strftime("%Y-%m-%d"), rotation=45)

    ax2 = ax1.twinx()
    ax2.set_ylabel('Masa ciała (kg)', color='red', fontweight='bold')
    min_waga = df_plot['weight_kg'].min() - 2
    max_waga = df_plot['weight_kg'].max() + 2
    ax2.set_ylim(min_waga, max_waga) 
    
    line2 = ax2.plot(df_plot['Data'], df_plot['weight_kg'], marker='o', linestyle='-', color='red', linewidth=2, label='Masa ciała')
    ax2.tick_params(axis='y', labelcolor='red')

    #Zadanie treningowe 1: Analityczny Cel (Poziom: Rozgrzewka)
    cel_kg = 0
    line_cel = [] # Pusta lista, na wypadek gdyby ćwiczenie nie miało ustawionego celu

    if cwiczenie == 'Bench Press (Barbell)':
        cel_kg = 140
    elif cwiczenie == 'Front Squat':
        cel_kg = 160

    # Rysujemy linię i zapisujemy ją do zmiennej (w nawiasach kwadratowych, tak jak line1 i line2)
    if cel_kg > 0:
        line_cel = [ax1.axhline(y = cel_kg, color = 'green', linestyle = '--', linewidth = 2, alpha = 0.7, label = f'Cel {cel_kg} kg')]

    ax1.set_xlabel('Data treningu')
    
    lines = line1 + line2 + line_cel
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='lower center') 

    plt.title(f'Progres vs Masa Ciała: {cwiczenie}', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # 4. Automatyczny zapis na dysk zamiast wyświetlania w notatniku
    # Podmieniamy spacje na podłogi, żeby pliki miały ładne nazwy (np. raport_Front_Squat.png)
    nazwa_pliku = f"raport_{cwiczenie.replace(' ', '_')}_{dzisiejsza_data}.png"
    plt.savefig(nazwa_pliku)
    print(f"Sukces: Wygenerowano {nazwa_pliku}")
    
    # Zamykamy obiekt wykresu, żeby zwolnić RAM
    plt.close()

# %%
import matplotlib.pyplot as plt

# Lista ćwiczeń do analizy (możesz tu dodawać kolejne!)
wielka_czworka = ['Bench Press (Barbell)', 'Front Squat', 'Romanian Deadlift (Barbell)', 'Overhead Press (Smith Machine)']

# 1. Tworzymy wielkie płótno i siatkę 2x2
fig, axes = plt.subplots(nrows = 2, ncols = 2, figsize = (16, 10))

# 2. Spłaszczamy siatkę, żeby móc łatwo iterować po okienkach (od 0 do 3)
axes_flat = axes.flatten()

# Odpalamy silnik - używamy enumerate, żeby mieć indeks (i) od 0 do 3
for i, cwiczenie in enumerate(wielka_czworka):

    # Wybieramy konkretne okienko z naszej siatki
    ax1 = axes_flat[i]

    # Filtrujemy dane
    df_plot = df_dzienne_podsumowanie[df_dzienne_podsumowanie['Cwiczenie'] == cwiczenie]

    if df_plot.empty:
        ax1.set_title(f'Brak danych: {cwiczenie}')
        continue

    # --- LEWA OŚ (SIŁA) ---
    line1 = ax1.plot(df_plot['Data'], df_plot['Max_e1RM'], marker='s', linestyle='-', color='blue', linewidth=2, label='1RM Epley')
    ax1.set_ylabel('Szacowany 1RM (kg)', color='blue', fontweight='bold')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.grid(True, linestyle='-', alpha = 0.7)

    # Ustawiamy skrócony format dat, żeby zmieściły się w mniejszych okienkach
    ax1.set_xticks(df_plot['Data'])
    ax1.set_xticklabels(df_plot['Data'].dt.strftime("%m-%d"), rotation=45)

    # --- PRAWA OŚ (MASA CIAŁA) ---
    ax2 = ax1.twinx()
    min_waga = df_plot['weight_kg'].min() - 2
    max_waga = df_plot['weight_kg'].max() + 2
    ax2.set_ylim(min_waga, max_waga)

    line2 = ax2.plot(df_plot['Data'], df_plot['weight_kg'], marker='o', linestyle='-', color='red', linewidth=2, label='Masa ciała')
    ax2.set_ylabel('Masa ciała (kg)', color='red', fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='red')

    # Kosmetyka pojedynczego okienka
    ax1.set_title(cwiczenie, fontsize=12, fontweight='bold')

# 3. Finalizacja całego Dashboardu
plt.tight_layout() # Magiczna funkcja, która pilnuje, żeby wykresy na siebie nie najeżdżały!

nazwa_pliku = 'Dashboard_Wielka_Czworka.png'
plt.savefig(nazwa_pliku)
print(f"Sukces: Wygenerowano {nazwa_pliku}")

plt.close()

# %%
import matplotlib.pyplot as plt

# Lista ćwiczeń do analizy (możesz tu dodawać kolejne!)
wielka_czworka = ['Bench Press (Barbell)', 'Front Squat', 'Romanian Deadlift (Barbell)', 'Overhead Press (Smith Machine)']

# 1. Tworzymy wielkie płótno i siatkę 2x2
fig, axes = plt.subplots(nrows = 2, ncols = 2, figsize = (16, 10))

# 2. Spłaszczamy siatkę, żeby móc łatwo iterować po okienkach (od 0 do 3)
axes_flat = axes.flatten()

# Odpalamy silnik - używamy enumerate, żeby mieć indeks (i) od 0 do 3
for i, cwiczenie in enumerate(wielka_czworka):

    # Wybieramy konkretne okienko z naszej siatki
    ax1 = axes_flat[i]

    # Filtrujemy dane
    df_plot = df_dzienne_podsumowanie[df_dzienne_podsumowanie['Cwiczenie'] == cwiczenie]

    # --- NOWOŚĆ: Obliczamy średnią kroczącą z 2 ostatnich treningów ---
    # min_periods=1 sprawia, że pierwszy trening nie będzie pusty
    df_plot['Trend_1RM'] = df_plot['Max_e1RM'].rolling(window=2, min_periods = 1).mean()
    
    if df_plot.empty:
        ax1.set_title(f'Brak danych: {cwiczenie}')
        continue

    # --- LEWA OŚ (SIŁA) ---
    line1 = ax1.plot(df_plot['Data'], df_plot['Max_e1RM'], marker='s', linestyle='-', color='blue', linewidth=2, label='1RM Epley')

    min_1rm = df_plot['Max_e1RM'].min() - 5
    max_1rm = df_plot['Max_e1RM'].max() + 5
    ax1.set_ylim(min_1rm, max_1rm)
    
    # --- NOWOŚĆ: Rysujemy nasz wygładzony trend (np. jasnoniebieski, przerywany) ---
    line_trend = ax1.plot(df_plot['Data'], df_plot['Trend_1RM'], linestyle='--', color='cyan', linewidth=2, label='Trend 1RM')
    
    ax1.set_ylabel('Szacowany 1RM (kg)', color='blue', fontweight='bold')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.grid(True, linestyle='-', alpha = 0.7)

    # Ustawiamy skrócony format dat, żeby zmieściły się w mniejszych okienkach
    ax1.set_xticks(df_plot['Data'])
    ax1.set_xticklabels(df_plot['Data'].dt.strftime("%m-%d"), rotation=45)

    # --- PRAWA OŚ (MASA CIAŁA) ---
    ax2 = ax1.twinx()
    min_waga = df_plot['weight_kg'].min() - 2
    max_waga = df_plot['weight_kg'].max() + 2
    ax2.set_ylim(min_waga, max_waga)

    line2 = ax2.plot(df_plot['Data'], df_plot['weight_kg'], marker='o', linestyle='-', color='red', linewidth=2, label='Masa ciała')
    ax2.set_ylabel('Masa ciała (kg)', color='red', fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='red')

    # Kosmetyka pojedynczego okienka
    ax1.set_title(cwiczenie, fontsize=12, fontweight='bold')

    # Legenda
    lines = line1 + line2 + line_trend
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper center')

# 3. Finalizacja całego Dashboardu
plt.tight_layout() # Magiczna funkcja, która pilnuje, żeby wykresy na siebie nie najeżdżały!

nazwa_pliku = 'Dashboard_Wielka_Czworka_Wygladzona.png'
plt.savefig(nazwa_pliku)
print(f"Sukces: Wygenerowano {nazwa_pliku}")

plt.close()

# %%
# Korelacja Pearsona
import matplotlib.pyplot as plt

# Lista ćwiczeń do analizy (możesz tu dodawać kolejne!)
wielka_czworka = ['Bench Press (Barbell)', 'Front Squat', 'Romanian Deadlift (Barbell)', 'Overhead Press (Smith Machine)']

# 1. Tworzymy wielkie płótno i siatkę 2x2
fig, axes = plt.subplots(nrows = 2, ncols = 2, figsize = (16, 10))

# 2. Spłaszczamy siatkę, żeby móc łatwo iterować po okienkach (od 0 do 3)
axes_flat = axes.flatten()

# Odpalamy silnik - używamy enumerate, żeby mieć indeks (i) od 0 do 3
for i, cwiczenie in enumerate(wielka_czworka):

    # Wybieramy konkretne okienko z naszej siatki
    ax1 = axes_flat[i]

    # Filtrujemy dane
    df_plot = df_dzienne_podsumowanie[df_dzienne_podsumowanie['Cwiczenie'] == cwiczenie]

    # --- NOWOŚĆ: Obliczamy średnią kroczącą z 2 ostatnich treningów ---
    # min_periods=1 sprawia, że pierwszy trening nie będzie pusty
    df_plot['Trend_1RM'] = df_plot['Max_e1RM'].rolling(window=2, min_periods = 1).mean()
    
    if df_plot.empty:
        ax1.set_title(f'Brak danych: {cwiczenie}')
        continue

    # --- NOWOŚĆ: Wyliczamy korelację Pearsona ---
    # Funkcja .corr() w locie porównuje dwie kolumny
    korelacja = df_plot['weight_kg'].corr(df_plot['Max_e1RM'])

    # Zabezpieczenie: jeśli danych jest za mało, Pandas zwróci NaN (Not a Number)
    import pandas as pd
    if pd.isna(korelacja):
        korelacja_tekst = 'N/A'
    else:
        korelacja_tekst = f'r = {korelacja:.2f}' # do dwóch miejsc po przecinku

    # --- LEWA OŚ (SIŁA) ---
    line1 = ax1.plot(df_plot['Data'], df_plot['Max_e1RM'], marker='s', linestyle='-', color='blue', linewidth=2, label='1RM Epley')

    min_1rm = df_plot['Max_e1RM'].min() - 5
    max_1rm = df_plot['Max_e1RM'].max() + 5
    ax1.set_ylim(min_1rm, max_1rm)
    
    # --- NOWOŚĆ: Rysujemy nasz wygładzony trend (np. jasnoniebieski, przerywany) ---
    line_trend = ax1.plot(df_plot['Data'], df_plot['Trend_1RM'], linestyle='--', color='cyan', linewidth=2, label='Trend 1RM')
    
    ax1.set_ylabel('Szacowany 1RM (kg)', color='blue', fontweight='bold')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.grid(True, linestyle='-', alpha = 0.7)

    # Ustawiamy skrócony format dat, żeby zmieściły się w mniejszych okienkach
    ax1.set_xticks(df_plot['Data'])
    ax1.set_xticklabels(df_plot['Data'].dt.strftime("%d-%m"), rotation=45)
    ax1.set_xlabel('Data treningu', fontweight='bold')

    # --- PRAWA OŚ (MASA CIAŁA) ---
    ax2 = ax1.twinx()
    min_waga = df_plot['weight_kg'].min() - 2
    max_waga = df_plot['weight_kg'].max() + 2
    ax2.set_ylim(min_waga, max_waga)

    line2 = ax2.plot(df_plot['Data'], df_plot['weight_kg'], marker='o', linestyle='-', color='red', linewidth=2, label='Masa ciała')
    ax2.set_ylabel('Masa ciała (kg)', color='red', fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='red')

    # Kosmetyka pojedynczego okienka
    ax1.set_title(f'{cwiczenie} (Pearson): {korelacja_tekst}', fontsize=12, fontweight='bold')

    # Legenda
    lines = line1 + line2 + line_trend
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper center')

# 3. Finalizacja całego Dashboardu
plt.tight_layout() # Magiczna funkcja, która pilnuje, żeby wykresy na siebie nie najeżdżały!

nazwa_pliku = 'Dashboard_Wielka_Czworka_Korelacja.png'
plt.savefig(nazwa_pliku)
print(f"Sukces: Wygenerowano {nazwa_pliku}")

plt.close()

# %%
# Regresja liniowa - czy mamy wzrost czy spadek na wykresie
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates

# Lista ćwiczeń do analizy (możesz tu dodawać kolejne!)
wielka_czworka = ['Bench Press (Barbell)', 'Front Squat', 'Romanian Deadlift (Barbell)', 'Overhead Press (Smith Machine)']

# 1. Tworzymy wielkie płótno i siatkę 2x2
fig, axes = plt.subplots(nrows = 2, ncols = 2, figsize = (16, 10))

# 2. Spłaszczamy siatkę, żeby móc łatwo iterować po okienkach (od 0 do 3)
axes_flat = axes.flatten()

# Odpalamy silnik - używamy enumerate, żeby mieć indeks (i) od 0 do 3
for i, cwiczenie in enumerate(wielka_czworka):

    # Wybieramy konkretne okienko z naszej siatki
    ax1 = axes_flat[i]

    # Filtrujemy dane
    df_plot = df_dzienne_podsumowanie[df_dzienne_podsumowanie['Cwiczenie'] == cwiczenie]

    # --- NOWOŚĆ: Obliczamy średnią kroczącą z 2 ostatnich treningów ---
    # min_periods=1 sprawia, że pierwszy trening nie będzie pusty
    df_plot['Trend_1RM'] = df_plot['Max_e1RM'].rolling(window=2, min_periods = 1).mean()
    
    if df_plot.empty:
        ax1.set_title(f'Brak danych: {cwiczenie}')
        continue

    # --- REGRESJA LINIOWA (Kryształowa Kula) ---
    # 1. Tłumaczymy daty na format liczbowy, żeby matematyka mogła zadziałać
    x_num = mdates.date2num(df_plot['Data'])
    y_1rm = df_plot['Max_e1RM']

    # 2. Trenujemy model (wielomian 1 stopnia, czyli prosta linia)
    # np.polyfit wyliczy nam kąt nachylenia i punkt startowy
    wspolczynniki = np.polyfit(x_num, y_1rm, 1)
    model_predykcyjny = np.poly1d(wspolczynniki)

    # 3. Rysujemy naszą linię predykcji na wykresie (np. gruba magenta)
    ax1.plot(df_plot['Data'], model_predykcyjny(x_num), color = 'magenta', linestyle = ':', linewidth = 3, label = 'Model predykcyjny')
    
    # --- NOWOŚĆ: Wyliczamy korelację Pearsona ---
    # Funkcja .corr() w locie porównuje dwie kolumny
    korelacja = df_plot['weight_kg'].corr(df_plot['Max_e1RM'])

    # Zabezpieczenie: jeśli danych jest za mało, Pandas zwróci NaN (Not a Number)
    import pandas as pd
    if pd.isna(korelacja):
        korelacja_tekst = 'N/A'
    else:
        korelacja_tekst = f'r = {korelacja:.2f}' # do dwóch miejsc po przecinku

    # --- LEWA OŚ (SIŁA) ---
    line1 = ax1.plot(df_plot['Data'], df_plot['Max_e1RM'], marker='s', linestyle='-', color='blue', linewidth=2, label='1RM Epley')

    min_1rm = df_plot['Max_e1RM'].min() - 5
    max_1rm = df_plot['Max_e1RM'].max() + 5
    ax1.set_ylim(min_1rm, max_1rm)
    
    # --- NOWOŚĆ: Rysujemy nasz wygładzony trend (np. jasnoniebieski, przerywany) ---
    line_trend = ax1.plot(df_plot['Data'], df_plot['Trend_1RM'], linestyle='--', color='cyan', linewidth=2, label='Trend 1RM')
    
    ax1.set_ylabel('Szacowany 1RM (kg)', color='blue', fontweight='bold')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.grid(True, linestyle='-', alpha = 0.7)

    # Ustawiamy skrócony format dat, żeby zmieściły się w mniejszych okienkach
    ax1.set_xticks(df_plot['Data'])
    ax1.set_xticklabels(df_plot['Data'].dt.strftime("%d-%m"), rotation=45)
    ax1.set_xlabel('Data treningu', fontweight='bold')

    # --- PRAWA OŚ (MASA CIAŁA) ---
    ax2 = ax1.twinx()
    min_waga = df_plot['weight_kg'].min() - 2
    max_waga = df_plot['weight_kg'].max() + 2
    ax2.set_ylim(min_waga, max_waga)

    line2 = ax2.plot(df_plot['Data'], df_plot['weight_kg'], marker='o', linestyle='-', color='red', linewidth=2, label='Masa ciała')
    ax2.set_ylabel('Masa ciała (kg)', color='red', fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='red')

    # Kosmetyka pojedynczego okienka
    ax1.set_title(f'{cwiczenie} (Pearson): {korelacja_tekst}', fontsize=12, fontweight='bold')

    # Legenda
    lines = line1 + line2 + line_trend
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper center')

# 3. Finalizacja całego Dashboardu
plt.tight_layout() # Magiczna funkcja, która pilnuje, żeby wykresy na siebie nie najeżdżały!

nazwa_pliku = 'Dashboard_Wielka_Czworka_Korelacja_Regresja.png'
plt.savefig(nazwa_pliku)
print(f"Sukces: Wygenerowano {nazwa_pliku}")

plt.close()

# %%
# Interaktywny wykres w html
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# 1. Wybieramy jedno ćwiczenie
cwiczenie = 'Front Squat'
df_plot = df_dzienne_podsumowanie[df_dzienne_podsumowanie['Cwiczenie'] == cwiczenie]

# 2. Tworzymy obiekt wykresu z dwiema osiami Y (lewa: siła, prawa: waga)
fig = make_subplots(specs=[[{'secondary_y': True}]])

# 3. Folia nr 1: Szacowany 1RM (lewa oś)
fig.add_trace(
    go.Scatter(
        x=df_plot['Data'], y=df_plot['Max_e1RM'],
        mode = 'lines+markers', name = '1RM (Epley)',
        line = dict(color='blue', width = 3)
    ),
    secondary_y=False,
)

# 4. Folia nr 2: Masa ciała (prawa oś)
fig.add_trace(
    go.Scatter(
        x=df_plot['Data'], y=df_plot['weight_kg'],
        mode = 'lines+markers', name = 'Masa ciała)',
        line = dict(color='blue', width = 3)
    ),
    secondary_y=False,
)

# 5. Kosmetyka i magia interaktywności
fig.update_layout(
    title_text = f'Interaktywna analiza {cwiczenie}',
    hovermode = 'x unified'
)

# 6. Eksport do niezależnego pliku HTML!
nazwa_pliku = 'Front_Squat_interaktywny.html'
fig.write_html(nazwa_pliku)
print(f'Sukces! Zbudowano raport webowy: {nazwa_pliku}')


# %%
# Interaktwny wykres 2x2 w html (ta wielka czwórka)
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd

wielka_czworka = ['Bench Press (Barbell)', 'Front Squat', 'Romanian Deadlift (Barbell)', 'Overhead Press (Smith Machine)']

# 1. Tworzymy matrycę 2x2 - musimy zdefiniować, że KAZDE okienko ma prawą oś Y
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=wielka_czworka,
    specs=[[{'secondary_y': True}, {'secondary_y': True}],
           [{'secondary_y': True}, {'secondary_y': True}]]
)

# 2. Odpalamy pętlę po liście ćwiczeń
for i, cwiczenie in enumerate(wielka_czworka):

    # Inżynieryjna matematyka: zamiana indeksu (0-3) na pozycję w siatce 2x2 (indeksowane od 1!)
    rzad = (i // 2) + 1
    kolumna = (i % 2) +1

    df_plot = df_dzienne_podsumowanie[df_dzienne_podsumowanie['Cwiczenie'] == cwiczenie].copy()

    if df_plot.empty:
        continue

    # Dodajemy wygładzony trend
    df_plot['Trend_1RM'] = df_plot['Max_e1RM'].rolling(window = 2, min_periods=1).mean()

    # --- FOLIA 1: Surowy 1RM (Lewa Oś) ---
    fig.add_trace(
        go.Scatter( x=df_plot['Data'], y=df_plot['Max_e1RM'],
                    mode='lines+markers', name=f'1RM dla ({cwiczenie})',
                    line=dict(color='blue', width = 2)),
        row = rzad, col = kolumna, secondary_y=False            
    )

    # --- FOLIA 2: Wygładzony Trend (Lewa Oś) ---
    fig.add_trace(
        go.Scatter( x=df_plot['Data'], y=df_plot['Trend_1RM'],
                    mode='lines', name=f'Trend dla ({cwiczenie})',
                    line=dict(color='cyan', dash='dash', width=2)),
        row = rzad, col = kolumna, secondary_y=False            
    )

    # --- FOLIA 3: Masa Ciała (Prawa Oś) ---
    fig.add_trace(
        go.Scatter( x=df_plot['Data'], y=df_plot['weight_kg'],
                    mode='lines+markers', name=f'Waga dla ({cwiczenie})',
                    line=dict(color='red', width = 2)),
        row = rzad, col = kolumna, secondary_y=True            
    )

    # Blokujemy osie Y, żeby uniknąć "kłamstwa skali"
    min_1rm = df_plot['Max_e1RM'].min() - 5
    max_1rm = df_plot['Max_e1RM'].max() + 5
    fig.update_yaxes(range=[min_1rm, max_1rm], row = rzad, col = kolumna, secondary_y=False)

    min_waga = df_plot['weight_kg'].min() - 2
    max_waga = df_plot['weight_kg'].max() + 2
    fig.update_yaxes(range=[min_waga, max_waga], row = rzad, col = kolumna, secondary_y=True)

# 3. Kosmetyka całego płótna    
fig.update_layout(
    height=800,
    width = 1400,
    title_text = "Centrum dowodzenia",
    hovermode = 'x unified',
    showlegend = False # Wyłączamy legendę
)

# 4. Eksport do webowego formatu
nazwa_pliku = 'Wielka_Czworka_interaktywna.html'
fig.write_html(nazwa_pliku)
print(f'Sukces! Zbudowano raport: {nazwa_pliku}')

# %%
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd

wielka_czworka = ['Bench Press (Barbell)', 'Front Squat', 'Romanian Deadlift (Barbell)', 'Overhead Press (Smith Machine)']

# 1. Filtrujemy listę, żeby upewnić się, że mamy dane dla każdego ćwiczenia
obecne_cwiczenie = [c for c in wielka_czworka if not df_dzienne_podsumowanie[df_dzienne_podsumowanie['Cwiczenie'] == c].empty]

# 2. Tworzymy jedno duże płótno z podwójną osią Y
fig = make_subplots(specs=[[{'secondary_y': True}]])

buttons = []
warstwy = 3
liczba_warstw = len(obecne_cwiczenie) * warstwy

# 3. Odpalamy pętlę ładującą wszystkie dane
for i, cwiczenie in enumerate(obecne_cwiczenie):
    df_plot = df_dzienne_podsumowanie[df_dzienne_podsumowanie['Cwiczenie'] == cwiczenie].copy()

    # Dodajemy wygładzony trend
    df_plot['Trend_1RM'] = df_plot['Max_e1RM'].rolling(window=2, min_periods=1).mean()

    # Pierwsze ćwiczenie na liście jest widoczne od razu, reszta czeka w ukryciu
    czy_widoczne = (i == 0)

    # --- FOLIA 1: Surowy 1RM ---
    fig.add_trace(
        go.Scatter(x = df_plot['Data'], y = df_plot['Max_e1RM'],
                    mode = 'lines', name='1RM Epley',
                    line=dict(color = 'blue', width=2), visible = czy_widoczne),
        secondary_y=False
    )

    # --- FOLIA 2: Wygładzony Trend ---
    fig.add_trace(
        go.Scatter(x = df_plot['Data'], y = df_plot['Trend_1RM'],
                    mode = 'lines', name='Trend 1RM',
                    line=dict(color = 'cyan', dash = 'dash', width=2), visible = czy_widoczne),
        secondary_y=False
    )

    # --- FOLIA 3: Masa Ciała ---
    fig.add_trace(
        go.Scatter(x = df_plot['Data'], y = df_plot['weight_kg'],
                    mode = 'lines + markers', name='Masa ciała',
                    line=dict(color = 'red', width=2), visible = czy_widoczne),
        secondary_y=True
    )

    # 4. Tworzymy logikę przełącznika dla tego ćwiczenia
    # Tworzymy listę pełną "False", a potem zapalamy "True" tylko dla 3 warstw tego ćwiczenia
    widocznosc = [False] * liczba_warstw
    widocznosc[i*warstwy : (i+1)*warstwy] = [True] * warstwy

    # 5. Definiujemy, co się stanie po kliknięciu w menu
    button = dict(
        label = cwiczenie, # Nazwa menu
        method = 'update', # metoda aktualizacji
        args = [{'visible': widocznosc},        # przełącza warstwy    
                {'title': f'Analiza {cwiczenie}'}] # zmienia dynamicznie tytuł
    )
    buttons.append(button)

# 6. Dodajemy interfejs (Dropdown) do wykresu
fig.update_layout(
    updatemenus = [dict(
        active = 0,
        buttons = buttons,
        direction = 'down',
        x=0.01,
        xanchor = 'left',
        y=1.15,
        yanchor = 'top',
        bgcolor = 'white',
        bordercolor = 'black',
        borderwidth = 1
    )],
    height = 600,
    width = 1200,
    title_text=f'Analiza {obecne_cwiczenie[0]}',
    hovermode = 'x unified'
)

# Optymalizujemy zakresy dla lepszej czytelności po przełączaniu
fig.update_yaxes(title_text = 'Siła (kg)', secondary_y=False, color='blue', title_font=dict(weight='bold'))
fig.update_yaxes(title_text = 'Masa (kg)', secondary_y=True, color='red', title_font=dict(weight='bold'))

# eksport 
nazwa_pliku = 'Dashboard_z_menu.html'
fig.write_html(nazwa_pliku)
print(f'Wow, wygenerowano: {nazwa_pliku}')


# %%
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime

# 1. Wybieramy ćwiczenie i nasz cel
cwiczenie = 'Bench Press (Barbell)'
cel_kg = 140.0

# 2. Filtrujemy dane i kopiujemy, żeby nie psuć głównej tabeli
df_ml = df_dzienne_podsumowanie[df_dzienne_podsumowanie['Cwiczenie'] == cwiczenie].copy()
df_ml = df_ml.dropna(subset=['Max_e1RM', 'Data'])

# 3. Przygotowanie danych dla Scikit-Learn
# Algorytmy ML nie rozumieją dat, zamieniamy je na liczby ciągłe
df_ml['Data_liczbowo'] = df_ml['Data'].apply(lambda x: x.toordinal())

X = df_ml[['Data_liczbowo']] # model wymaga tabeli 2d - cechy
y = df_ml['Max_e1RM'] # cel - to co chcemy przewidzieć

# 4. Inicjalizacja i trening modelu sztucznej inteligencji
model = LinearRegression()
model.fit(X, y) # jakaś matematyczna magia

# 5. Wyciągamy statystyki z modelu
# Równanie prostej: y = a * x + b
wspolczynnik_wzostu = model.coef_[0] # Nasze 'a' (ile kg siły średnio przybywa dziennie)
punkt_startowy = model.intercept_ # nasze 'b'

# 6. Predykcja: Kiedy pęknie cel?
if wspolczynnik_wzostu > 0:
    # Obliczamy 'x' dla naszego 'y' (celu)
    przewidywany_dzien_liczbowo = (cel_kg - punkt_startowy) / wspolczynnik_wzostu

    # Zamieniamy twardą matematykę z powrotem na ludzką datę
    data_celu = datetime.fromordinal(int(przewidywany_dzien_liczbowo))

    print(f'Raport predykcyjny ML: {cwiczenie}')
    print(f'Obecne tempo wzrostu: {wspolczynnik_wzostu * 7:.2f} kilo na tydzień')
    print(f'Prognozowana data osiągnięcia {cel_kg} kg to {data_celu.strftime("%Y-%m-%d")}')

else:
    print('Algorytm wykrył stagnację lub spadki, potrzebujesz zbudować siłę, aby zadziałało')    

# %%
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime

# 1. Wybieramy ćwiczenie i nasz cel
cwiczenie = 'Romanian Deadlift (Barbell)'
cel_kg = 180.0

# 2. Filtrujemy dane i kopiujemy, żeby nie psuć głównej tabeli
df_ml = df_dzienne_podsumowanie[df_dzienne_podsumowanie['Cwiczenie'] == cwiczenie].copy()
df_ml = df_ml.dropna(subset=['Max_e1RM', 'Data'])

# 3. Przygotowanie danych dla Scikit-Learn
# Algorytmy ML nie rozumieją dat, zamieniamy je na liczby ciągłe
df_ml['Data_liczbowo'] = df_ml['Data'].apply(lambda x: x.toordinal())

X = df_ml[['Data_liczbowo']] # model wymaga tabeli 2d - cechy
y = df_ml['Max_e1RM'] # cel - to co chcemy przewidzieć

# 4. Inicjalizacja i trening modelu sztucznej inteligencji
model = LinearRegression()
model.fit(X, y) # jakaś matematyczna magia

# 5. Wyciągamy statystyki z modelu
# Równanie prostej: y = a * x + b
wspolczynnik_wzostu = model.coef_[0] # Nasze 'a' (ile kg siły średnio przybywa dziennie)
punkt_startowy = model.intercept_ # nasze 'b'

# 6. Predykcja: Kiedy pęknie cel?
if wspolczynnik_wzostu > 0:
    # Obliczamy 'x' dla naszego 'y' (celu)
    przewidywany_dzien_liczbowo = (cel_kg - punkt_startowy) / wspolczynnik_wzostu

    # Zamieniamy twardą matematykę z powrotem na ludzką datę
    data_celu = datetime.fromordinal(int(przewidywany_dzien_liczbowo))

    print(f'Raport predykcyjny ML: {cwiczenie}')
    print(f'Obecne tempo wzrostu: {wspolczynnik_wzostu * 7:.2f} kilo na tydzień')
    print(f'Prognozowana data osiągnięcia {cel_kg} kg to {data_celu.strftime("%Y-%m-%d")}')

else:
    print('Algorytm wykrył stagnację lub spadki, potrzebujesz zbudować siłę, aby zadziałało')    

# %%
import plotly.graph_objects as go
import pandas as pd

# 1. Używamy głównej, połączonej tabeli. 
# Wyrzucamy 'Cardio' i 'Rozgrzewka', żeby nie zaburzały nam czystych proporcji siłowych
maska_treningowa = ~df_merged['Partia_miesniowa'].isin(['Cardio', 'Rozgrzewka'])
df_radar = df_merged[maska_treningowa].copy()

# 2. Liczymy objętość (ilość serii) na każdą partię
# Każdy wiersz w logach Hevy to jedna seria, więc wystarczy je zliczyć funkcją .size()
objetosc_partii = df_radar.groupby('Partia_miesniowa').size().reset_index(name='Liczba_Serii')

# 3. Wyciągamy dane do list
kategorie = objetosc_partii['Partia_miesniowa'].tolist()
wartosci = objetosc_partii['Liczba_Serii'].tolist()

# Trik dla Plotly: zamykamy obwód pajęczyny, dodając pierwszy element na sam koniec list
kategorie.append(kategorie[0])
wartosci.append(wartosci[0])

# 4. Tworzymy obiekt wykresu pajęczynowego
fig = go.Figure()

fig.add_trace(go.Scatterpolar(
    r = wartosci,
    theta = kategorie,
    fill='toself',
    name='Seria robocza',
    line= dict(color = 'magenta', width=3),
    fillcolor='rgba (255,0,255,0.3)' # przezroczysty fiolet
))

# 5. Kosmetyka i siatka radaru
fig.update_layout(
    polar = dict(
        radialaxis = dict(
            visible = True,
            range = [0, max(wartosci) + 10] # dynamicznie dopasowuje skale do ulubionej partii
        )
    ),
    title_text = 'Wykres pajęczynowy, ilośc serii, licznik objętości, itp.',
    title_font = dict(size=10, color='magenta', weight='bold'),
    showlegend = False,
    height = 700,
    width = 900
)

# 6. Eksport
nazwa_pliku = 'Dashboard_radar_sylwetki.png'
fig.write_html(nazwa_pliku)
print(f'Wow, wygenerowano: {nazwa_pliku}')


# %%
import plotly.graph_objects as go
import pandas as pd

# 1. autorski silnik mapujący, można go w przyszłości dowolnie rozbudowywać o kolejne ćwiczenia
slownik_asyst = {
    'Bench Press (Barbell)': {'Klatka': 1.0, 'Triceps': 0.5, 'Barki': 0.5},
    'Front Squat': {'Nogi': 1.0, 'Brzuch': 0.5, 'Plecy': 0.5},
    'Romanian Deadlift': {'Nogi': 1.0, 'Plecy': 1.0, 'Brzuch': 0.5},
    'Overhead Press (Smith Machine)': {'Barki': 1.0, 'Triceps': 0.5}
}

# Wyrzucamy puste przebiegi
maska_treningowa = ~df_merged['Partia_miesniowa'].isin(['Cardio', 'Rozgrzewka', 'Brak kategorii'])
df_radar = df_merged[maska_treningowa].copy()

# 2. Inicjalizacja pustego koszyka na obliczenia
prawdziwa_objetosc = {}

# 3. Pętla przeliczająca serie
for index, row in df_radar.iterrows():
    cwiczenie = row['Cwiczenie']
    partia_glowna = row['Partia_miesniowa']

    # Jeśli ćwiczenie jest w naszym słowniku, rozbijamy punkty
    if cwiczenie in slownik_asyst:
        for partia, punkty in slownik_asyst[cwiczenie].items():
            # .get(partia, 0) pobiera obecną wartość, a jeśli jej nie ma, wstawia 0
            prawdziwa_objetosc[partia] = prawdziwa_objetosc.get(partia, 0) + punkty

    else:
        # Jeśli ćwiczenia nie ma w słowniku, dajemy 1.0 punkt na główną partię
        prawdziwa_objetosc[partia_glowna] = prawdziwa_objetosc.get(partia_glowna, 0) + 1.0

# 4. Pakujemy wyliczone dane z powrotem do formatu zrozumiałego dla wykresu
kategorie = list(prawdziwa_objetosc.keys())
wartosci = list(prawdziwa_objetosc.values())

# Zamykamy obwód pajęczyny (wymóg Plotly)
kategorie.append(kategorie[0])
wartosci.append(wartosci[0])

# 5. Generujemy Ostateczny Radar
fig = go.Figure()

fig.add_trace(go.Scatterpolar(
    r = wartosci,
    theta=kategorie,
    fill = 'toself',
    name = 'Faktyczne zaangażowanie',
    line = dict(color = 'cyan', width = 3),
    fillcolor = 'rgba(0,255,255,0.3)'  
))

fig.update_layout(
    polar = dict(
        radialaxis = dict(
            visible = True,
            range = [0, max(wartosci) + 10]
        )
    ),
    title_text = 'Prawdziwy radar sylwetki (z uwględnieniem tych asyst i wag)',
    title_font = dict(size = 18, color='cyan', weight = 'bold'),
    showlegend = False,
    height = 700,
    width = 900 
)

# standardowy eksport
nazwa_pliku = 'index.html'
fig.write_html(nazwa_pliku)
print(f'Super, utworzono {nazwa_pliku}')




