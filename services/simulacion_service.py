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
    
    def calcular_compatibilidad_total(person1: Person, person2: Person) -> dict:
        """Sistema completo de compatibilidad"""
        scores = {}
        
        # 1. Edad (30 puntos) - Diferencia máxima 15 años
        age_diff = abs(person1.calculate_virtual_age() - person2.calculate_virtual_age())
        if age_diff <= 3:
            scores['age'] = 30
        elif age_diff <= 8:
            scores['age'] = 20
        elif age_diff <= 15:
            scores['age'] = 10
        else:
            scores['age'] = 0
        
        # 2. Intereses (25 puntos) - Mínimo 2 en común
        common_interests = len(set(person1.interests) & set(person2.interests))
        scores['interests'] = min(25, common_interests * 8)  # 8 puntos por interés común
        
        # 3. Salud emocional (25 puntos) - Similar nivel
        emotional_diff = abs(person1.emotional_health - person2.emotional_health)
        scores['emotional'] = max(0, 25 - emotional_diff // 4)
        
        # 4. Genética (20 puntos) - No familiares directos
        if es_compatible_geneticamente(person1, person2):
            scores['genetic'] = 20
        else:
            scores['genetic'] = 0
        
        total = sum(scores.values())
        
        return {
            'total': total,
            'compatible': total >= 70,
            'breakdown': scores,
            'recommendation': get_compatibility_message(total)
        }

    def get_compatibility_message(score):
        if score >= 85:
            return "💕 Pareja perfecta"
        elif score >= 70:
            return "💖 Muy compatible"
        elif score >= 50:
            return "💛 Compatible con esfuerzo"
        else:
            return "💔 Incompatible"

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
        """Versión mejorada de simulación de nacimiento"""
        # Verificaciones base
        if not mother.alive or not father.alive:
            return False, "Uno o ambos padres han fallecido"
        
        mother_age = getattr(mother, 'virtual_age', mother.calculate_age())
        father_age = getattr(father, 'virtual_age', father.calculate_age())
        
        # Verificar edad reproductiva
        if not (18 <= mother_age <= 45):
            return False, f"Madre fuera de edad reproductiva ({mother_age} años)"
        
        if not (18 <= father_age <= 65):
            return False, f"Padre fuera de edad reproductiva ({father_age} años)"
        
        # Verificar compatibilidad
        compatibility = SimulacionService.calcular_compatibilidad_total(mother, father)
        if not compatibility['compatible']:
            return False, f"Compatibilidad insuficiente ({compatibility['total']:.1f}%)"
        
        # Generar bebé con datos realistas
        gender = "F" if random.random() < 0.48 else "M"  # Ligeramente más niñas
        first_name, _ = Family.generate_name(gender)
        
        # Apellido: Combinación realista (padre + madre o solo padre)
        if random.random() < 0.7:  # 70% usa apellido del padre
            last_name = father.last_name
        else:  # 30% combina apellidos
            last_name = f"{father.last_name}-{mother.last_name}"
        
        # Generar cédula única
        cedula = Family.generate_cedula()
        while not Family.validate_cedula_unique(cedula, family):
            cedula = Family.generate_cedula()
        
        # Provincia: Hereda de los padres
        province = father.province if random.random() < 0.6 else mother.province
        
        # Crear bebé
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        baby = Person(
            cedula=cedula,
            first_name=first_name,
            last_name=last_name,
            birth_date=current_date,
            gender=gender,
            province=province,
            marital_status="Soltero/a"
        )
        
        # Heredar algunos intereses de los padres
        parent_interests = list(set(mother.interests + father.interests))
        baby.interests = random.sample(parent_interests, min(2, len(parent_interests)))
        baby.interests.extend(random.sample(["Juegos", "Dibujo", "Música"], 1))
        
        # Agregar a la familia
        family.add_or_update_member(baby)
        
        # Registrar relaciones familiares
        from services.relacion_service import RelacionService
        success, message = RelacionService.registrar_padres(
            family, baby.cedula, mother.cedula, father.cedula
        )
        
        if success:
            # Registrar evento en todos los involucrados
            birth_event = f"Nacimiento de {baby.first_name}"
            mother.add_event(f"Dio a luz a {baby.first_name}", current_date)
            father.add_event(f"Nació su hijo/a {baby.first_name}", current_date)
            baby.add_event("Nacimiento", current_date)
            
            return True, f"👶 ¡Nació {baby.first_name} {baby.last_name}! Padres: {mother.first_name} y {father.first_name}"
        
        return False, "Error al registrar el nacimiento"

    @staticmethod
    def ejecutar_ciclo_cumpleanos(family: Family) -> list:
        """Ejecuta cumpleaños para todas las personas vivas"""
        eventos = []
        current_date = datetime.datetime.now()
        
        for person in family.get_living_members():
            # Incrementar edad virtual
            person.virtual_age = getattr(person, 'virtual_age', person.calculate_age()) + 1
            
            # Actualizar año de nacimiento virtual para mantener consistencia
            birth_year = int(person.birth_date[:4]) if person.birth_date else current_date.year - 20
            person.virtual_birth_year = birth_year - person.virtual_age
            
            # Registrar evento
            person.add_event(f"Cumpleaños #{person.virtual_age}", current_date.strftime("%Y-%m-%d"))
            eventos.append(f"🎂 {person.first_name} {person.last_name} cumple {person.virtual_age} años")
            
            # Efectos del envejecimiento
            SimulacionService._aplicar_efectos_edad(person, eventos)
        
        return eventos

    @staticmethod
    def _aplicar_efectos_edad(person: Person, eventos: list):
        """Aplica efectos del envejecimiento"""
        edad = getattr(person, 'virtual_age', person.calculate_age())
        
        # Efectos por rango de edad
        if edad == 18:
            eventos.append(f"✨ {person.first_name} alcanza la mayoría de edad")
        elif edad == 65:
            person.add_event("Jubilación", datetime.datetime.now().strftime("%Y-%m-%d"))
            eventos.append(f"🏆 {person.first_name} se jubila")
        
        # Deterioro de salud emocional con la edad
        if edad > 70 and random.random() < 0.3:
            person.emotional_health = max(10, person.emotional_health - random.randint(1, 3))

    @staticmethod
    def ejecutar_ciclo_completo(family: Family, config: SimulationConfig) -> list:
        """Ejecuta todos los eventos del ciclo de simulación"""
        eventos = []
        
        # 1. Cumpleaños automáticos
        birthday_events = SimulacionService.ejecutar_ciclo_cumpleanos(family)
        eventos.extend(birthday_events)
        
        # 2. Fallecimientos probabilísticos
        death_events = SimulacionService.procesar_fallecimientos(family)
        eventos.extend(death_events)
        
        # 3. Búsqueda de parejas
        romance_events = SimulacionService.procesar_busqueda_parejas(family, config)
        eventos.extend(romance_events)
        
        # 4. Nacimientos
        birth_events = SimulacionService.procesar_nacimientos(family, config)
        eventos.extend(birth_events)
        
        # 5. Efectos colaterales
        side_effects = SimulacionService.procesar_efectos_colaterales(family)
        eventos.extend(side_effects)
        
        return eventos
    
    @staticmethod
    def calcular_probabilidad_muerte(person: Person) -> float:
        """Calcula probabilidad de muerte basada en edad y salud"""
        age = getattr(person, 'virtual_age', person.calculate_age())
        
        # Probabilidad base por edad
        if age < 1:
            base_prob = 0.005  # Mortalidad infantil
        elif age < 18:
            base_prob = 0.0001  # Muy baja en jóvenes
        elif age < 50:
            base_prob = 0.001
        elif age < 70:
            base_prob = 0.005
        elif age < 80:
            base_prob = 0.02
        elif age < 90:
            base_prob = 0.08
        else:
            base_prob = 0.15
        
        # Modificadores por salud emocional
        health_modifier = 1.0
        if person.emotional_health < 30:
            health_modifier = 1.5  # 50% más probabilidad
        elif person.emotional_health < 50:
            health_modifier = 1.2  # 20% más probabilidad
        elif person.emotional_health > 80:
            health_modifier = 0.8  # 20% menos probabilidad
        
        # Modificador por estado civil (personas solas tienen mayor riesgo)
        if person.marital_status == "Viudo/a" and age > 65:
            health_modifier *= 1.3
        elif person.marital_status == "Soltero/a" and age > 40:
            years_single = age - 25  # Asumiendo soltería prolongada después de 25
            health_modifier *= (1 + years_single * 0.01)  # 1% adicional por año solo
        
        return min(0.3, base_prob * health_modifier)  # Máximo 30%

    @staticmethod
    def encontrar_tutor_legal_avanzado(child: Person, family: Family) -> tuple:
        """Sistema avanzado de búsqueda de tutores legales"""
        # Prioridad 1: Abuelos vivos
        potential_guardians = []
        
        # Abuelos paternos y maternos
        grandparents = []
        for parent in [child.father, child.mother]:
            if parent:
                for grandparent in [parent.father, parent.mother]:
                    if grandparent and grandparent.alive:
                        age = getattr(grandparent, 'virtual_age', grandparent.calculate_age())
                        if age < 75:  # No muy mayores
                            grandparents.append((grandparent, 'abuelo', 10))
        
        # Prioridad 2: Tíos/Tías menores de 50 años con estabilidad
        aunts_uncles = []
        for parent in [child.father, child.mother]:
            if parent and parent.father:
                for sibling in parent.father.children:
                    if (sibling != parent and sibling.alive and 
                        getattr(sibling, 'virtual_age', sibling.calculate_age()) < 50):
                        stability_score = 8
                        if sibling.spouse:
                            stability_score += 2
                        if sibling.children:
                            stability_score += 1
                        aunts_uncles.append((sibling, 'tío/tía', stability_score))
        
        # Prioridad 3: Hermanos mayores de edad
        older_siblings = []
        for sibling in child.siblings:
            if (sibling.alive and 
                getattr(sibling, 'virtual_age', sibling.calculate_age()) >= 18):
                older_siblings.append((sibling, 'hermano/a', 6))
        
        # Combinar y ordenar por prioridad
        all_candidates = grandparents + aunts_uncles + older_siblings
        all_candidates.sort(key=lambda x: x[2], reverse=True)
        
        if all_candidates:
            guardian, relationship, score = all_candidates[0]
            
            # Registrar la tutoría
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            child.add_event(f"Tutoría asignada a {guardian.first_name} {guardian.last_name} ({relationship})", current_date)
            guardian.add_event(f"Asume tutoría de {child.first_name} {child.last_name}", current_date)
            
            return True, f"👨‍👩‍👧‍👦 {guardian.first_name} {guardian.last_name} asume la tutoría de {child.first_name}"
        
        # Si no hay familiares, buscar en la comunidad
        community_guardians = [p for p in family.members 
                            if (p.alive and p != child and 
                                25 <= getattr(p, 'virtual_age', p.calculate_age()) <= 55 and
                                p.emotional_health > 60)]
        
        if community_guardians:
            guardian = random.choice(community_guardians)
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            child.add_event(f"Tutoría comunitaria asignada a {guardian.first_name} {guardian.last_name}", current_date)
            return True, f"🏘️ {guardian.first_name} {guardian.last_name} asume tutoría comunitaria de {child.first_name}"
        
        return False, f"⚠️ No se encontró tutor para {child.first_name} {child.last_name}"
    
    @staticmethod
    def procesar_efectos_viudez(person: Person, deceased_spouse: Person) -> list:
        """Procesa los efectos emocionales y sociales de la viudez"""
        eventos = []
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # Cambiar estado civil
        person.marital_status = "Viudo/a"
        person.spouse = None
        
        # Impacto emocional inmediato
        emotional_impact = random.randint(25, 40)
        person.emotional_health = max(10, person.emotional_health - emotional_impact)
        
        # Registrar eventos
        person.add_event(f"Viudez por fallecimiento de {deceased_spouse.first_name}", current_date)
        eventos.append(f"💔 {person.first_name} queda viudo/a tras el fallecimiento de {deceased_spouse.first_name}")
        
        # Efectos a largo plazo
        person.widowed_year = getattr(person, 'virtual_age', person.calculate_age())
        person.remarriage_probability = 0.3  # 30% base de volverse a casar
        
        # Reducir probabilidad según edad
        age = getattr(person, 'virtual_age', person.calculate_age())
        if age > 60:
            person.remarriage_probability *= 0.5
        elif age > 70:
            person.remarriage_probability *= 0.2
        
        return eventos

    @staticmethod
    def procesar_efectos_solteria_prolongada(person: Person) -> list:
        """Procesa efectos de soledad prolongada"""
        eventos = []
        age = getattr(person, 'virtual_age', person.calculate_age())
        
        if person.marital_status == "Soltero/a" and age > 30:
            years_single = age - 25  # Asumiendo que la presión social inicia a los 25
            
            # Deterioro gradual de salud emocional
            if years_single > 5 and random.random() < 0.4:  # 40% probabilidad
                health_decline = min(5, years_single // 2)
                person.emotional_health = max(20, person.emotional_health - health_decline)
                
                if years_single == 10:
                    eventos.append(f"😔 {person.first_name} comienza a sentir los efectos de la soledad prolongada")
                    person.add_event("Inicio de efectos por soledad", datetime.datetime.now().strftime("%Y-%m-%d"))
            
            # Aumentar desesperación por encontrar pareja
            person.partner_seeking_intensity = min(2.0, 1.0 + (years_single * 0.1))
        
        return eventos
    
    @staticmethod
    def procesar_efectos_muerte(deceased: Person, family: Family) -> list:
        """Procesa todos los efectos de un fallecimiento"""
        eventos = []
        
        # 1. Viudez del cónyuge
        if deceased.spouse and deceased.spouse.alive:
            viudez_eventos = procesar_efectos_viudez(deceased.spouse, deceased)
            eventos.extend(viudez_eventos)
        
        # 2. Huérfanos menores de edad
        menores = [child for child in deceased.children 
                if child.alive and child.calculate_virtual_age() < 18]
        
        for menor in menores:
            # Si ambos padres murieron, buscar tutor
            if not menor.father.alive and not menor.mother.alive:
                tutor_resultado = encontrar_tutor_legal(menor, family)
                eventos.append(tutor_resultado[1])
        
        # 3. Impacto emocional en hijos adultos
        hijos_adultos = [child for child in deceased.children 
                        if child.alive and child.calculate_virtual_age() >= 18]
        
        for hijo in hijos_adultos:
            # Reducir salud emocional por pérdida del padre/madre
            impacto = random.randint(15, 25)
            hijo.emotional_health = max(20, hijo.emotional_health - impacto)
            hijo.add_event(f"Luto por fallecimiento de {deceased.first_name}", 
                        datetime.datetime.now().strftime("%Y-%m-%d"))
            eventos.append(f"😢 {hijo.first_name} está de luto por {deceased.first_name}")
        
        return eventos