from typing import Tuple, Optional
from models.familia import Family
from models.persona import Person

class RelacionService:
    """Servicio para gestionar relaciones familiares"""
    
    @staticmethod
    def registrar_padres(family: Family, child_cedula: str, 
                        mother_cedula: str, father_cedula: str) -> Tuple[bool, str]:
        """Registra la relación de padres para un hijo"""
        child = family.get_member_by_cedula(child_cedula)
        mother = family.get_member_by_cedula(mother_cedula)
        father = family.get_member_by_cedula(father_cedula)
        
        if not child or not mother or not father:
            return False, "Una o más personas no existen en la familia"
        
        if mother.gender != "F":
            return False, "La persona seleccionada como madre debe ser mujer"
        
        if father.gender != "M":
            return False, "La persona seleccionada como padre debe ser hombre"
        
        # Establecer relaciones
        child.mother = mother
        child.father = father
        
        # Asegurar que el hijo no esté duplicado
        if child not in mother.children:
            mother.children.append(child)
        if child not in father.children:
            father.children.append(child)
        
        return True, "Relación de padres registrada exitosamente"
    
    @staticmethod
    def registrar_pareja(family: Family, person1_cedula: str, 
                        person2_cedula: str) -> Tuple[bool, str]:
        """Registra una unión de pareja entre dos personas"""
        person1 = family.get_member_by_cedula(person1_cedula)
        person2 = family.get_member_by_cedula(person2_cedula)
        
        if not person1 or not person2:
            return False, "Una o más personas no existen en la familia"
        
        if person1 == person2:
            return False, "No se puede registrar pareja consigo mismo"
        
        if person1.gender == person2.gender:
            return False, "No se puede registrar pareja del mismo género"
        
        # Verificar si ya están registrados como pareja
        if person1.spouse == person2:
            return False, "Estas personas ya están registradas como pareja"
        
        # Establecer relación
        person1.spouse = person2
        person2.spouse = person1
        
        # Actualizar estado civil
        person1.marital_status = "Casado/a"
        person2.marital_status = "Casado/a"
        
        return True, "Pareja registrada exitosamente"
    
    @staticmethod
    def encontrar_relacion(person1: Person, person2: Person) -> str:
        """Encuentra la relación entre dos personas"""
        if not person1 or not person2 or person1 == person2:
            return "No hay relación"
        
        # Padres
        if person1 == person2.father or person1 == person2.mother:
            return "Padre/Madre"
        
        # Hijos
        if person2 in person1.children:
            return "Hijo/Hija"
        
        # Hermanos
        if (person1.mother and person2.mother and 
            person1.mother == person2.mother and person1.father == person2.father):
            return "Hermano/Hermana"
        
        # Abuelos
        if (person1 == person2.father.father if person2.father else False or 
            person1 == person2.father.mother if person2.father else False or
            person1 == person2.mother.father if person2.mother else False or
            person1 == person2.mother.mother if person2.mother else False):
            return "Abuelo/Abuela"
        
        # Nietos
        for child in person1.children:
            if person2 in child.children:
                return "Nieto/Nieta"
        
        # Tíos
        if (person1.mother and person2.mother and 
            person1.mother == person2.mother.father):
            return "Tío/Tía paterno"
        if (person1.mother and person2.mother and 
            person1.mother == person2.mother.mother):
            return "Tío/Tía materno"
        
        # Sobrinos
        for sibling in person1.children:
            if person2 in sibling.children:
                return "Sobrino/Sobrina"
        
        # Primos
        if (person1.mother and person2.mother and 
            person1.mother.mother == person2.mother.mother):
            return "Primo/Prima"
        
        return "Relación no identificada"
    
    @staticmethod
    def obtener_primos_primer_grado(person: Person) -> list:
        """Obtiene los primos de primer grado de una persona"""
        cousins = []
        
        # Obtener hermanos de los padres
        if person.father and person.father.mother:
            for sibling in person.father.mother.children:
                if sibling != person.father and sibling.alive:
                    cousins.extend([child for child in sibling.children if child.alive])
        
        if person.mother and person.mother.mother:
            for sibling in person.mother.mother.children:
                if sibling != person.mother and sibling.alive:
                    cousins.extend([child for child in sibling.children if child.alive])
        
        return cousins
    
    @staticmethod
    def obtener_antepasados_maternos(person: Person) -> list:
        """Obtiene todos los antepasados maternos de una persona"""
        ancestors = []
        current = person
        
        while current.mother:
            ancestors.append(current.mother)
            current = current.mother
        
        return ancestors
    
    @staticmethod
    def obtener_descendientes_vivos(person: Person) -> list:
        """Obtiene todos los descendientes vivos de una persona"""
        descendants = []
        
        def encontrar_descendientes(current):
            for child in current.children:
                if child.alive:
                    descendants.append(child)
                encontrar_descendientes(child)
        
        encontrar_descendientes(person)
        return descendants

# Funciones de utilidad para consultas
def obtener_nacimientos_ultimos_10_años(family: Family) -> int:
    """Obtiene cuántas personas nacieron en los últimos 10 años"""
    count = 0
    for person in family.members:
        if person.birth_date:
            birth_year = int(person.birth_date[:4])
            if family.current_year - birth_year <= 10:
                count += 1
    return count

def obtener_parejas_con_hijos(family: Family, min_hijos: int = 2) -> list:
    """Obtiene las parejas actuales con mínimo de hijos en común"""
    couples = []
    for person in family.members:
        if person.spouse and person.alive and person.spouse.alive:
            common_children = set(person.children) & set(person.spouse.children)
            if len(common_children) >= min_hijos:
                couples.append((person, person.spouse))
    return couples

def obtener_fallecidos_antes_50(family: Family) -> int:
    """Obtiene cuántas personas fallecieron antes de cumplir 50 años"""
    count = 0
    for person in family.members:
        if person.death_date and person.birth_date:
            try:
                birth_year = int(person.birth_date[:4])
                death_year = int(person.death_date[:4])
                if death_year - birth_year < 50:
                    count += 1
            except (ValueError, TypeError):
                continue
    return count
