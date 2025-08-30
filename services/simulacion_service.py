from asyncio.log import logger
import logging
import random
import datetime
from typing import Tuple, Optional
from models.family import Family
from models.person import Person
from models.simulation_config import SimulationConfig
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
        if person.marital_status == "Soltero/a" and person.calculate_virtual_age() > 30:
            years_single = family.current_year - int(person.birth_date.split('-')[0]) - 30
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
            if child.alive and child.calculate_virtual_age() < 18:
                # Si el otro padre también falleció, buscar tutor
                if (parent.gender == "M" and child.mother and not child.mother.alive) or \
                   (parent.gender == "F" and child.father and not child.father.alive):
                    SimulacionService.encontrar_tutor_legal_avanzado(child, family)

    @staticmethod
    def simular_nacimiento_mejorado(mother: Person, father: Person, family: Family) -> Tuple[bool, str]:
        """Versión mejorada de simulación de nacimiento con lógica correcta de apellidos"""
        # Verificaciones base
        if not mother.alive or not father.alive:
            return False, "Uno o ambos padres han fallecido"
        
        mother_age = mother.calculate_virtual_age()
        father_age = father.calculate_virtual_age()
        
        # Verificar edad reproductiva
        if not (18 <= mother_age <= 45):
            return False, f"Madre fuera de edad reproductiva ({mother_age} años)"
        
        if not (18 <= father_age <= 65):
            return False, f"Padre fuera de edad reproductiva ({father_age} años)"
        
        # Verificar compatibilidad
        compatibility = SimulacionService.calcular_compatibilidad_total(mother, father)
        if not compatibility['compatible']:
            return False, f"Compatibilidad insuficiente ({compatibility['total']:.1f}%)"
        
        # Generar datos del bebé
        gender = "F" if random.random() < 0.48 else "M"
        first_name, _ = Family.generate_name(gender)
        
        # LÓGICA CORRECTA DE APELLIDOS: Apellido del padre + Apellido de la madre
        # En Costa Rica: [Primer apellido del padre] [Primer apellido de la madre]
        father_surname = father.last_name.split()[0] if father.last_name else "Desconocido"
        mother_surname = mother.last_name.split()[0] if mother.last_name else "Desconocida"
        last_name = f"{father_surname} {mother_surname}"
        
        # Generar cédula única
        cedula = Family.generate_cedula()
        while not Family.validate_cedula_unique(cedula, family):
            cedula = Family.generate_cedula()
        
        # Provincia: Hereda principalmente del padre (60%) o madre (40%)
        province = father.province if random.random() < 0.6 else mother.province
        
        # Crear bebé
        current_date = f"{family.current_year}-01-01"
        baby = Person(
            cedula=cedula,
            first_name=first_name,
            last_name=last_name,
            birth_date=current_date,
            gender=gender,
            province=province,
            marital_status="Soltero/a"
        )
        
        # Edad virtual inicial
        baby.virtual_age = 0
        
        # Heredar intereses de los padres de forma inteligente
        parent_interests = list(set(mother.interests + father.interests))
        baby_base_interests = ["Juegos", "Dibujo", "Música", "Cuentos", "Naturaleza"]
        
        # Los bebés empiezan con intereses de bebé
        baby.interests = random.sample(baby_base_interests, min(2, len(baby_base_interests)))
        
        # Ocasionalmente heredan 1 interés de los padres (10% probabilidad)
        if parent_interests and random.random() < 0.1:
            inherited_interest = random.choice(parent_interests)
            if inherited_interest not in baby.interests:
                baby.interests.append(inherited_interest)
        
        # Establecer salud emocional inicial alta
        baby.emotional_health = random.randint(85, 100)
        
        # Agregar a la familia
        family.add_or_update_member(baby)
        
        # ✅ CORRECCIÓN: Importar RelacionService LOCALMENTE para evitar importación circular
        from services.relacion_service import RelacionService
        
        # Registrar relaciones familiares
        success, message = RelacionService.registrar_padres(
            family, baby.cedula, mother.cedula, father.cedula
        )
        
        if success:
            # Registrar evento en todos los involucrados
            mother.add_event(f"Dio a luz a {baby.first_name} {baby.last_name}", current_date)
            father.add_event(f"Nació su hijo/a {baby.first_name} {baby.last_name}", current_date)
            baby.add_event("Nacimiento", current_date)
            
            # Efecto positivo en la salud emocional de los padres
            mother.emotional_health = min(100, mother.emotional_health + random.randint(5, 15))
            father.emotional_health = min(100, father.emotional_health + random.randint(5, 15))
            
            return True, f"👶 ¡Nació {baby.first_name} {baby.last_name}! Padres: {mother.first_name} y {father.first_name}"
        
        return False, "Error al registrar el nacimiento"
        
        # Provincia: Hereda de los padres
        province = father.province if random.random() < 0.6 else mother.province
        
        # Crear bebé
        current_date = f"{family.current_year}-01-01"
        baby = Person(
            cedula=cedula,
            first_name=first_name,
            last_name=last_name,
            birth_date=current_date,
            gender=gender,
            province=province,
            marital_status="Soltero/a"
        )
        
        # Edad virtual inicial
        baby.virtual_age = 0
        
        # Heredar algunos intereses de los padres
        parent_interests = list(set(mother.interests + father.interests))
        if parent_interests:
            baby.interests = random.sample(parent_interests, min(2, len(parent_interests)))
        else:
            baby.interests = random.sample(["Juegos", "Dibujo", "Música"], 2)
        
        # Agregar intereses de bebé
        baby_interests = ["Juegos", "Dibujo", "Música"]
        baby.interests.extend(random.sample(baby_interests, 1))
        
        # Agregar a la familia
        family.add_or_update_member(baby)
        
        # ✅ CORRECCIÓN: Importar RelacionService LOCALMENTE para evitar importación circular
        from services.relacion_service import RelacionService
        
        # Registrar relaciones familiares
        success, message = RelacionService.registrar_padres(
            family, baby.cedula, mother.cedula, father.cedula
        )
        
        if success:
            # Registrar evento en todos los involucrados
            mother.add_event(f"Dio a luz a {baby.first_name}", current_date)
            father.add_event(f"Nació su hijo/a {baby.first_name}", current_date)
            baby.add_event("Nacimiento", current_date)
            
            return True, f"👶 ¡Nació {baby.first_name} {baby.last_name}! Padres: {mother.first_name} y {father.first_name}"
        
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
            age = person.calculate_virtual_age()
            death_probability = config.death_probability_base
            if age > 60:
                death_probability += 0.01 * (age - 60)
                
            if random.random() < death_probability:
                success, message = SimulacionService.simular_fallecimiento(person, family)
                if success:
                    eventos.append(message)
            
            # Probabilidad de encontrar pareja (solo para mayores de 18 años)
            if (person.alive and 
                person.calculate_virtual_age() >= 18 and 
                person.marital_status == "Soltero/a" and 
                random.random() < config.find_partner_probability and 
                not person.has_partner()):
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
                
                success, message = SimulacionService.simular_nacimiento_mejorado(
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
    def calcular_compatibilidad_total(person1: Person, person2: Person) -> dict:
        """Sistema completo de compatibilidad con 4 factores principales"""
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
        if SimulacionService.es_compatible_geneticamente(person1, person2):
            scores['genetic'] = 20
        else:
            scores['genetic'] = 0
        
        total = sum(scores.values())
        
        return {
            'total': total,
            'compatible': total >= 70,  # Umbral del 70%
            'breakdown': scores,
            'common_interests': list(set(person1.interests) & set(person2.interests)),
            'recommendation': SimulacionService.get_compatibility_message(total)
        }

    @staticmethod
    def get_compatibility_message(score):
        """Genera un mensaje descriptivo basado en el puntaje de compatibilidad"""
        if score >= 85:
            return "💕 Pareja perfecta - Compatibilidad excepcional en todos los aspectos"
        elif score >= 70:
            return "💖 Muy compatible - Tienen un buen potencial para una relación estable"
        elif score >= 50:
            return "💛 Compatible con esfuerzo - Necesitarán trabajar en algunas áreas para mantener la relación"
        else:
            return "💔 Incompatible - Altas probabilidades de conflictos y problemas en la relación"

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
        age_diff = abs(person1.calculate_virtual_age() - person2.calculate_virtual_age())
        if age_diff > 40:
            return False
        
        return True

    @staticmethod
    def verificar_requisitos_union(person1: Person, person2: Person, family: Family) -> tuple:
        """
        Verifica todos los requisitos para una unión de pareja
        
        Returns:
            tuple: (bool, str) - (Es compatible, Mensaje de resultado)
        """
        # 1. Verificar edad mínima (18 años)
        if person1.calculate_virtual_age() < 18:
            return False, f"{person1.first_name} debe ser mayor de 18 años ({person1.calculate_virtual_age()} años)"
        if person2.calculate_virtual_age() < 18:
            return False, f"{person2.first_name} debe ser mayor de 18 años ({person2.calculate_virtual_age()} años)"
        
        # 2. Verificar estado civil (no pueden estar unidos a otra persona)
        if person1.has_partner():
            return False, f"{person1.first_name} ya está en una relación"
        if person2.has_partner():
            return False, f"{person2.first_name} ya está en una relación"
        
        # 3. Verificar diferencia de edad (máximo 15 años)
        age_diff = abs(person1.calculate_virtual_age() - person2.calculate_virtual_age())
        if age_diff > 15:
            return False, f"Diferencia de edad excesiva ({age_diff} años). Máximo permitido: 15 años"
        
        # 4. Verificar compatibilidad genética
        if not SimulacionService.es_compatible_geneticamente(person1, person2):
            return False, "Incompatibilidad genética detectada. No se recomienda la unión por riesgos en descendencia"
        
        # 5. Verificar compatibilidad emocional (intereses en común)
        common_interests = set(person1.interests) & set(person2.interests)
        if len(common_interests) < 2:
            return False, f"Se requieren al menos 2 intereses en común. Tienen {len(common_interests)} interés(es) compartido(s)"
        
        # 6. Verificar índice de compatibilidad
        compatibility = SimulacionService.calcular_compatibilidad_total(person1, person2)
        if not compatibility['compatible']:
            return False, f"Índice de compatibilidad insuficiente ({compatibility['total']:.1f}%). Mínimo requerido: 70%"
        
        return True, f"✅ {person1.first_name} y {person2.first_name} cumplen con todos los requisitos para formar pareja"

    @staticmethod
    def intentar_encontrar_pareja(person: Person, family: Family) -> bool:
        """Intenta encontrar una pareja para una persona soltera, priorizando generar personas externas"""
        if not person.alive or person.has_partner():
            return False
        
        # PRIORIDAD 1: Generar persona externa (80% de probabilidad)
        if random.random() < 0.8:
            return SimulacionService.generar_persona_externa_para_pareja(person, family)
        
        # PRIORIDAD 2: Buscar dentro de la familia existente (20% de probabilidad)
        possible_partners = []
        for potential in family.members:
            if (potential != person and 
                potential.alive and 
                not potential.has_partner() and 
                potential.gender != person.gender and
                potential.calculate_virtual_age() >= 18):
                
                # Verificar compatibilidad completa
                compatibility = SimulacionService.calcular_compatibilidad_total(person, potential)
                
                # Requisitos mínimos para pareja interna
                age_diff = abs(person.calculate_virtual_age() - potential.calculate_virtual_age())
                if (age_diff <= 15 and 
                    compatibility['total'] >= 60 and  # Umbral más bajo para familia existente
                    SimulacionService.es_compatible_geneticamente(person, potential)):
                    possible_partners.append((potential, compatibility['total']))
        
        # Si hay parejas compatibles dentro de la familia, elegir la mejor
        if possible_partners:
            partner, compatibility_score = max(possible_partners, key=lambda x: x[1])
            
            # ✅ CORRECCIÓN: Importar RelacionService LOCALMENTE para evitar importación circular
            from services.relacion_service import RelacionService
            
            success, _ = RelacionService.registrar_pareja(family, person.cedula, partner.cedula, es_simulacion=True)
            if success:
                current_date = f"{family.current_year}-01-01"
                person.add_event(f"Formó pareja con {partner.first_name} {partner.last_name}", current_date)
                partner.add_event(f"Formó pareja con {person.first_name} {person.last_name}", current_date)
                logger.info(f"{person.first_name} y {partner.first_name} formaron pareja (compatibilidad: {compatibility_score:.1f}%)")
                return True
        
        # Si no hay parejas internas compatibles, generar persona externa como respaldo
        return SimulacionService.generar_persona_externa_para_pareja(person, family)
    
    @staticmethod
    def generar_persona_externa_para_pareja(person: Person, family: Family) -> bool:
        """Genera una persona externa compatible para formar pareja con alguien de la familia"""
        # Determinar género de la pareja
        target_gender = "F" if person.gender == "M" else "M"
    
        # Generar cédula única
        cedula = Family.generate_cedula()
        while not Family.validate_cedula_unique(cedula, family):
            cedula = Family.generate_cedula()
    
        # Generar nombre y apellido únicos (evitar apellidos existentes en la familia)
        first_name, _ = Family.generate_name(target_gender)
        
        # Generar apellido único no usado en la familia
        existing_surnames = set(member.last_name for member in family.members)
        all_surnames = ["González", "Vargas", "Morales", "Castro", "Rojas", "Herrera", "Vega", "Ramírez", 
                       "Aguilar", "Solano", "Mora", "Araya", "Villalobos", "Cordero", "Chaves", "Monge", 
                       "Quesada", "Carballo", "Mendez", "Esquivel", "Segura", "Trejos", "Salas", "Picado"]
        
        available_surnames = [s for s in all_surnames if s not in existing_surnames]
        last_name = random.choice(available_surnames) if available_surnames else random.choice(all_surnames)
    
        # Generar edad compatible con la persona original
        person_age = person.calculate_virtual_age()
        age_diff = random.randint(-8, 8)  # Diferencia de hasta 8 años
        age = max(18, min(85, person_age + age_diff))
    
        # Calcular fecha de nacimiento
        current_year = family.current_year
        birth_year = current_year - age
        birth_date = f"{birth_year}-01-01"
    
        # Determinar provincia (60% misma provincia, 40% diferente)
        provinces = ["San José", "Alajuela", "Cartago", "Heredia", "Guanacaste", "Puntarenas", "Limón"]
        if random.random() < 0.6:
            province = person.province
        else:
            province = random.choice([p for p in provinces if p != person.province])
    
        # Crear la persona externa
        new_partner = Person(
            cedula=cedula,
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date,
            gender=target_gender,
            province=province,
            marital_status="Soltero/a"
        )
    
        # Establecer edad virtual
        new_partner.virtual_age = age
    
        # Generar intereses compatibles (al menos 2 en común con la persona original)
        person_interests = set(person.interests) if person.interests else set()
        base_interests = ["Trabajo", "Familia", "Deportes", "Lectura", "Música", "Viajes", "Arte", 
                         "Cocina", "Tecnología", "Cine", "Naturaleza", "Fotografía"]
        
        # Asegurar al menos 2 intereses comunes
        common_interests = random.sample(list(person_interests), min(2, len(person_interests)))
        
        # Agregar intereses adicionales únicos
        remaining_interests = [i for i in base_interests if i not in common_interests and i not in person_interests]
        additional_interests = random.sample(remaining_interests, min(2, len(remaining_interests)))
        
        new_partner.interests = common_interests + additional_interests
    
        # Establecer salud emocional compatible
        person_health = getattr(person, 'emotional_health', 70)
        health_variation = random.randint(-15, 15)
        new_partner.emotional_health = max(50, min(100, person_health + health_variation))
    
        # Agregar a la familia
        family.add_or_update_member(new_partner)
        
        # Registrar evento de creación
        current_date = f"{family.current_year}-01-01"
        new_partner.add_event(f"Se unió a la familia como pareja de {person.first_name}", current_date)
        person.add_event(f"Conoció a {new_partner.first_name} {new_partner.last_name}", current_date)
    
        # ✅ CORRECCIÓN: Importar RelacionService LOCALMENTE para evitar importación circular
        from services.relacion_service import RelacionService
        
        # Registrar pareja
        success, message = RelacionService.registrar_pareja(family, person.cedula, new_partner.cedula, es_simulacion=True)
    
        if success:
            # ✅ CORRECCIÓN CRÍTICA: Asegurar que las referencias bidireccionales estén correctas
            # Esto garantiza que la persona externa aparezca conectada en el árbol genealógico
            
            # Actualizar referencias en la familia para ambas personas
            person_in_family = family.get_member_by_cedula(person.cedula)
            partner_in_family = family.get_member_by_cedula(new_partner.cedula)
            
            if person_in_family and partner_in_family:
                # Establecer relación bidireccional explícitamente
                person_in_family.spouse = partner_in_family
                partner_in_family.spouse = person_in_family
                
                # Actualizar estados civiles
                person_in_family.marital_status = "Casado/a"
                partner_in_family.marital_status = "Casado/a"
                
                # Registrar eventos de matrimonio
                marriage_date = f"{family.current_year}-01-01"
                person_in_family.add_event(f"Matrimonio con {partner_in_family.first_name} {partner_in_family.last_name}", marriage_date)
                partner_in_family.add_event(f"Matrimonio con {person_in_family.first_name} {person_in_family.last_name}", marriage_date)
            
            logger.info(f"✅ Persona externa {new_partner.first_name} {new_partner.last_name} registrada exitosamente como pareja de {person.first_name}")
            return True
        else:
            # Si falla el registro de pareja, remover la persona de la familia
            family.members = [m for m in family.members if m.cedula != new_partner.cedula]
            logger.error(f"❌ Error registrando pareja externa: {message}")
            return False
            logger.info(f"Intereses comunes: {common_interests}")
            return True
    
        return False

    @staticmethod
    def generar_poblacion_externa(family: Family, cantidad: int = 5) -> list:
        """Genera múltiples personas externas para enriquecer el pool de candidatos a pareja"""
        personas_generadas = []
        
        # Diversificar edades y géneros
        for i in range(cantidad):
            # Alternar géneros
            gender = "M" if i % 2 == 0 else "F"
            
            # Generar cédula única
            cedula = Family.generate_cedula()
            while not Family.validate_cedula_unique(cedula, family):
                cedula = Family.generate_cedula()
            
            # Generar nombre y apellido únicos
            first_name, _ = Family.generate_name(gender)
            existing_surnames = set(member.last_name.split()[0] for member in family.members if member.last_name)
            
            all_surnames = ["González", "Vargas", "Morales", "Castro", "Rojas", "Herrera", "Vega", "Ramírez", 
                           "Aguilar", "Solano", "Mora", "Araya", "Villalobos", "Cordero", "Chaves", "Monge", 
                           "Quesada", "Carballo", "Mendez", "Esquivel", "Segura", "Trejos", "Salas", "Picado",
                           "Mena", "Fallas", "Alfaro", "Ulate", "Zúñiga", "Calderón", "Matarrita", "Elizondo"]
            
            available_surnames = [s for s in all_surnames if s not in existing_surnames]
            last_name = random.choice(available_surnames) if available_surnames else random.choice(all_surnames)
            
            # Generar edad adulta (20-60 años)
            age = random.randint(20, 60)
            birth_year = family.current_year - age
            birth_date = f"{birth_year}-01-01"
            
            # Provincia aleatoria
            provinces = ["San José", "Alajuela", "Cartago", "Heredia", "Guanacaste", "Puntarenas", "Limón"]
            province = random.choice(provinces)
            
            # Crear persona
            new_person = Person(
                cedula=cedula,
                first_name=first_name,
                last_name=last_name,
                birth_date=birth_date,
                gender=gender,
                province=province,
                marital_status="Soltero/a"
            )
            
            # Establecer edad virtual
            new_person.virtual_age = age
            
            # Intereses variados
            base_interests = ["Trabajo", "Familia", "Deportes", "Lectura", "Música", "Viajes", "Arte", 
                             "Cocina", "Tecnología", "Cine", "Naturaleza", "Fotografía", "Baile", "Estudio"]
            new_person.interests = random.sample(base_interests, random.randint(3, 6))
            
            # Salud emocional variada pero generalmente buena
            new_person.emotional_health = random.randint(60, 95)
            
            # Agregar a la familia
            family.add_or_update_member(new_person)
            personas_generadas.append(new_person)
            
            # Registrar evento
            current_date = f"{family.current_year}-01-01"
            new_person.add_event("Se unió a la comunidad", current_date)
        
        return personas_generadas

    @staticmethod
    def ejecutar_ciclo_cumpleanos(family: Family) -> list:
        """Ejecuta cumpleaños para todas las personas vivas"""
        eventos = []
        current_date = f"{family.current_year}-01-01"
        
        for person in family.get_living_members():
            # Incrementar edad virtual
            person.incrementar_edad_virtual(1)
            
            # Registrar evento
            person.add_event(f"Cumpleaños #{person.virtual_age}", current_date)
            eventos.append(f"🎂 {person.first_name} {person.last_name} cumple {person.virtual_age} años")
            
            # Efectos del envejecimiento
            SimulacionService._aplicar_efectos_edad(person, eventos)
        
        return eventos

    @staticmethod
    def _aplicar_efectos_edad(person: Person, eventos: list):
        """Aplica efectos del envejecimiento"""
        edad = person.calculate_virtual_age()
        
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
        age = person.calculate_virtual_age()
        
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
        
        # Modificador por estado civil
        if person.marital_status == "Viudo/a" and age > 65:
            health_modifier *= 1.3
        elif person.marital_status == "Soltero/a" and age > 40:
            years_single = age - 25
            health_modifier *= (1 + years_single * 0.01)
        
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
                        age = grandparent.calculate_virtual_age()
                        if age < 75:  # No muy mayores
                            grandparents.append((grandparent, 'abuelo', 10))
        
        # Prioridad 2: Tíos/Tías menores de 50 años con estabilidad
        aunts_uncles = []
        for parent in [child.father, child.mother]:
            if parent and parent.father:
                for sibling in parent.father.children:
                    if (sibling != parent and sibling.alive and 
                        sibling.calculate_virtual_age() < 50):
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
                sibling.calculate_virtual_age() >= 18):
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
                                25 <= p.calculate_virtual_age() <= 55 and
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
        person.widowed_year = person.calculate_virtual_age()
        person.remarriage_probability = 0.3  # 30% base de volverse a casar
        
        # Reducir probabilidad según edad
        age = person.calculate_virtual_age()
        if age > 60:
            person.remarriage_probability *= 0.5
        elif age > 70:
            person.remarriage_probability *= 0.2
        
        return eventos

    @staticmethod
    def procesar_efectos_solteria_prolongada(person: Person) -> list:
        """Procesa efectos de soledad prolongada"""
        eventos = []
        age = person.calculate_virtual_age()
        
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
            viudez_events = SimulacionService.procesar_efectos_viudez(deceased.spouse, deceased)
            eventos.extend(viudez_events)
        
        # 2. Huérfanos menores de edad
        menores = [child for child in deceased.children 
                if child.alive and child.calculate_virtual_age() < 18]
        
        for menor in menores:
            # Si ambos padres murieron, buscar tutor
            if not menor.father.alive and not menor.mother.alive:
                tutor_resultado = SimulacionService.encontrar_tutor_legal_avanzado(menor, family)
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

    @staticmethod
    def procesar_fallecimientos(family: Family) -> list:
        """Procesa fallecimientos probabilísticos"""
        eventos = []
        
        for person in family.get_living_members().copy():
            death_prob = SimulacionService.calcular_probabilidad_muerte(person)
            
            if random.random() < death_prob:
                # Procesar fallecimiento
                person.alive = False
                person.death_date = datetime.datetime.now().strftime("%Y-%m-%d")
                person.add_event("Fallecimiento", person.death_date)
                
                # Registrar en eventos
                eventos.append(f"⚰️ {person.first_name} {person.last_name} ha fallecido a los {person.calculate_virtual_age()} años")
                
                # Procesar efectos colaterales
                if person.spouse and person.spouse.alive:
                    viudez_events = SimulacionService.procesar_efectos_viudez(person.spouse, person)
                    eventos.extend(viudez_events)
                
                # Manejar hijos menores
                for child in person.children:
                    if child.alive and child.calculate_virtual_age() < 18:
                        both_parents_dead = (
                            (not child.father or not child.father.alive) and
                            (not child.mother or not child.mother.alive)
                        )
                        if both_parents_dead:
                            tutor_success, tutor_msg = SimulacionService.encontrar_tutor_legal_avanzado(child, family)
                            if tutor_success:
                                eventos.append(tutor_msg)
        
        return eventos
        
    @staticmethod
    def procesar_busqueda_parejas(family: Family, config: SimulationConfig) -> list:
        """Procesa búsqueda de parejas con énfasis en generación de personas externas"""
        eventos = []
        
        # Obtener solteros elegibles
        solteros = [p for p in family.get_living_members() 
                if (p.marital_status == "Soltero/a" and 
                    p.calculate_virtual_age() >= config.min_marriage_age and
                    not p.has_partner())]
        
        # Filtrar por edad y probabilidad
        candidatos_activos = []
        for person in solteros:
            age = person.calculate_virtual_age()
            # Probabilidad aumenta con la edad hasta cierto punto
            age_factor = 1.0
            if age >= 25:
                age_factor = 1.5
            if age >= 30:
                age_factor = 2.0
            if age >= 35:
                age_factor = 2.5
            if age >= 45:
                age_factor = 1.5  # Disminuye después de 45
            
            adjusted_probability = config.find_partner_probability * age_factor
            
            if random.random() < adjusted_probability:
                candidatos_activos.append(person)
        
        # Procesar cada candidato
        for person in candidatos_activos:
            # Priorizar generación de personas externas (85% probabilidad)
            if random.random() < 0.85:
                success = SimulacionService.generar_persona_externa_para_pareja(person, family)
                if success:
                    partner = person.spouse
                    compatibility = SimulacionService.calcular_compatibilidad_total(person, partner)
                    current_date = f"{family.current_year}-01-01"
                    
                    person.add_event(f"Matrimonio con {partner.first_name} {partner.last_name}", current_date)
                    partner.add_event(f"Matrimonio con {person.first_name} {person.last_name}", current_date)
                    
                    eventos.append(f"💍 {person.first_name} se casó con {partner.first_name} {partner.last_name} (persona externa, compatibilidad: {compatibility['total']:.1f}%)")
                    continue
            
            # Buscar pareja dentro de la familia (15% probabilidad)
            possible_partners = []
            for potential in family.get_living_members():
                if (potential != person and 
                    not potential.has_partner() and
                    potential.gender != person.gender and
                    potential.calculate_virtual_age() >= config.min_marriage_age):
                    
                    compatibility = SimulacionService.calcular_compatibilidad_total(person, potential)
                    if compatibility['compatible']:
                        possible_partners.append((potential, compatibility['total']))
            
            if possible_partners:
                # Elegir al más compatible
                possible_partners.sort(key=lambda x: x[1], reverse=True)
                partner, compatibility_score = possible_partners[0]
                
                # ✅ CORRECCIÓN: Importar RelacionService LOCALMENTE para evitar importación circular
                from services.relacion_service import RelacionService
                
                # Registrar pareja
                success, message = RelacionService.registrar_pareja(family, person.cedula, partner.cedula, es_simulacion=True)
                if success:
                    current_date = f"{family.current_year}-01-01"
                    person.add_event(f"Matrimonio con {partner.first_name} {partner.last_name}", current_date)
                    partner.add_event(f"Matrimonio con {person.first_name} {person.last_name}", current_date)
                    eventos.append(f"💍 {person.first_name} y {partner.first_name} se casaron (familia interna, compatibilidad: {compatibility_score:.1f}%)")
        
        return eventos
    
    @staticmethod
    def procesar_nacimientos(family: Family, config: SimulationConfig) -> list:
        """Procesa nacimientos de parejas"""
        eventos = []
        
        # Obtener parejas fértiles
        parejas_fertiles = []
        for person in family.get_living_members():
            if (person.has_partner() and person.spouse and person.spouse.alive and
                person.gender == "F"):  # Solo procesar desde la mujer para evitar duplicados
                
                woman_age = person.calculate_virtual_age()
                man_age = person.spouse.calculate_virtual_age()
                
                if (config.min_marriage_age <= woman_age <= config.max_female_fertility and
                    config.min_marriage_age <= man_age <= config.max_male_fertility):
                    parejas_fertiles.append((person, person.spouse))
        
        for mother, father in parejas_fertiles:
            if random.random() < config.birth_probability:
                success, message = SimulacionService.simular_nacimiento_mejorado(mother, father, family)
                if success:
                    eventos.append(message)
        
        return eventos
    
    @staticmethod
    def procesar_efectos_colaterales(family: Family) -> list:
        """Procesa efectos colaterales de eventos familiares"""
        eventos = []
        
        for person in family.get_living_members():
            # Efectos de soledad prolongada
            soledad_events = SimulacionService.procesar_efectos_solteria_prolongada(person)
            eventos.extend(soledad_events)
            
            # Efectos de envejecimiento en viudos
            if person.marital_status == "Viudo/a":
                age = person.calculate_virtual_age()
                if age > 65 and random.random() < 0.2:  # 20% probabilidad
                    decline = random.randint(1, 3)
                    person.emotional_health = max(10, person.emotional_health - decline)
                    if decline >= 2:
                        eventos.append(f"😔 {person.first_name} sufre deterioro emocional por viudez prolongada")
        
        return eventos