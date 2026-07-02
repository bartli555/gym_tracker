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