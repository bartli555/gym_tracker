import json

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

            # 2. Tworzymy nazwę pliku (inną niż dla treningu, żeby zachować porządek)
        filename = f"waga_{self.date}.json"

            # 3. Zapis na dysk
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(weight_data, file, indent=4, ensure_ascii=False)

        print(f"Zapisano wagę {self.weight} w pliku {filename}")
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
set_1 = TrainingSet("Bench Press", 80, 8)
set_2 = TrainingSet("Front Squat", 100, 6)
set_3 = TrainingSet("RDL", 120, 4)

# Odpalamy gotową metodę
set_1.show_info()
set_2.show_info()
set_3.show_info()

# Testujemy Twoją metodę calculate_volume()
print(f"Objętość RDL: {set_3.calculate_volume()} kg")

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
            
            # 3. Zapisujemy zgrabny plik na dysku z dzisiejszą datą w nazwie
            filename = f"training{self.date}.json"
        
            with open (filename, 'w', encoding="UTF-8") as file:
                json.dump(workout_data, file, indent=4, ensure_ascii=False)
        
        print(f"Zapisano w pliku {filename}")

        pass

# --- TESTOWANIE KOMPOZYCJI ---
# 1. Tworzymy nowy trening
dzisiejszy_trening = Workout("2026-07-02", "Nogi & Push")

# 2. Dorzucamy serie (obiekty set_1, set_2, set_3 stworzyliśmy w poprzednim zadaniu)
dzisiejszy_trening.add_set(set_1)
dzisiejszy_trening.add_set(set_2)
dzisiejszy_trening.add_set(set_3)

# Zapisujemy nasz trening do pliku!
dzisiejszy_trening.save_to_json()

# 3. Odpalamy Twoją nową funkcję liczącą sumę
print(f"PODSUMOWANIE:")
print(f"Całkowity tonaż dzisiejszej sesji to: {dzisiejszy_trening.calculate_total_volume()} kg")

# Tworzymy nowy pomiar
dzisiejsza_waga = BodyWeightLog("2026-07-03", 92.5, "Redukcja idzie zgodnie z planem")

# Wyświetlamy i zapisujemy
dzisiejsza_waga.show_info()
dzisiejsza_waga.save_to_json()