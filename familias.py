from personas import Person

class Family:
    """Clase que representa una familia en el sistema"""
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.members = []  # Lista de personas

def add_person_to_family(family, cedula, name, birth_date, death_date, gender, province, marital_status):
    """Agrega una nueva persona a la familia"""
    person = Person(cedula, name, birth_date, death_date, gender, province, marital_status)
    family.members.append(person)

def get_person_by_cedula(family, cedula):
    """Obtiene una persona por su cédula"""
    for member in family.members:
        if member.cedula == cedula:
            return member
    return None

def validate_family_has_members(family, min_members=1):
    """Verifica que la familia tenga suficientes miembros"""
    return len(family.members) >= min_members