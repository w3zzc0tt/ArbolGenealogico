from typing import Tuple, Optional
from models.family import Family
from models.person import Person

class RelacionService:
    """Servicio para gestionar relaciones familiares"""
    
    @staticmethod
    def registrar_padres(family: Family, child_cedula: str, 
                        mother_cedula: Optional[str] = None, 
                        father_cedula: Optional[str] = None) -> Tuple[bool, str]:
        """
        Registra la relación de padres para un hijo.
        Actualiza automáticamente la lista de hermanos.
        """
        child = family.get_member_by_cedula(child_cedula)
        if not child:
            return False, "El hijo no existe en la familia"
        
        # Validar que al menos un padre/madre esté presente
        if not mother_cedula and not father_cedula:
            return False, "Debe proporcionar al menos una madre o un padre"
        
        # Obtener objetos de personas
        mother = family.get_member_by_cedula(mother_cedula) if mother_cedula else None
        father = family.get_member_by_cedula(father_cedula) if father_cedula else None
        
        # Validar que los padres existan si se proporcionaron
        if mother_cedula and not mother:
            return False, "La madre seleccionada no existe en la familia"
        if father_cedula and not father:
            return False, "El padre seleccionado no existe en la familia"
        
        # Validar género para los padres proporcionados
        if mother and mother.gender != "Femenino":
            return False, "La persona seleccionada como madre debe ser mujer"
        
        if father and father.gender != "Masculino":
            return False, "La persona seleccionada como padre debe ser hombre"
        
        # Establecer relaciones
        if mother:
            child.mother = mother
            if child not in mother.children:
                mother.children.append(child)
        
        if father:
            child.father = father
            if child not in father.children:
                father.children.append(child)
        
        # ✅ ACTUALIZAR HERMANOS AUTOMÁTICAMENTE
        RelacionService._actualizar_hermanos(child, family)
        
        return True, "Relación de padres registrada exitosamente"

    @staticmethod
    def _actualizar_hermanos(person: Person, family: Family):
        """Actualiza la lista de hermanos para todos los hijos de los padres"""
        if person.father or person.mother:
            # Obtener todos los hijos de los padres
            padres = [p for p in [person.father, person.mother] if p]
            for padre in padres:
                for hermano in padre.children:
                    if hermano != person and hermano not in person.siblings:
                        person.siblings.append(hermano)
                        hermano.siblings.append(person)
    
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

def buscar_personas_por_nombre(family: Family, nombre: str) -> list:
    """Busca personas por nombre o apellido (búsqueda parcial, insensible a mayúsculas)"""
    nombre = nombre.lower()
    resultados = []
    for person in family.members:
        if (nombre in person.first_name.lower() or 
            nombre in person.last_name.lower()):
            resultados.append(person)
    return resultados

def obtener_personas_sin_relacion(family: Family) -> list:
    """Obtiene personas sin relaciones familiares (sin padres, hijos, pareja o hermanos)"""
    sin_relacion = []
    for person in family.members:
        if (not person.mother and not person.father and 
            not person.children and not person.spouse and 
            not person.siblings):
            sin_relacion.append(person)
    return sin_relacion

def obtener_estadisticas_familia(family: Family) -> dict:
    """Obtiene estadísticas generales de la familia"""
    total = len(family.members)
    vivos = len(family.get_living_members())
    fallecidos = len(family.get_deceased_members())
    promedio_edad = (sum(p.calculate_age() for p in family.get_living_members()) / vivos) if vivos > 0 else 0
    return {
        'total': total,
        'vivos': vivos,
        'fallecidos': fallecidos,
        'promedio_edad': round(promedio_edad, 2)
    }
def obtener_personas_por_estado_civil(family: Family, estado_civil: str) -> list:
    """Obtiene personas por estado civil"""
    return [p for p in family.members if p.marital_status.lower() == estado_civil.lower()]

def obtener_personas_por_provincia(family: Family, provincia: str) -> list:
    """Obtiene personas por provincia"""
    return [p for p in family.members if p.province.lower() == provincia.lower()] 

def buscar_por_caracteristica(family: Family, caracteristica: str, valor) -> list:
    """Busca personas por una característica específica"""
    resultados = []
    for person in family.members:
        if hasattr(person, caracteristica):
            if str(getattr(person, caracteristica)).lower() == str(valor).lower():
                resultados.append(person)
    return resultados