import datetime
from typing import Optional
from .person import Person

class Family:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.members = []
        self.current_year = datetime.datetime.now().year

    def add_member(self, person: Person) -> None:
        """Agrega una persona a la familia"""
        self.members.append(person)

    def get_member_by_cedula(self, cedula: str) -> Optional[Person]:
        """Obtiene una persona por su cédula"""
        for member in self.members:
            if member.cedula == cedula:
                return member
        return None

    def get_living_members(self) -> list:
        """Obtiene todas las personas vivas de la familia"""
        return [member for member in self.members if member.alive]

    def get_deceased_members(self) -> list:
        """Obtiene todas las personas fallecidas de la familia"""
        return [member for member in self.members if not member.alive]

    @staticmethod
    def validate_cedula_unique(cedula: str, family: 'Family') -> bool:
        """Valida que la cédula sea única en la familia"""
        for member in family.members:
            if member.cedula == cedula:
                return False
        return True

    @staticmethod
    def generate_cedula() -> str:
        """Genera una cédula única aleatoria"""
        import random
        return str(random.randint(100000000, 999999999))

    @staticmethod
    def generate_name(gender: str) -> tuple:
        """Genera un nombre aleatorio según el género"""
        male_names = ["Juan", "Carlos", "José", "Luis", "Miguel", "Pedro", "Ricardo", "Fernando", "Andrés", "Diego"]
        female_names = ["María", "Ana", "Laura", "Sofía", "Isabel", "Carmen", "Elena", "Patricia", "Claudia", "Verónica"]
        last_names = ["González", "Rodríguez", "Pérez", "López", "Martínez", "García", "Hernández", "Sánchez", "Ramírez", "Torres"]
        
        if gender == "M":
            first_name = random.choice(male_names)
        else:
            first_name = random.choice(female_names)
            
        last_name = random.choice(last_names)
        return first_name, last_name
