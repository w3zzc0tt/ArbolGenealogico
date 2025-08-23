import random
import datetime
from typing import Tuple, Optional
from models.family import Family
from models.person import Person

class SimulacionService:
    """Servicio para gestionar la simulación de eventos familiares"""
    
    @staticmethod
    def simular_cumpleaños(person: Person, family: Family) -> None:
        """Simula un cumpleaños para una persona"""
        person.add_event("Cumpleaños", datetime.datetime.now().strftime("%Y-%m-%d"))
        
        # Si la persona está viuda, la salud emocional puede disminuir
        if person.marital_status == "Viudo/a" and person.emotional_health > 20:
            person.emotional_health -= random.randint(1, 5)
        
        # Si está soltero/a por mucho tiempo, la salud emocional disminuye
        if person.marital_status == "Soltero/a" and person.calculate_age() > 30:
            years_single = family.current_year - int(person.birth_date[:4]) - 30
            if years_single > 0:
                person.emotional_health = max(10, person.emotional_health - (years_single * 2))
        
        # Afectar esperanza de vida si la salud emocional es baja
        if person.emotional_health < 30:
            if random.random() < 0.1:  # 10% de probabilidad
                SimulacionService.simular_fallecimiento(person, family)

    @staticmethod
    def simular_fallecimiento(person: Person, family: Family) -> Tuple[bool, str]:
        """Simula el fallecimiento de una persona"""
        if not person.alive:
            return False, "La persona ya ha fallecido"
        
        # Actualizar estado
        person.alive = False
        person.death_date = datetime.datetime.now().strftime("%Y-%m-%d")
        person.marital_status = "Viudo/a" if person.spouse else "Fallecido/a"
        person.add_event("Fallecimiento", person.death_date)
        
        # Si tiene pareja, actualizar estado de la pareja
        if person.spouse and person.spouse.alive:
            person.spouse.marital_status = "Viudo/a"
            person.spouse.emotional_health = max(10, person.spouse.emotional_health - 30)
            person.spouse.add_event("Viudez", person.death_date)
        
        # Manejar hijos menores de edad
        SimulacionService.manejar_hijos_menores(person, family)
        
        return True, f"{person.first_name} {person.last_name} ha fallecido."

    @staticmethod
    def manejar_hijos_menores(parent: Person, family: Family) -> None:
        """Maneja los hijos menores cuando un padre fallece"""
        for child in parent.children:
            if child.alive and child.calculate_age() < 18:
                # Si el otro padre también falleció, buscar tutor
                if (parent.gender == "M" and child.mother and not child.mother.alive) or \
                   (parent.gender == "F" and child.father and not child.father.alive):
                    SimulacionService.encontrar_tutor_legal(child, family)

    @staticmethod
    def encontrar_tutor_legal(child: Person, family: Family) -> None:
        """Busca un tutor legal para un niño"""
        # Buscar abuelos
        grandparents = []
        if child.mother and child.mother.mother:
            grandparents.append(child.mother.mother)
        if child.mother and child.mother.father:
            grandparents.append(child.mother.father)
        if child.father and child.father.mother:
            grandparents.append(child.father.mother)
        if child.father and child.father.father:
            grandparents.append(child.father.father)
        
        # Filtrar abuelos vivos
        living_grandparents = [p for p in grandparents if p and p.alive]
        
        if living_grandparents:
            guardian = random.choice(living_grandparents)
            child.add_event(f"Tutor: {guardian.first_name} {guardian.last_name}", datetime.datetime.now().strftime("%Y-%m-%d"))
            return
        
        # Buscar tías/tíos
        aunts_uncles = []
        if child.mother and child.mother.mother:
            for sibling in child.mother.mother.children:
                if sibling != child.mother and sibling.alive:
                    aunts_uncles.append(sibling)
        if child.father and child.father.mother:
            for sibling in child.father.mother.children:
                if sibling != child.father and sibling.alive:
                    aunts_uncles.append(sibling)
        
        if aunts_uncles:
            guardian = random.choice(aunts_uncles)
            child.add_event(f"Tutor: {guardian.first_name} {guardian.last_name}", datetime.datetime.now().strftime("%Y-%m-%d"))
            return
        
        # Si no hay familiares cercanos, asignar tutor aleatorio
        living_members = [p for p in family.members if p.alive and p != child]
        if living_members:
            guardian = random.choice(living_members)
            child.add_event(f"Tutor: {guardian.first_name} {guardian.last_name}", datetime.datetime.now().strftime("%Y-%m-%d"))

    @staticmethod
    def simular_nacimiento(mother: Person, father: Person, family: Family) -> Tuple[bool, str]:
        """Simula el nacimiento de un hijo"""
        if not mother.alive or not father.alive:
            return False, "Uno o ambos padres no están vivos"
        
        if not mother.can_have_children():
            return False, "La madre no puede tener hijos en este momento"
        
        # Generar datos del bebé
        gender = "F" if random.random() < 0.5 else "M"
        first_name, _ = Family.generate_name(gender)
        last_name = father.last_name  # Hereda el apellido del padre
        cedula = Family.generate_cedula()
        
        birth_date = f"{family.current_year}-01-01"
        
        # Crear el bebé
        from services.persona_service import PersonaService
        success, baby, error = PersonaService.crear_persona(
            family, cedula, first_name, last_name, birth_date, 
            "", gender, father.province, "Soltero/a"
        )
        
        if not success:
            return False, error
        
        # Registrar como hijos de ambos padres
        from services.relacion_service import RelacionService
        success, message = RelacionService.registrar_padres(
            family, baby.cedula, mother.cedula, father.cedula
        )
        
        if success:
            baby.add_event("Nacimiento", birth_date)
            return True, f"¡Felicitaciones! {mother.first_name} {mother.last_name} y {father.first_name} {father.last_name} tuvieron un bebé: {baby.first_name} {baby.last_name}"
        else:
            return False, "Error al registrar el nacimiento"

    @staticmethod
    def ejecutar_ciclo_simulacion(family: Family) -> list:
        """Ejecuta un ciclo completo de simulación para una familia"""
        eventos = []
        
        # Incrementar el año en la simulación
        family.current_year += 1
        eventos.append(f"Año de simulación: {family.current_year}")
        
        # Procesar eventos para cada persona
        for person in family.members:
            if person.alive:
                # Cumpleaños
                SimulacionService.simular_cumpleaños(person, family)
                
                # Probabilidad de fallecimiento aleatorio
                age = person.calculate_age()
                death_probability = 0.01 * (age - 60) if age > 60 else 0.001
                if random.random() < death_probability:
                    success, message = SimulacionService.simular_fallecimiento(person, family)
                    if success:
                        eventos.append(message)
            
            # Probabilidad de encontrar pareja
            if (person.marital_status == "Soltero/a" and person.calculate_age() >= 18 and 
                random.random() < 0.05):  # 5% de probabilidad
                pareja_encontrada = SimulacionService.intentar_encontrar_pareja(person, family)
                if pareja_encontrada:
                    eventos.append(f"{person.first_name} {person.last_name} encontró pareja")
        
        # Probabilidad de nacimientos
        for person in family.members:
            if (person.can_have_children() and person.has_partner() and 
                random.random() < 0.3):  # 30% de probabilidad
                success, message = SimulacionService.simular_nacimiento(person, person.spouse, family)
                if success:
                    eventos.append(message)
        
        return eventos

    @staticmethod
    def intentar_encontrar_pareja(person: Person, family: Family) -> bool:
        """Intenta encontrar una pareja para una persona soltera"""
        if not person.alive or person.has_partner():
            return False
            
        # Buscar posibles parejas
        possible_partners = []
        for potential in family.members:
            if (potential != person and potential.alive and not potential.has_partner() and
                potential.gender != person.gender):
                # Verificar compatibilidad básica
                if (abs(person.calculate_age() - potential.calculate_age()) <= 15 and
                    len(set(person.interests) & set(potential.interests)) >= 2):
                    possible_partners.append(potential)
        
        # Seleccionar una pareja al azar
        if possible_partners:
            partner = random.choice(possible_partners)
            from services.relacion_service import RelacionService
            success, _ = RelacionService.registrar_pareja(family, person.cedula, partner.cedula)
            return success
            
        return False
