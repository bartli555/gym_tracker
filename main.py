import json
import os

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

def main_menu():
    while True:
        print("\n" + "="*35)
        print("DZIENNIK TRENINGOWY MENU")
        print("="*35)
        print("1. Zapisz pomiar wagi")
        print("2. Dodaj nowy trening")
        print("3. Wyjście z programu")
        print("="*35)

        wybor = input("Wybierz opcję 1-3:")

        if wybor == "1":
            print("\n ---Dodawanie wagi--- ")
            data = input("Podaj datę: np. (2026-07-06)")
            try:
                # Zamieniamy tekst z klawiatury na liczbę zmiennoprzecinkową (float)
                waga = float(input("Podaj wagę w kg" ))
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
            nowy_trening.save_to_json()

        elif wybor == "3":
            print("\n Zamykam, do zobaczenia na treningu. ")
            break # To słowo kluczowe ostatecznie przerywa główną pętlę

        else:
            print("/n Nieznana opcja. Wybierz 1, 2 lub 3. ")

# To jest standardowy sposób odpalania głównej funkcji w Pythonie
if __name__ == "__main__":
    main_menu()




        



              