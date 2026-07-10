import json
import os
import csv
import sqlite3

class BodyWeightLog:
    def __init__(self, date, weight, notes=""):
        self.date = date
        self.weight = weight
        self.notes = notes

    def show_info(self):
        print(f"[{self.date}] Waga: {self.weight}kg | Notatki: {self.notes}")

    def save_to_json(self):
        # 1. Pakujemy pomiar w słownik
        weight_data = {
                "date": self.date,
                "weight": self.weight,
                "notes": self.notes
        }

        # 2. Definiujemy nazwę naszego folderu na logi
        folder_name ="logs"

        # 3. Jeśli folder 'logs' nie istnieje w naszym projekcie, Python go tworzy    
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        # 3. worzymy pełną ścieżkę do pliku (np. logs/waga_2026-07-03.json)
        filename = f"Waga_{self.date}.json"
        filepath = os.path.join(folder_name, filename)

        # 4. Zapisujemy plik używając nowej ścieżki
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(weight_data, file, indent=4, ensure_ascii=False)

        print(f"Zapisano wagę {self.weight} w folderze {filepath}")
        pass



class TrainingSet:
    # To jest konstruktor - odpala się przy tworzeniu każdej nowej serii
    def __init__(self, exercise_name, weight, reps):
        self.exercise_name = exercise_name
        self.weight = weight
        self.reps = reps

    # METODA 1: Wyświetlanie ładnego komunikatu
    def show_info(self):
        print(f"Ćwiczenie: {self.exercise_name} | {self.weight}kg x {self.reps}powtórzenia.")

    # METODA 2: Obliczanie objętości (TUTAJ TWOJE ZADANIE)
    def calculate_volume(self):
        return self.weight * self.reps
        pass

# --- TESTOWANIE W PRAKTYCE ---

# Tworzymy konkretne obiekty (Twoje serie)
#set_1 = TrainingSet("Bench Press", 80, 8)
#set_2 = TrainingSet("Front Squat", 100, 6)
#set_3 = TrainingSet("RDL", 120, 4)

# Odpalamy gotową metodę
#set_1.show_info()
#set_2.show_info()
#set_3.show_info()

# Testujemy Twoją metodę calculate_volume()
#print(f"Objętość RDL: {set_3.calculate_volume()} kg")

# -----------------------------------------------------

class Workout:
    def __init__(self, date, target_muscle):
        self.date = date
        self.target_muscle = target_muscle
        # Tworzymy listę do której będziemy wrzucać obiekty, klasy TrainingSet
        self.sets = []
        
    def add_set(self, training_set):
        #Ta metoda dorzuca nową serię do naszej listy
        self.sets.append(training_set)
        print(f"Dodano nową serię: {training_set.exercise_name} do treningu z dnia: {self.date}.")

    def calculate_total_volume(self):
        total_volume = 0
        # Pętla przechodzi przez każdy element na liście 'self.sets'
        for seria in self.sets:
            # Do obecnej sumy dodajemy wynik obliczony przez pojedynczą serię
            total_volume += seria.calculate_volume()
        return total_volume

    def save_to_json(self):
        # 1. Tworzymy główny słownik z informacjami o sesji 
        workout_data = {
            "date": self.date,
            "target_muscle": self.target_muscle,
            "total_tonnage": self.calculate_total_volume(),
            "exercises": []
        }
            # 2. Wyciągamy szczegóły każdej pojedynczej serii
        for seria in self.sets:
            workout_data["exercises"].append({
                    "name": seria.exercise_name,
                    "weight": seria.weight,
                    "reps": seria.reps,
                    "volume": seria.calculate_volume()
                })
            
            # 2. Definiujemy nazwę naszego folderu na logi           
            folder_name ="logs"

            # 3. Jeśli folder 'logs' nie istnieje w naszym projekcie, Python go tworzy    
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)
            
            # 3. # 3. worzymy pełną ścieżkę do pliku (np. logs/training_2026-07-03.json)
            filename = f"training{self.date}.json"
            filepath = os.path.join(folder_name, filename)
        
            with open (filepath, 'w', encoding="UTF-8") as file:
                json.dump(workout_data, file, indent=4, ensure_ascii=False)
        
        print(f"Zapisano w pliku {filename}")

        pass

    def save_to_db(self):
        # 1. Otwieramy połączenie z naszym sejfem
        conn = sqlite3.connect('gym_tracker.db')
        cursor = conn.cursor()

        # --- BEZPIECZNIK: Tworzymy tabele, jeśli by ich brakowało ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                target_muscle TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_sets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workout_id INTEGER,
                exercise_name TEXT NOT NULL,
                weight REAL NOT NULL,
                reps INTEGER NOT NULL,
                FOREIGN KEY (workout_id) REFERENCES workouts (id)
            )
        ''')
        # -------------------------------------------------------------

        # 2. Wrzucamy główny trening do tabeli 'workouts'
        # Znak zapytania (?) to zabezpieczenie przed tzw. SQL Injection
        cursor.execute('''
            INSERT INTO workouts (date, target_muscle)
            VALUES  (?, ?)
        ''', (self.date, self.target_muscle))

        # 3. Pobieramy ID tego nowo dodanego treningu (Klucz Główny)
        workout_id = cursor.lastrowid

        # 4. Pętla wrzucająca poszczególne serie do tabeli 'training_sets'
        # Każda seria dostaje 'workout_id', żeby wiedziała, do jakiego treningu należy
        for s in self.sets:
            cursor.execute('''
                INSERT INTO training_sets (workout_id, exercise_name, weight, reps)
                VALUES (?, ?, ?, ?)  
            ''', (workout_id, s.exercise_name, s.weight, s.reps))

        # 5. Zatwierdzamy zmiany i zamykamy drzwi do bazy
        conn.commit()
        conn.close()

        print(f"Baza danych: Trening z {self.date} zapisany w tabelach SQLite!")

def setup_database():
    # Tworzymy połączenie z plikiem bazy (stworzy się sam, jeśli nie istnieje)
    conn = sqlite3.connect('gym_tracker.db')
    cursor = conn.cursor()

    # Tworzymy tabelę dla głównych treningów
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            target_muscle TEXT NOT NULL                      
        )
    ''')

# Tworzymy tabelę dla poszczególnych serii
# FOREIGN KEY to tzw. klucz obcy – łączy daną serię z konkretnym id treningu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trainig_sets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_id INTEGER,
            exercise_name TEXT NOT NULL,
            weight REAL NOT NULL,
            reps INTEGER NOT NULL,
            FOREIGN KEY (workout_id) REFERENCES workouts (id)                   
        )
    ''')

    # Zapisujemy zmiany i zamykamy połączenie
    conn.commit()
    conn.close()

# --- TESTOWANIE KOMPOZYCJI ---
# 1. Tworzymy nowy trening
#dzisiejszy_trening = Workout("2026-07-02", "Nogi & Push")

# 2. Dorzucamy serie (obiekty set_1, set_2, set_3 stworzyliśmy w poprzednim zadaniu)
#dzisiejszy_trening.add_set(set_1)
#dzisiejszy_trening.add_set(set_2)
#dzisiejszy_trening.add_set(set_3)

# Zapisujemy nasz trening do pliku!
#dzisiejszy_trening.save_to_json()

# 3. Odpalamy Twoją nową funkcję liczącą sumę
#print(f"PODSUMOWANIE:")
#print(f"Całkowity tonaż dzisiejszej sesji to: {dzisiejszy_trening.calculate_total_volume()} kg")

# Tworzymy nowy pomiar
#dzisiejsza_waga = BodyWeightLog("2026-07-03", 92.5, "Redukcja idzie zgodnie z planem")

# Wyświetlamy i zapisujemy
#dzisiejsza_waga.show_info()
#dzisiejsza_waga.save_to_json()

# --- ODCZYT DANYCH ---

def load_weight_log(date):
    # 1. Budujemy ścieżkę do pliku, którego szukamy
        filepath = os.path.join("logs", f"waga_{date}.json")
    # 2. Zabezpieczenie: sprawdzamy, czy taki plik w ogóle istnieje
        if os.path.exists(filepath):
            #Otwieramy plik w trybie odczytu (r)
            with open(filepath, 'r', encoding='utf-8') as file:
                # Magia: Python zamienia tekst z pliku z powrotem na słownik
                data = json.load(file)
                print(f"Super! W dniu {data['date']} Twoja waga wynosiła: {data['weight']} kg.")
                return data
        else:
            print(f"Błąd nie odnaleziono zapisu z dnia {date}.")
            return None

# Testujemy czytnik:
# Wpisz tutaj dzisiejszą datę, pod którą zapisał się Twój plik z wagą
# wczytane_dane = load_weight_log("2026-07-03")            

def load_workout(date):

    # 1. Łączymy się z bazą
    conn = sqlite3.connect('gym_tracker.db')
    cursor = conn.cursor()

    # 2. Szukamy głównego treningu po dacie (Używamy języka SQL)
    cursor.execute('''
        SELECT id, date, target_muscle FROM workouts WHERE date = ?
    ''', (date,))
    workout_row = cursor.fetchone() # Pobieramy jeden pasujący wiersz

    # Zabezpieczenie: jeśli nie ma takiego treningu
    if workout_row is None: 
        print(f"Nie znaleziono treningu z dnia {date}.")
        conn.close()
        return

    # Rozpakowujemy krotkę (tuple) z danymi
    workout_id, w_date, w_muscle = workout_row

    # 3. Odbudowujemy nasz obiekt Workout
    restored_workout = Workout(w_date, w_muscle)

    # 4. Szukamy wszystkich serii, które mają to konkretne workout_id
    cursor.execute("SELECT exercise_name, weight, reps FROM training_sets WHERE workout_id = ?", (workout_id,))
    sets_rows = cursor.fetchall() # Pobieramy wszystkie pasujące serie

    # 5. Doklejamy serie do obiektu (pamiętaj o zgodności nazw z klasą TrainingSet!)
    for row in sets_rows:
        # row[0] to nazwa, row[1] to ciężar, row[2] to powtórzenia
        temp_set = TrainingSet(row[0], row[1], row[2])
        restored_workout.add_set(temp_set)

    conn.close()

    print(f"Elegancko. Wczytano trening '{restored_workout.target_muscle}' z dnia {restored_workout.date}")    
    print(f"Całkowity tonaż tej sesji to {restored_workout.calculate_total_volume()} kg.")

    # 1. Szukamy odpowiedniego pliku w folderze logs
    filepath = os.path.join("logs", f"training{date}.json")

    if os.path.exists(filepath):
        with open (filepath, 'r', encoding="utf-8") as file:
            data = json.load(file)

            # 2. Odtwarzamy główny obiekt treningu
            restored_workout = Workout(data["date"], data["target_muscle"])

            # 3. Pętla, która przechodzi przez każdą zapisaną serię
            for ex in data["exercises"]:
                # Tworzymy obiekt serii na podstawie danych z pliku JSON
                restored_set = TrainingSet(ex["name"], ex["weight"], ex["reps"])

                # Dodajemy serię do zrekonstruowanego treningu
                restored_workout.add_set(restored_set)

            # 4. Wyświetlamy podsumowanie, żeby potwierdzić, że tonaż się zgadza
            print(f"Sukces. Wczytano trening '{restored_workout.target_muscle}' z dnia '{restored_workout.date}")
            print(f"Całkowity tonaż tej sesji to: '{restored_workout.calculate_total_volume()}' kg.")

            # Zwracamy gotowy, pełnoprawny obiekt (przyda się w przyszłości do wykresów)
            return restored_workout
    else:
        print(f"Błąd. Nie znaleziono pliku z dnia {date}.")
        return None    


def analyze_history():
    folder_name = "logs"
    if not os.path.exists(folder_name):
        print("Błąd. Folder logs nie istnieje")
        return
    
    total_volume = 0
    workout_count = 0

    print ("\n ---Analiza historii treningów--- ")

    #os.listdir() skanuje cały folder i zwraca listę plików
    for filename in os.listdir(folder_name):

        # Filtrujemy: interesują nas tylko pliki treningowe z rozszerzeniem .json
        if filename.startswith("training") and filename.endswith(".json"):
            filepath = os.path.join(folder_name, filename)

            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)

                # Szybka rekonstrukcja obiektu, żeby użyć metody calculate_total_volume()
                temp_workout = Workout(data["date"], data["target_muscle"])
                for ex in data["exercises"]:
                    temp_set = TrainingSet(ex["name"], ex["weight"], ex["reps"])
                    temp_workout.add_set(temp_set)

                # Zbieranie danych do statystyk
                session_volume = temp_workout.calculate_total_volume()
                total_volume += session_volume
                workout_count += 1

                print(f"{data['date']} {data['target_muscle']}: {session_volume} kg")    

    # Podsumowanie wyliczane tylko, jeśli znaleziono chociaż jeden trening
    if workout_count > 0:
        srednia = total_volume / workout_count
        print("-" *35)
        print('Podsumowanie')
        print(f"Liczba odbytych treningów: {workout_count}")
        print(f"Łączny przerzucony ciężar: {total_volume}")
        print(f"Średni tonaż na sesję: {srednia:.2f} kg")
    else:
        print("Nie znaleziono żadnych treningów :(")                

def export_to_csv():
    folder_name = "logs"
    csv_filename = os.path.join(folder_name, "workout_history.csv")

    if not os.path.exists(folder_name):
        print("Błąd. Folder logs nie istnieje")
        return
    
    # Nagłówki kolumn w naszym pliku CSV
    headers = ['Data', 'Partia miesniowa', 'Cwiczenie', 'Ciezar (kg)', 'Powtorzenia', 'Tonaz serii (kg)']

    licznik_serii = 0

    print("\n Rozpoczynam eksport danych")

    # Otwieramy plik CSV do zapisu
    with open(csv_filename, mode='w', newline='' ,encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file, delimiter=';') # Średnik pozwala na łatwiejsze otwarcie w polskim Excelu
        writer.writerow(headers) # Zapisujemy nagłówki na samej górze

        # Skanujemy folder identycznie jak przy analizie
        for filename in os.listdir(folder_name):
            if filename.startswith("training") and filename.endswith(".json"):
                filepath = os.path.join(folder_name, filename)

                with open(filepath, 'r', encoding='utf-8') as json_file:
                    data = json.load(json_file)

                data_treningu = data['date']
                partia = data['target_muscle']

               # Wyciągamy każdą pojedynczą serię jako osobny wiersz w tabeli

                for ex in data['exercises']:
                   cwiczenie = ex['name']
                   ciezar = ex['weight']
                   powtorzenia = ex['reps']
                   tonaz_serii = ciezar * powtorzenia

                   # Zapisujemy gotowy wiersz do pliku CSV
                   writer.writerow([data_treningu, partia, cwiczenie, ciezar, powtorzenia, tonaz_serii])
                   licznik_serii += 1

    print(f'Elegancko!. Wyeksportowano {licznik_serii} serii do pliku {csv_filename}')                   

def main_menu():
    while True:
        print("\n" + "="*35)
        print("DZIENNIK TRENINGOWY MENU")
        print("="*35)
        print("1. Zapisz pomiar wagi")
        print("2. Dodaj nowy trening")
        print("3. Przejrzyj historię wagi")
        print("4. Odczyt treningu z konkretnego dnia")
        print("5. Analiza historii treningów")
        print("6. Eksportuj do pliku CSV")
        print("7. Wyjście z programu")
        print("="*35)

        wybor = input("Wybierz opcję 1-7: ")

        if wybor == "1":
            print("\n ---Dodawanie wagi--- ")
            data = input("Podaj datę: np. (2026-07-06)")
            try:
                # Zamieniamy tekst z klawiatury na liczbę zmiennoprzecinkową (float)
                waga = float(input("Podaj wagę w kg: " ))
                notatki = input("Dodatkowe notatki: (opcjonalne)")

                nowy_pomiar = BodyWeightLog(data, waga, notatki)
                nowy_pomiar.save_to_json()
            except ValueError:
                print("Błąd. Waga musi być liczbą. (np. 85)")

        elif wybor == "2":
            print("\n ---Dodawanie nowego treningu--- ")
            data = input("Podaj datę treningu: np(2026-07-06)")
            partia = input("Podaj trenowaną partię: np(Klatka i plecy)")

            nowy_trening = Workout(data,partia)

            # Wewnętrzna pętla do dodawania kolejnych serii
            while True:
                cwiczenie = input("\n Podaj nazwę ćwiczenia (lub wpisz 'koniec' aby zapisać trening): ")
                # Jeśli wpiszesz 'koniec', przerywamy dodawanie serii
                if cwiczenie.lower() == 'koniec':
                    break

                try:
                    ciezar = float(input("Podaj ciężar roboczy w kg: "))
                    powtorzenia = int(input("Podaj liczbę powtórzeń: "))

                    nowa_seria = TrainingSet(cwiczenie, ciezar, powtorzenia)
                    nowy_trening.add_set(nowa_seria)
                except ValueError:
                    print("Błąd. Ciężar i powtórzenia muszą być liczbami!")

            # Gdy wyjdziemy z pętli wpisywania serii, zapisujemy cały trening
            nowy_trening.save_to_db()

        elif wybor == "3":
            print("\n Odczyt wagi ")
            data = input("Podaj datę pomiaru, którego szukasz (np. 2026-07-06): ")
            # Wywołujemy Twoją funkcję, która już istnieje wyżej w kodzie!
            load_weight_log(data)

        elif wybor == "4":
            print("\n Odczyt treningu")
            data = input("Podaj datę treningu, którego szukasz (np. 2026-07-02): ")
            # Wywołujemy funkcję, która już istnieje w kodzie!
            load_workout(data)

        elif wybor == "5":
            print("\n Analza historii treningów")
            # Wywołujemy funkcję, która już istnieje w kodzie!
            analyze_history()

        elif wybor == "6":
            print("\n Eksport do pliku CSV")
            # Wywołujemy funkcję, która już istnieje w kodzie!
            export_to_csv()

        elif wybor == "7":
            print("\n Zamykam, do zobaczenia na treningu. ")
            break # To słowo kluczowe ostatecznie przerywa główną pętlę

        else:
            print("/n Nieznana opcja. Wybierz 1, 2, 3, 4, 5, 6 lub 7. ")

# To jest standardowy sposób odpalania głównej funkcji w Pythonie
if __name__ == "__main__":
    setup_database()
    main_menu()




        



              