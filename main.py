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
        print(f"Dodano nową serię: {training_set.exercise_name}" do treningu z dnia: {training_set.date}.)

    def calculate_total_volume(self):
        total_volume = 0
        for seria in self.sets:
            
        return total_volume

        pass

# --- TESTOWANIE KOMPOZYCJI ---
# 1. Tworzymy nowy trening
dzisiejszy_trening = Workout("2026-07-02", "Nogi & Push")

# 2. Dorzucamy serie (obiekty set_1, set_2, set_3 stworzyliśmy w poprzednim zadaniu)
dzisiejszy_trening.add.set(set_1)
dzisiejszy_trening.add.set(set_2)
dzisiejszy_trening.add.set(set_3)

# 3. Odpalamy Twoją nową funkcję liczącą sumę
print(f"PODSUMOWANIE:")
print(f"Całkowity tonaż dzisiejszej sesji to: {dzisiejszy_trening.calculate_total_volume()} kg")