import datetime

class Person:
    def __init__(self, cedula, first_name, last_name, birth_date, gender, province, death_date=None):
        self.cedula = cedula
        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.death_date = death_date
        self.gender = gender
        self.province = province
        self.marital_status = "Soltero"
        self.spouse = None
        self.mother = None
        self.father = None
        self.children = []
        self.siblings = []
        self.alive = death_date is None
        self.history = [f"Nació en {birth_date}"]
        if not self.alive:
            self.history.append(f"Falleció en {death_date}")

    def add_event(self, event_type, date=None):
        if not date:
            date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.history.append(f"{event_type} ({date})")
        self.history.sort(key=lambda x: x.split('(')[1].rstrip(')') if '(' in x else "")

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.cedula})"


class Family:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.members = []
