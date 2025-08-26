from asyncio.log import logger
import logging
import random
import datetime
from typing import Tuple, Optional
from models.family import Family
from models.person import Person
from models.simulation_config import SimulationConfig
from services.relacion_service import RelacionService
from services.persona_service import PersonaService

class SimulacionService:
    """Servicio para gestionar la simulación de eventos familiares"""
    
    @staticmethod
    def simular_cumpleaños(person: Person, family: Family) -> None:
        """Simula un cumpleaños para una persona"""
        sim_date = f"{family.current_year}-01-01"
        person.add_event("Cumpleaños", sim_date)
        
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
        
        # Mes aleatorio
        month = random.randint(1, 12)
        day = random.randint(1, 28)  # Evitar problemas con febrero
        birth_date = f"{family.current_year}-{month:02d}-{day:02d}"
        
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
    def ejecutar_ciclo_simulacion(family: Family, config: SimulationConfig = None) -> list:
        """Ejecuta un ciclo completo de simulación para una familia"""
        if config is None:
            config = SimulationConfig()
            
        eventos = []
        
        # Incrementar el año en la simulación
        family.current_year += config.events_interval
        sim_date = f"{family.current_year}-01-01"
        eventos.append(f"Año de simulación: {family.current_year}")
        
        # Crear una copia de la lista de miembros para evitar problemas de modificación durante iteración
        members_copy = family.members.copy()
        
        # Procesar eventos para cada persona
        for person in members_copy:
            if not person.alive:
                continue
                
            # Cumpleaños
            person.add_event("Cumpleaños", sim_date)
            
            # Probabilidad de fallecimiento
            age = person.calculate_age()
            death_probability = config.death_probability_base
            if age > 60:
                death_probability += 0.01 * (age - 60)
                
            if random.random() < death_probability:
                success, message = SimulacionService.simular_fallecimiento(person, family)
                if success:
                    eventos.append(message)
            
            # Probabilidad de encontrar pareja
            if (person.marital_status == "Soltero/a" and person.calculate_age() >= 18 and 
                random.random() < config.find_partner_probability and not person.has_partner()):
                pareja_encontrada = SimulacionService.intentar_encontrar_pareja(person, family)
                if pareja_encontrada:
                    eventos.append(f"{person.first_name} {person.last_name} encontró pareja")
        
        # Probabilidad de nacimientos (separado del ciclo principal para evitar problemas con nuevos miembros)
        for person in members_copy:
            # Verificar que la persona esté viva, pueda tener hijos y tenga pareja viva
            if (person.alive and 
                person.can_have_children() and 
                person.has_partner() and 
                person.spouse and  # Asegurar que spouse no sea None
                person.spouse.alive and 
                random.random() < config.birth_probability):
                
                success, message = SimulacionService.simular_nacimiento(
                    person, person.spouse, family
                )
                if success:
                    eventos.append(message)
        
        # Asegurar consistencia en las relaciones de pareja
        for person in members_copy:
            if person.spouse and person.spouse.spouse != person:
                # Corregir relación recíproca
                person.spouse.spouse = person
                if "Casado" not in person.spouse.marital_status:
                    person.spouse.marital_status = "Casado/a"
        
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
    
    @staticmethod
    def calcular_compatibilidad(person1: Person, person2: Person) -> float:
        """Calcula un índice de compatibilidad entre dos personas (0-100%)"""
        # 1. Compatibilidad de edad (máximo 40 puntos)
        age_diff = abs(person1.calculate_age() - person2.calculate_age())
        age_score = max(0, 40 - (age_diff * 2.5))  # -2.5 puntos por año de diferencia
        
        # 2. Compatibilidad de intereses (máximo 40 puntos)
        common_interests = len(set(person1.interests) & set(person2.interests))
        total_interests = len(set(person1.interests) | set(person2.interests))
        interest_score = (common_interests / total_interests * 40) if total_interests > 0 else 0
        
        # 3. Compatibilidad emocional (máximo 20 puntos)
        emotional_score = 20 - abs(person1.emotional_health - person2.emotional_health) / 5
        
        # Total (0-100%)
        total_score = min(100, age_score + interest_score + emotional_score)
        return total_score

    @staticmethod
    def es_pareja_compatible(person1: Person, person2: Person) -> bool:
        """Determina si dos personas son compatibles para formar pareja"""
        return SimulacionService.calcular_compatibilidad(person1, person2) >= 60

    @staticmethod
    def intentar_encontrar_pareja(person: Person, family: Family) -> bool:
        """Intenta encontrar una pareja para una persona soltera"""
        if not person.alive or person.has_partner():
            return False
            
        # Buscar posibles parejas
        possible_partners = []
        for potential in family.members:
            if (potential != person and potential.alive and 
                not potential.has_partner() and
                potential.gender != person.gender):
                
                # Verificar compatibilidad completa
                age_diff = abs(person.calculate_age() - potential.calculate_age())
                compatibility = SimulacionService.calcular_compatibilidad(person, potential)
                
                # Relajar requisitos para personas mayores
                if age_diff <= 20 and compatibility >= 50:
                    possible_partners.append(potential)
        
        # Seleccionar una pareja al azar
        if possible_partners:
            partner = random.choice(possible_partners)
            success, _ = RelacionService.registrar_pareja(family, person.cedula, partner.cedula)
            if success:
                logger.info(f"{person.first_name} y {partner.first_name} formaron pareja (compatibilidad: {SimulacionService.calcular_compatibilidad(person, partner):.1f}%)")
            return success
            
        return False
        

    @staticmethod
    def es_compatible_geneticamente(person1: Person, person2: Person) -> bool:
        """Verifica compatibilidad genética para evitar riesgos en descendencia"""
        # Caso 1: Parientes directos
        if person1 in [person2.father, person2.mother, person2.spouse] or \
        person2 in [person1.father, person1.mother, person1.spouse]:
            return False
        
        # Caso 2: Hermanos
        if person1 in person2.siblings or person2 in person1.siblings:
            return False
        
        # Caso 3: Primos hermanos (comparten abuelos)
        grandparents1 = set()
        for parent in [person1.father, person1.mother]:
            if parent:
                for grandparent in [parent.father, parent.mother]:
                    if grandparent:
                        grandparents1.add(grandparent.cedula)
        
        grandparents2 = set()
        for parent in [person2.father, person2.mother]:
            if parent:
                for grandparent in [parent.father, parent.mother]:
                    if grandparent:
                        grandparents2.add(grandparent.cedula)
        
        # Si comparten más de un abuelo, hay riesgo genético
        if len(grandparents1 & grandparents2) > 1:
            return False
        
        # Caso 4: Edad extrema
        age_diff = abs(person1.calculate_age() - person2.calculate_age())
        if age_diff > 40:
            return False
        
        return True

    @staticmethod
    def simular_nacimiento(mother: Person, father: Person, family: Family) -> Tuple[bool, str]:
        """Simula el nacimiento de un hijo"""
        if not mother.alive or not father.alive:
            return False, "Uno o ambos padres no están vivos"
        
        if not mother.can_have_children():
            return False, "La madre no puede tener hijos en este momento"
        
        # Verificar compatibilidad genética
        if not SimulacionService.es_compatible_geneticamente(mother, father):
            return False, "Riesgo genético: no se recomienda la procreación"
        
        # Generar datos del bebé
        gender = "F" if random.random() < 0.5 else "M"
        first_name, _ = Family.generate_name(gender)
        last_name = father.last_name  # Hereda el apellido del padre
        cedula = Family.generate_cedula()
        
        # Mes aleatorio
        month = random.randint(1, 12)
        day = random.randint(1, 28)  # Evitar problemas con febrero
        birth_date = f"{family.current_year}-{month:02d}-{day:02d}"
        
        # Crear el bebé
        success, baby, error = PersonaService.crear_persona(
            family, cedula, first_name, last_name, birth_date,
            "", gender, father.province, "Soltero/a"
        )
        
        if not success:
            return False, error
        
        # Registrar como hijos de ambos padres
        success, message = RelacionService.registrar_padres(
            family, baby.cedula, mother.cedula, father.cedula
        )
        
        if success:
            baby.add_event("Nacimiento", birth_date)
            return True, f"¡Felicitaciones! {mother.first_name} {mother.last_name} y {father.first_name} {father.last_name} tuvieron un bebé: {baby.first_name} {baby.last_name}"
        else:
            return False, "Error al registrar el nacimiento"