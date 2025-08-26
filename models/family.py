import datetime
import random
from typing import Optional
from .person import Person

class Family:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.members = []
        self.current_year = datetime.datetime.now().year

    # En models/family.py
    def undo(self):
        if self.history:
            self.restore_state(self.history.pop())

    def add_or_update_member(self, person: Person) -> None:
        """Agrega o actualiza una persona en la familia"""
        for i, p in enumerate(self.members):
            if p.cedula == person.cedula:
                self.members[i] = person
                return
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

    def add_relationship(self, parent_cedula: str, child_cedula: str) -> None:
        """Establece una relación de padre-hijo entre dos miembros de la familia."""
        parent = self.get_member_by_cedula(parent_cedula)
        child = self.get_member_by_cedula(child_cedula)
        
        if parent and child:
            child.father = parent if parent.gender == "Masculino" else child.father
            child.mother = parent if parent.gender == "Femenino" else child.mother
            parent.children.append(child)
        else:
            raise ValueError("Uno o ambos miembros no existen en la familia.")

    def verificar_integridad(self) -> bool:
        """Verifica la integridad del árbol familiar"""
        errores = []
        
        for person in self.members:
            # Verificar pareja
            if person.spouse:
                if person.spouse.spouse != person:
                    errores.append(f"{person.first_name} tiene pareja pero no es recíproca")
                
                # Verificar estado civil
                if "Casado" not in person.marital_status:
                    errores.append(f"{person.first_name} tiene pareja pero estado civil es '{person.marital_status}'")
            
            # Verificar padres
            if person.father and person not in person.father.children:
                errores.append(f"{person.first_name} tiene padre pero no está en sus hijos")
            if person.mother and person not in person.mother.children:
                errores.append(f"{person.first_name} tiene madre pero no está en sus hijos")
        
        if errores:
            for error in errores:
                print(f"ERROR DE INTEGRIDAD: {error}")
            return False
        
        return True