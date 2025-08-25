import datetime
import random

class Person:
    def __init__(self, cedula, first_name, last_name, birth_date, gender, province, death_date=None, marital_status="Soltero/a"):
        self.cedula = cedula
        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.death_date = death_date
        self.gender = gender
        self.province = province
        self.marital_status = marital_status
        self.spouse = None
        self.mother = None
        self.father = None
        self.children = []
        self.siblings = []
        self.alive = death_date is None
        self.history = [f"Nació el {birth_date}"]
        if not self.alive:
            self.history.append(f"Falleció el {death_date}")

    def set_death_date(self, death_date: str):
        """Establece la fecha de defunción y actualiza estado"""
        self.death_date = death_date
        self.alive = False
        self.add_event("Fallecimiento", death_date)

    def set_alive(self):
        """Establece que la persona está viva"""
        self.death_date = None
        self.alive = True
        self.add_event("Regreso a la vida")

        # Atributos para simulación
        self.emotional_health = 100
        self.interests = self.generate_interests()

    def generate_interests(self):
        all_interests = ["Deportes", "Lectura", "Música", "Arte", "Tecnología", "Cocina", "Viajes", "Naturaleza"]
        return random.sample(all_interests, 3)

    def add_event(self, event_type, date=None):
        if not date:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.history.append(f"{event_type} ({date})")
        self.history.sort(key=lambda x: x.split('(')[1].rstrip(')') if '(' in x else "")

    def calculate_age(self):
        try:
            birth = datetime.datetime.strptime(self.birth_date, "%Y-%m-%d")
            today = datetime.datetime.now()
            age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
            return age
        except:
            return 0

    def get_full_name(self) -> str:
        """Obtiene el nombre completo de la persona"""
        return f"{self.first_name} {self.last_name}"

    def can_have_children(self) -> bool:
        """Determina si la persona puede tener hijos"""
        if not self.alive:
            return False
        if self.gender == "F":
            age = self.calculate_age()
            return 18 <= age <= 45
        else:
            age = self.calculate_age()
            return 18 <= age <= 65

    def has_partner(self) -> bool:
        """Verifica si la persona tiene pareja"""
        return self.spouse is not None and self.spouse.alive

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.cedula})"
    
    def add_history(self, event: str):
        """Agrega un evento manual al historial"""
        from datetime import datetime
        date = datetime.now().strftime("%Y-%m-%d")
        self.history.append(f"{event} ({date})")