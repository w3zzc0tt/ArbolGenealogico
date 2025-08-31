"""
Servicio para analizar relaciones familiares y ejecutar consultas genealógicas complejas.
"""
from datetime import datetime, date
from typing import List, Optional, Tuple, Set
from models.person import Person
from models.family import Family


class RelacionService:
    """Servicio para analizar relaciones familiares"""
    
    @staticmethod
    def encontrar_relacion(persona_a: Person, persona_b: Person) -> str:
        """
        Encuentra la relación familiar entre dos personas.
        
        Args:
            persona_a: Primera persona
            persona_b: Segunda persona
            
        Returns:
            str: Descripción de la relación entre las personas
        """
        if persona_a.cedula == persona_b.cedula:
            return "Es la misma persona"
        
        # Verificar relación directa de pareja
        if persona_a.spouse and persona_a.spouse.cedula == persona_b.cedula:
            return "Son cónyuges/pareja"
        
        # Verificar relación padre-hijo
        if persona_a.father and persona_a.father.cedula == persona_b.cedula:
            return f"{persona_b.first_name} es el padre de {persona_a.first_name}"
        if persona_a.mother and persona_a.mother.cedula == persona_b.cedula:
            return f"{persona_b.first_name} es la madre de {persona_a.first_name}"
        
        # Verificar relación hijo-padre
        if persona_b.father and persona_b.father.cedula == persona_a.cedula:
            return f"{persona_a.first_name} es el padre de {persona_b.first_name}"
        if persona_b.mother and persona_b.mother.cedula == persona_a.cedula:
            return f"{persona_a.first_name} es la madre de {persona_b.first_name}"
        
        # Verificar hermanos
        if persona_a.siblings:
            for hermano in persona_a.siblings:
                if hermano.cedula == persona_b.cedula:
                    return "Son hermanos"
        
        # Verificar abuelos
        relacion_abuelo = RelacionService._verificar_relacion_abuelo(persona_a, persona_b)
        if relacion_abuelo:
            return relacion_abuelo
        
        # Verificar primos
        relacion_primo = RelacionService._verificar_relacion_primo(persona_a, persona_b)
        if relacion_primo:
            return relacion_primo
        
        # Verificar tíos/sobrinos
        relacion_tio = RelacionService._verificar_relacion_tio_sobrino(persona_a, persona_b)
        if relacion_tio:
            return relacion_tio
        
        return "No se encontró relación familiar directa"
    
    @staticmethod
    def _verificar_relacion_abuelo(persona_a: Person, persona_b: Person) -> Optional[str]:
        """Verifica si hay relación abuelo-nieto"""
        # A es abuelo de B
        if persona_a.children:
            for hijo in persona_a.children:
                if hijo.children:
                    for nieto in hijo.children:
                        if nieto.cedula == persona_b.cedula:
                            return f"{persona_a.first_name} es {'abuelo' if persona_a.gender == 'M' else 'abuela'} de {persona_b.first_name}"
        
        # B es abuelo de A
        if persona_b.children:
            for hijo in persona_b.children:
                if hijo.children:
                    for nieto in hijo.children:
                        if nieto.cedula == persona_a.cedula:
                            return f"{persona_b.first_name} es {'abuelo' if persona_b.gender == 'M' else 'abuela'} de {persona_a.first_name}"
        
        return None
    
    @staticmethod
    def _verificar_relacion_primo(persona_a: Person, persona_b: Person) -> Optional[str]:
        """Verifica si son primos"""
        # Obtener abuelos de A
        abuelos_a = set()
        if persona_a.father:
            if persona_a.father.father:
                abuelos_a.add(persona_a.father.father.cedula)
            if persona_a.father.mother:
                abuelos_a.add(persona_a.father.mother.cedula)
        if persona_a.mother:
            if persona_a.mother.father:
                abuelos_a.add(persona_a.mother.father.cedula)
            if persona_a.mother.mother:
                abuelos_a.add(persona_a.mother.mother.cedula)
        
        # Obtener abuelos de B
        abuelos_b = set()
        if persona_b.father:
            if persona_b.father.father:
                abuelos_b.add(persona_b.father.father.cedula)
            if persona_b.father.mother:
                abuelos_b.add(persona_b.father.mother.cedula)
        if persona_b.mother:
            if persona_b.mother.father:
                abuelos_b.add(persona_b.mother.father.cedula)
            if persona_b.mother.mother:
                abuelos_b.add(persona_b.mother.mother.cedula)
        
        # Si comparten abuelos, son primos
        if abuelos_a & abuelos_b:
            return "Son primos"
        
        return None
    
    @staticmethod
    def _verificar_relacion_tio_sobrino(persona_a: Person, persona_b: Person) -> Optional[str]:
        """Verifica relación tío-sobrino"""
        # A es tío de B
        if persona_a.siblings:
            for hermano in persona_a.siblings:
                if hermano.children:
                    for sobrino in hermano.children:
                        if sobrino.cedula == persona_b.cedula:
                            return f"{persona_a.first_name} es {'tío' if persona_a.gender == 'M' else 'tía'} de {persona_b.first_name}"
        
        # B es tío de A
        if persona_b.siblings:
            for hermano in persona_b.siblings:
                if hermano.children:
                    for sobrino in hermano.children:
                        if sobrino.cedula == persona_a.cedula:
                            return f"{persona_b.first_name} es {'tío' if persona_b.gender == 'M' else 'tía'} de {persona_a.first_name}"
        
        return None
    
    @staticmethod
    def obtener_primos_primer_grado(persona: Person) -> List[Person]:
        """
        Obtiene todos los primos de primer grado de una persona.
        Los primos de primer grado son hijos de los hermanos de los padres.
        """
        primos = []
        
        # Primos por lado paterno
        if persona.father and persona.father.siblings:
            for tio in persona.father.siblings:
                if tio.children:
                    primos.extend(tio.children)
        
        # Primos por lado materno
        if persona.mother and persona.mother.siblings:
            for tia in persona.mother.siblings:
                if tia.children:
                    primos.extend(tia.children)
        
        # Eliminar duplicados y a la persona misma
        primos_unicos = []
        cedulas_vistas = set()
        for primo in primos:
            if primo.cedula != persona.cedula and primo.cedula not in cedulas_vistas:
                primos_unicos.append(primo)
                cedulas_vistas.add(primo.cedula)
        
        return primos_unicos
    
    @staticmethod
    def obtener_antepasados_maternos(persona: Person) -> List[Person]:
        """
        Obtiene todos los antepasados por línea materna.
        """
        antepasados = []
        
        def buscar_antepasados_maternos(p: Person, visitados: Set[str]):
            if not p or p.cedula in visitados:
                return
            
            visitados.add(p.cedula)
            
            # Agregar madre
            if p.mother:
                antepasados.append(p.mother)
                buscar_antepasados_maternos(p.mother, visitados)
        
        if persona.mother:
            buscar_antepasados_maternos(persona, set())
        
        return antepasados
    
    @staticmethod
    def obtener_descendientes_vivos(persona: Person) -> List[Person]:
        """
        Obtiene todos los descendientes vivos de una persona.
        """
        descendientes = []
        
        def buscar_descendientes(p: Person, visitados: Set[str]):
            if not p or p.cedula in visitados:
                return
            
            visitados.add(p.cedula)
            
            if p.children:
                for hijo in p.children:
                    if hijo.alive:
                        descendientes.append(hijo)
                    buscar_descendientes(hijo, visitados)
        
        buscar_descendientes(persona, set())
        return descendientes
    
    @staticmethod
    def obtener_nacimientos_ultimos_10_años(family: Family) -> int:
        """
        Cuenta cuántas personas nacieron en los últimos 10 años.
        """
        año_actual = datetime.now().year
        año_limite = año_actual - 10
        contador = 0
        
        for persona in family.members:
            if persona.birth_date:
                try:
                    # Manejar diferentes formatos de fecha
                    if isinstance(persona.birth_date, str):
                        # Parsear fecha desde string (formato YYYY-MM-DD)
                        fecha_nacimiento = datetime.strptime(persona.birth_date, "%Y-%m-%d")
                        año_nacimiento = fecha_nacimiento.year
                    elif hasattr(persona.birth_date, 'year'):
                        # Es un objeto datetime
                        año_nacimiento = persona.birth_date.year
                    else:
                        continue
                    
                    if año_nacimiento >= año_limite:
                        contador += 1
                except (ValueError, AttributeError):
                    # Si no se puede parsear la fecha, continuar
                    continue
        
        return contador
    
    @staticmethod
    def obtener_parejas_con_hijos(family: Family, min_hijos: int = 2) -> List[Tuple[Person, Person]]:
        """
        Obtiene parejas que tienen un número mínimo de hijos en común.
        """
        parejas_con_hijos = []
        parejas_procesadas = set()
        
        for persona in family.members:
            if persona.spouse and persona.children:
                # Crear ID único para la pareja
                pareja_id = tuple(sorted([persona.cedula, persona.spouse.cedula]))
                
                if pareja_id not in parejas_procesadas:
                    parejas_procesadas.add(pareja_id)
                    
                    # Contar hijos en común
                    hijos_persona = set(hijo.cedula for hijo in persona.children)
                    hijos_conyuge = set(hijo.cedula for hijo in persona.spouse.children) if persona.spouse.children else set()
                    hijos_comunes = hijos_persona & hijos_conyuge
                    
                    if len(hijos_comunes) >= min_hijos:
                        parejas_con_hijos.append((persona, persona.spouse))
        
        return parejas_con_hijos
    
    @staticmethod
    def obtener_fallecidos_antes_50(family: Family) -> int:
        """
        Cuenta cuántas personas fallecieron antes de cumplir 50 años.
        """
        contador = 0
        
        for persona in family.members:
            if not persona.alive and persona.birth_date and persona.death_date:
                try:
                    # Manejar diferentes formatos de fecha
                    if isinstance(persona.birth_date, str) and isinstance(persona.death_date, str):
                        fecha_nacimiento = datetime.strptime(persona.birth_date, "%Y-%m-%d")
                        fecha_muerte = datetime.strptime(persona.death_date, "%Y-%m-%d")
                    elif hasattr(persona.birth_date, 'year') and hasattr(persona.death_date, 'year'):
                        fecha_nacimiento = persona.birth_date
                        fecha_muerte = persona.death_date
                    else:
                        continue
                    
                    edad_muerte = fecha_muerte.year - fecha_nacimiento.year
                    
                    # Ajustar si no había cumplido años en la fecha de muerte
                    if (fecha_muerte.month < fecha_nacimiento.month or 
                        (fecha_muerte.month == fecha_nacimiento.month and 
                         fecha_muerte.day < fecha_nacimiento.day)):
                        edad_muerte -= 1
                    
                    if edad_muerte < 50:
                        contador += 1
                except (ValueError, AttributeError):
                    # Si no se puede parsear las fechas, continuar
                    continue
        
        return contador

    @staticmethod
    def _es_masculino(gender: str) -> bool:
        """Verifica si el género es masculino en cualquier formato"""
        return gender in ["M", "Masculino"]
    
    @staticmethod
    def _es_femenino(gender: str) -> bool:
        """Verifica si el género es femenino en cualquier formato"""
        return gender in ["F", "Femenino"]

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
                        if person not in hermano.siblings:
                            hermano.siblings.append(person)
    
    @staticmethod
    def registrar_pareja(family: Family, person1_cedula: str, 
                        person2_cedula: str, es_simulacion: bool = False) -> Tuple[bool, str]:   
        """
        Registra una unión de pareja entre dos personas
        
        Args:
            family: La familia donde registrar la pareja
            person1_cedula: Cédula de la primera persona
            person2_cedula: Cédula de la segunda persona  
            es_simulacion: Si es True, aplica validaciones completas de simulación.
                          Si es False, solo aplica validaciones básicas para construcción manual.
        """
        person1 = family.get_member_by_cedula(person1_cedula)
        person2 = family.get_member_by_cedula(person2_cedula)
        
        if not person1 or not person2:
            return False, "Una o más personas no existen en la familia"
        
        if person1 == person2:
            return False, "No se puede registrar pareja consigo mismo"
        
        # CORREGIDO: Usar funciones auxiliares para validar géneros
        if RelacionService._es_masculino(person1.gender) and RelacionService._es_masculino(person2.gender):
            return False, "No se puede registrar pareja del mismo género (ambos masculinos)"
        if RelacionService._es_femenino(person1.gender) and RelacionService._es_femenino(person2.gender):
            return False, "No se puede registrar pareja del mismo género (ambas femeninas)"
        
        # Aplicar validaciones según el contexto
        if es_simulacion:
            # Para simulaciones: aplicar todas las validaciones completas
            from services.utils_service import verificar_requisitos_union
            validation = verificar_requisitos_union(person1, person2, family)
            if not validation[0]:
                return False, validation[1]
        else:
            # Para construcción manual: solo validaciones básicas
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
        
        # Verificar si ya están registrados como pareja
        if person1.spouse == person2 and person2.spouse == person1:
            # Asegurar que el estado civil esté correcto
            if "Casado" not in person1.marital_status:
                person1.marital_status = "Casado/a"
            if "Casado" not in person2.marital_status:
                person2.marital_status = "Casado/a"
            return True, "Pareja ya registrada"
        
        # Verificar si alguno ya tiene pareja
        if person1.spouse and person1.spouse != person2:
            return False, f"{person1.first_name} ya tiene pareja"
        if person2.spouse and person2.spouse != person1:
            return False, f"{person2.first_name} ya tiene pareja"
        
        # Establecer relación
        person1.spouse = person2
        person2.spouse = person1
        
        # Actualizar estado civil
        person1.marital_status = "Casado/a"
        person2.marital_status = "Casado/a"
        
        # Registrar evento en ambas personas usando el nuevo sistema
        current_date = datetime.now().strftime("%Y-%m-%d")
        person1.register_life_event('marriage', f'con {person2.first_name}', current_date)
        person2.register_life_event('marriage', f'con {person1.first_name}', current_date)
        
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
        if person1.mother and person2.mother and person1.mother in person2.mother.siblings:
            return "Tío/Tía paterno"
        if person1.mother and person2.father and person1.mother in person2.father.siblings:
            return "Tío/Tía paterno"
        if person1.father and person2.mother and person1.father in person2.mother.siblings:
            return "Tío/Tía materno"
        if person1.father and person2.father and person1.father in person2.father.siblings:
            return "Tío/Tía materno"
        
        # Sobrinos
        for sibling in person1.siblings:
            if person2 in sibling.children:
                return "Sobrino/Sobrina"
        
        # Primos
        if (person1.mother and person2.mother and 
            person1.mother in person2.mother.siblings):
            return "Primo/Prima materno"
        if (person1.father and person2.father and 
            person1.father in person2.father.siblings):
            return "Primo/Prima paterno"
        
        return "Relación no identificada"
    
    @staticmethod
    def obtener_primos_primer_grado(person: Person) -> list:
        """Obtiene los primos de primer grado de una persona (hijos de los hermanos de los padres)"""
        cousins = []
        
        # Obtener hermanos de los padres
        if person.father:
            for sibling in person.father.siblings:
                if sibling.alive:
                    cousins.extend([child for child in sibling.children if child.alive])
        
        if person.mother:
            for sibling in person.mother.siblings:
                if sibling.alive:
                    cousins.extend([child for child in sibling.children if child.alive])
        
        # Eliminar duplicados
        return list(set(cousins))
    
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
    
    @staticmethod
    def registrar_padres(family: Family, child_cedula: str, father_cedula: str = None, mother_cedula: str = None) -> Tuple[bool, str]:
        """
        Registra los padres de un hijo
        """
        child = family.get_member_by_cedula(child_cedula)
        if not child:
            return False, "El hijo no existe en la familia"
        
        # Registrar padre si se proporciona
        if father_cedula:
            father = family.get_member_by_cedula(father_cedula)
            if not father:
                return False, "El padre no existe en la familia"
            
            if not RelacionService._es_masculino(father.gender):
                return False, "La persona designada como padre no es masculina"
            
            # Establecer relación padre-hijo
            child.father = father
            if child not in father.children:
                father.children.append(child)
        
        # Registrar madre si se proporciona
        if mother_cedula:
            mother = family.get_member_by_cedula(mother_cedula)
            if not mother:
                return False, "La madre no existe en la familia"
            
            if not RelacionService._es_femenino(mother.gender):
                return False, "La persona designada como madre no es femenina"
            
            # Establecer relación madre-hijo
            child.mother = mother
            if child not in mother.children:
                mother.children.append(child)
        
        # Actualizar hermanos automáticamente
        RelacionService._actualizar_hermanos(child, family)
        
        return True, "Relación de padres registrada exitosamente"
    
    @staticmethod
    def registrar_hijo_con_pareja(family: Family, parent_cedula: str, child_cedula: str) -> Tuple[bool, str]:
        """
        Registra un hijo para un padre/madre y automáticamente lo asigna al cónyuge
        """
        parent = family.get_member_by_cedula(parent_cedula)
        child = family.get_member_by_cedula(child_cedula)
        
        if not parent or not child:
            return False, "Una o más personas no existen en la familia"
        
        # Primero registrar al padre/madre con el hijo
        if RelacionService._es_masculino(parent.gender):
            exito, mensaje = RelacionService.registrar_padres(
                family, 
                child_cedula=child_cedula, 
                father_cedula=parent.cedula
            )
        else:
            exito, mensaje = RelacionService.registrar_padres(
                family, 
                child_cedula=child_cedula, 
                mother_cedula=parent.cedula
            )
        
        if not exito:
            return False, mensaje
        
        # Ahora verificar si el padre/madre tiene cónyuge
        if parent.spouse:
            # El cónyuge también se convierte en padre/madre
            spouse = parent.spouse
            if RelacionService._es_masculino(spouse.gender):
                exito_spouse, mensaje_spouse = RelacionService.registrar_padres(
                    family, 
                    child_cedula=child_cedula, 
                    father_cedula=spouse.cedula
                )
            else:
                exito_spouse, mensaje_spouse = RelacionService.registrar_padres(
                    family, 
                    child_cedula=child_cedula, 
                    mother_cedula=spouse.cedula
                )
            
            if exito_spouse:
                return True, f"{mensaje} y {mensaje_spouse}"
        
        return True, mensaje

    # Funciones de utilidad para consultas
    @staticmethod
    def obtener_nacimientos_ultimos_10_años(family: Family) -> int:
        """Obtiene cuántas personas nacieron en los últimos 10 años"""
        count = 0
        for person in family.members:
            if person.birth_date:
                birth_year = int(person.birth_date[:4])
                if family.current_year - birth_year <= 10:
                    count += 1
        return count

    @staticmethod
    def obtener_parejas_con_hijos(family: Family, min_hijos: int = 2) -> list:
        """Obtiene las parejas actuales con mínimo de hijos en común"""
        couples = []
        for person in family.members:
            if person.spouse and person.alive and person.spouse.alive:
                common_children = set(person.children) & set(person.spouse.children)
                if len(common_children) >= min_hijos:
                    couples.append((person, person.spouse))
        return couples

    @staticmethod
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

    @staticmethod
    def buscar_personas_por_nombre(family: Family, nombre: str) -> list:
        """Busca personas por nombre o apellido (búsqueda parcial, insensible a mayúsculas)"""
        nombre = nombre.lower()
        resultados = []
        for person in family.members:
            if (nombre in person.first_name.lower() or 
                nombre in person.last_name.lower()):
                resultados.append(person)
        return resultados

    @staticmethod
    def obtener_personas_sin_relacion(family: Family) -> list:
        """Obtiene personas sin relaciones familiares (sin padres, hijos, pareja o hermanos)"""
        sin_relacion = []
        for person in family.members:
            if (not person.mother and not person.father and 
                not person.children and not person.spouse and 
                not person.siblings):
                sin_relacion.append(person)
        return sin_relacion

    @staticmethod
    def obtener_estadisticas_familia(family: Family) -> dict:
        """Obtiene estadísticas generales de la familia"""
        total = len(family.members)
        vivos = len(family.get_living_members())
        fallecidos = len(family.get_deceased_members())
        promedio_edad = (sum(p.calculate_virtual_age() for p in family.get_living_members()) / vivos) if vivos > 0 else 0
        return {
            'total': total,
            'vivos': vivos,
            'fallecidos': fallecidos,
            'promedio_edad': round(promedio_edad, 2)
        }

    @staticmethod
    def obtener_personas_por_estado_civil(family: Family, estado_civil: str) -> list:
        """Obtiene personas por estado civil"""
        return [p for p in family.members if p.marital_status.lower() == estado_civil.lower()]

    @staticmethod
    def obtener_personas_por_provincia(family: Family, provincia: str) -> list:
        """Obtiene personas por provincia"""
        return [p for p in family.members if p.province.lower() == provincia.lower()] 

    @staticmethod
    def buscar_por_caracteristica(family: Family, caracteristica: str, valor) -> list:
        """Busca personas por una característica específica"""
        resultados = []
        for person in family.members:
            if hasattr(person, caracteristica):
                if str(getattr(person, caracteristica)).lower() == str(valor).lower():
                    resultados.append(person)
        return resultados

    @staticmethod
    def encontrar_familiares_por_tipo(persona_referencia: Person, family: Family, tipo_relacion: str) -> List[Person]:
        """
        Encuentra todos los familiares de un tipo específico para una persona de referencia.
        
        Args:
            persona_referencia: Persona de referencia
            family: Familia a la que pertenece
            tipo_relacion: Tipo de relación a buscar (ej: "primo", "tío", "hermano", etc.)
            
        Returns:
            List[Person]: Lista de personas que tienen esa relación
        """
        familiares = []
        tipo_relacion = tipo_relacion.lower()
        
        # Buscar en toda la familia
        for persona in family.members:
            if persona.cedula == persona_referencia.cedula:
                continue
                
            relacion = persona_referencia.get_relationship_to(persona, family).lower()
            
            # Verificar si la relación coincide con el tipo buscado
            if tipo_relacion in relacion or relacion.startswith(tipo_relacion):
                familiares.append(persona)
        
        return familiares

    @staticmethod
    def analizar_relacion_detallada(persona_a: Person, persona_b: Person, family: Family) -> dict:
        """
        Analiza en detalle la relación entre dos personas.
        
        Args:
            persona_a: Primera persona
            persona_b: Segunda persona
            family: Familia a la que pertenecen
            
        Returns:
            dict: Análisis detallado de la relación
        """
        relacion_a_b = persona_a.get_relationship_to(persona_b, family)
        relacion_b_a = persona_b.get_relationship_to(persona_a, family)
        
        # Determinar grado de consanguinidad
        grado = RelacionService._calcular_grado_consanguinidad(persona_a, persona_b)
        
        # Determinar línea familiar
        linea = RelacionService._determinar_linea_familiar(persona_a, persona_b)
        
        return {
            'persona_a': persona_a.get_full_name(),
            'persona_b': persona_b.get_full_name(),
            'relacion_a_hacia_b': relacion_a_b,
            'relacion_b_hacia_a': relacion_b_a,
            'grado_consanguinidad': grado,
            'linea_familiar': linea,
            'son_consanguineos': grado > 0,
            'distancia_generacional': RelacionService._calcular_distancia_generacional(persona_a, persona_b)
        }

    @staticmethod
    def _calcular_grado_consanguinidad(persona_a: Person, persona_b: Person) -> int:
        """
        Calcula el grado de consanguinidad entre dos personas.
        
        Returns:
            int: Grado de consanguinidad (0 = sin relación, 1 = primer grado, etc.)
        """
        # Primer grado: padres-hijos
        if (persona_a.father == persona_b or persona_a.mother == persona_b or
            persona_b.father == persona_a or persona_b.mother == persona_a):
            return 1
        
        # Segundo grado: hermanos, abuelos-nietos
        if persona_a._are_siblings(persona_b):
            return 2
        
        # Verificar abuelos-nietos
        if RelacionService._es_abuelo_nieto(persona_a, persona_b):
            return 2
        
        # Tercer grado: tíos-sobrinos
        if RelacionService._es_tio_sobrino(persona_a, persona_b):
            return 3
        
        # Cuarto grado: primos hermanos
        if RelacionService._son_primos_hermanos(persona_a, persona_b):
            return 4
        
        return 0  # Sin relación consanguínea directa

    @staticmethod
    def _determinar_linea_familiar(persona_a: Person, persona_b: Person) -> str:
        """Determina si la relación es por línea paterna, materna o mixta"""
        # Verificar línea paterna
        if RelacionService._tienen_ancestro_paterno_comun(persona_a, persona_b):
            return "Línea paterna"
        
        # Verificar línea materna
        if RelacionService._tienen_ancestro_materno_comun(persona_a, persona_b):
            return "Línea materna"
        
        # Verificar si hay relación mixta
        if RelacionService._tienen_relacion_mixta(persona_a, persona_b):
            return "Línea mixta"
        
        return "Sin línea familiar directa"

    @staticmethod
    def _calcular_distancia_generacional(persona_a: Person, persona_b: Person) -> int:
        """Calcula la distancia generacional entre dos personas"""
        # Asignar nivel generacional basado en ancestros
        nivel_a = RelacionService._calcular_nivel_generacional(persona_a)
        nivel_b = RelacionService._calcular_nivel_generacional(persona_b)
        
        return abs(nivel_a - nivel_b)

    @staticmethod
    def _calcular_nivel_generacional(persona: Person) -> int:
        """Calcula el nivel generacional de una persona (0 = raíz)"""
        nivel = 0
        actual = persona
        
        # Contar generaciones hacia arriba
        while actual.father or actual.mother:
            nivel += 1
            # Preferir padre, luego madre
            actual = actual.father if actual.father else actual.mother
            
            # Evitar bucles infinitos
            if nivel > 10:
                break
        
        return nivel

    @staticmethod
    def _es_abuelo_nieto(persona_a: Person, persona_b: Person) -> bool:
        """Verifica si hay relación abuelo-nieto"""
        # A es abuelo de B
        for hijo in persona_a.children:
            if persona_b in hijo.children:
                return True
        
        # B es abuelo de A
        for hijo in persona_b.children:
            if persona_a in hijo.children:
                return True
        
        return False

    @staticmethod
    def _es_tio_sobrino(persona_a: Person, persona_b: Person) -> bool:
        """Verifica si hay relación tío-sobrino"""
        # A es tío de B (A es hermano de un padre de B)
        if persona_b.father and persona_a._are_siblings(persona_b.father):
            return True
        if persona_b.mother and persona_a._are_siblings(persona_b.mother):
            return True
        
        # B es tío de A
        if persona_a.father and persona_b._are_siblings(persona_a.father):
            return True
        if persona_a.mother and persona_b._are_siblings(persona_a.mother):
            return True
        
        return False

    @staticmethod
    def _son_primos_hermanos(persona_a: Person, persona_b: Person) -> bool:
        """
        Verifica si son primos hermanos usando la lógica de deducción:
        Los primos son hijos de hermanos de los padres
        """
        # Verificar si los padres de A son hermanos de los padres de B
        
        # Caso 1: Padre de A es hermano del padre de B
        if (persona_a.father and persona_b.father and 
            persona_a.father._are_siblings(persona_b.father)):
            return True
        
        # Caso 2: Padre de A es hermano de la madre de B
        if (persona_a.father and persona_b.mother and 
            persona_a.father._are_siblings(persona_b.mother)):
            return True
        
        # Caso 3: Madre de A es hermana del padre de B
        if (persona_a.mother and persona_b.father and 
            persona_a.mother._are_siblings(persona_b.father)):
            return True
        
        # Caso 4: Madre de A es hermana de la madre de B
        if (persona_a.mother and persona_b.mother and 
            persona_a.mother._are_siblings(persona_b.mother)):
            return True
        
        return False

    @staticmethod
    def _tienen_ancestro_paterno_comun(persona_a: Person, persona_b: Person) -> bool:
        """Verifica si comparten un ancestro por línea paterna"""
        ancestros_a = RelacionService._obtener_ancestros_paternos(persona_a)
        ancestros_b = RelacionService._obtener_ancestros_paternos(persona_b)
        
        return bool(ancestros_a.intersection(ancestros_b))

    @staticmethod
    def _tienen_ancestro_materno_comun(persona_a: Person, persona_b: Person) -> bool:
        """Verifica si comparten un ancestro por línea materna"""
        ancestros_a = RelacionService._obtener_ancestros_maternos(persona_a)
        ancestros_b = RelacionService._obtener_ancestros_maternos(persona_b)
        
        return bool(ancestros_a.intersection(ancestros_b))

    @staticmethod
    def _tienen_relacion_mixta(persona_a: Person, persona_b: Person) -> bool:
        """Verifica si tienen relación por ambas líneas"""
        return (RelacionService._tienen_ancestro_paterno_comun(persona_a, persona_b) and
                RelacionService._tienen_ancestro_materno_comun(persona_a, persona_b))

    @staticmethod
    def _obtener_ancestros_paternos(persona: Person, max_generaciones: int = 5) -> Set[str]:
        """Obtiene todos los ancestros por línea paterna"""
        ancestros = set()
        actual = persona.father
        generacion = 0
        
        while actual and generacion < max_generaciones:
            ancestros.add(actual.cedula)
            actual = actual.father
            generacion += 1
        
        return ancestros

    @staticmethod
    def _obtener_ancestros_maternos(persona: Person, max_generaciones: int = 5) -> Set[str]:
        """Obtiene todos los ancestros por línea materna"""
        ancestros = set()
        actual = persona.mother
        generacion = 0
        
        while actual and generacion < max_generaciones:
            ancestros.add(actual.cedula)
            actual = actual.mother
            generacion += 1
        
        return ancestros

    @staticmethod
    def generar_reporte_relaciones(persona_referencia: Person, family: Family) -> dict:
        """
        Genera un reporte completo de todas las relaciones de una persona.
        
        Args:
            persona_referencia: Persona de referencia
            family: Familia a la que pertenece
            
        Returns:
            dict: Reporte completo de relaciones organizadas por tipo
        """
        reporte = {
            'persona_referencia': persona_referencia.get_full_name(),
            'primer_grado': {
                'padres': [],
                'hijos': []
            },
            'segundo_grado': {
                'abuelos': [],
                'nietos': [],
                'hermanos': []
            },
            'tercer_grado': {
                'bisabuelos': [],
                'bisnietos': [],
                'tios': [],
                'sobrinos': []
            },
            'cuarto_grado': {
                'primos': [],
                'tios_abuelos': []
            },
            'afinidad': {
                'conyuge': [],
                'suegros': [],
                'yernos_nueras': [],
                'cunados': []
            }
        }
        
        # Clasificar a todas las personas de la familia
        for persona in family.members:
            if persona.cedula == persona_referencia.cedula:
                continue
                
            relacion = persona_referencia.get_relationship_to(persona, family).lower()
            
            # Clasificar por grado
            if any(word in relacion for word in ['padre', 'madre', 'hijo', 'hija']):
                if 'padre' in relacion or 'madre' in relacion:
                    reporte['primer_grado']['padres'].append({
                        'nombre': persona.get_full_name(),
                        'relacion': relacion,
                        'cedula': persona.cedula
                    })
                else:
                    reporte['primer_grado']['hijos'].append({
                        'nombre': persona.get_full_name(),
                        'relacion': relacion,
                        'cedula': persona.cedula
                    })
            
            elif any(word in relacion for word in ['abuelo', 'abuela', 'nieto', 'nieta', 'hermano', 'hermana']):
                if 'abuelo' in relacion or 'abuela' in relacion:
                    reporte['segundo_grado']['abuelos'].append({
                        'nombre': persona.get_full_name(),
                        'relacion': relacion,
                        'cedula': persona.cedula
                    })
                elif 'nieto' in relacion or 'nieta' in relacion:
                    reporte['segundo_grado']['nietos'].append({
                        'nombre': persona.get_full_name(),
                        'relacion': relacion,
                        'cedula': persona.cedula
                    })
                else:
                    reporte['segundo_grado']['hermanos'].append({
                        'nombre': persona.get_full_name(),
                        'relacion': relacion,
                        'cedula': persona.cedula
                    })
            
            elif any(word in relacion for word in ['tío', 'tía', 'sobrino', 'sobrina', 'bisabuelo', 'bisabuela']):
                if 'bisabuelo' in relacion or 'bisabuela' in relacion:
                    reporte['tercer_grado']['bisabuelos'].append({
                        'nombre': persona.get_full_name(),
                        'relacion': relacion,
                        'cedula': persona.cedula
                    })
                elif 'tío' in relacion or 'tía' in relacion:
                    reporte['tercer_grado']['tios'].append({
                        'nombre': persona.get_full_name(),
                        'relacion': relacion,
                        'cedula': persona.cedula
                    })
                else:
                    reporte['tercer_grado']['sobrinos'].append({
                        'nombre': persona.get_full_name(),
                        'relacion': relacion,
                        'cedula': persona.cedula
                    })
            
            elif any(word in relacion for word in ['primo', 'prima']):
                reporte['cuarto_grado']['primos'].append({
                    'nombre': persona.get_full_name(),
                    'relacion': relacion,
                    'cedula': persona.cedula
                })
            
            elif any(word in relacion for word in ['cónyuge', 'suegro', 'suegra', 'yerno', 'nuera', 'cuñado', 'cuñada']):
                if 'cónyuge' in relacion:
                    reporte['afinidad']['conyuge'].append({
                        'nombre': persona.get_full_name(),
                        'relacion': relacion,
                        'cedula': persona.cedula
                    })
                elif 'suegro' in relacion or 'suegra' in relacion:
                    reporte['afinidad']['suegros'].append({
                        'nombre': persona.get_full_name(),
                        'relacion': relacion,
                        'cedula': persona.cedula
                    })
                elif 'yerno' in relacion or 'nuera' in relacion:
                    reporte['afinidad']['yernos_nueras'].append({
                        'nombre': persona.get_full_name(),
                        'relacion': relacion,
                        'cedula': persona.cedula
                    })
                else:
                    reporte['afinidad']['cunados'].append({
                        'nombre': persona.get_full_name(),
                        'relacion': relacion,
                        'cedula': persona.cedula
                    })
        
        return reporte

    @staticmethod
    def buscar_familiares_por_tipo(family: Family, persona_cedula: str, tipo_relacion: str) -> list:
        """
        Busca todos los familiares de un tipo específico usando la lógica mejorada de relaciones
        
        Args:
            family (Family): La familia
            persona_cedula (str): Cédula de la persona de referencia
            tipo_relacion (str): Tipo de relación a buscar (ej: "primo", "tío", "sobrino")
            
        Returns:
            list: Lista de personas que tienen esa relación con la persona de referencia
        """
        persona_ref = None
        for p in family.members:
            if p.cedula == persona_cedula:
                persona_ref = p
                break
        
        if not persona_ref:
            return []
        
        familiares = []
        tipo_lower = tipo_relacion.lower()
        
        for otra_persona in family.members:
            if otra_persona != persona_ref:
                relacion = persona_ref.get_relationship_to(otra_persona, family)
                relacion_lower = relacion.lower()
                
                # Buscar coincidencias flexibles
                if (tipo_lower in relacion_lower or 
                    (tipo_lower == "primo" and "primo" in relacion_lower) or
                    (tipo_lower == "tío" and "tío" in relacion_lower) or
                    (tipo_lower == "sobrino" and "sobrino" in relacion_lower) or
                    (tipo_lower == "hermano" and "hermano" in relacion_lower)):
                    familiares.append({
                        'persona': otra_persona,
                        'relacion': relacion,
                        'nombre': otra_persona.get_full_name(),
                        'cedula': otra_persona.cedula
                    })
        
        return familiares

    @staticmethod
    def obtener_relacion_detallada(family: Family, cedula_1: str, cedula_2: str) -> dict:
        """
        Obtiene información detallada sobre la relación entre dos personas
        
        Args:
            family (Family): La familia
            cedula_1 (str): Cédula de la primera persona
            cedula_2 (str): Cédula de la segunda persona
            
        Returns:
            dict: Información detallada sobre la relación
        """
        persona_1 = None
        persona_2 = None
        
        for p in family.members:
            if p.cedula == cedula_1:
                persona_1 = p
            elif p.cedula == cedula_2:
                persona_2 = p
        
        if not persona_1 or not persona_2:
            return {
                'error': 'Una o ambas personas no fueron encontradas',
                'relacion': 'Desconocida'
            }
        
        relacion_1_a_2 = persona_1.get_relationship_to(persona_2, family)
        relacion_2_a_1 = persona_2.get_relationship_to(persona_1, family)
        
        return {
            'persona_1': {
                'nombre': persona_1.get_full_name(),
                'cedula': persona_1.cedula
            },
            'persona_2': {
                'nombre': persona_2.get_full_name(),
                'cedula': persona_2.cedula
            },
            'relacion_1_a_2': relacion_1_a_2,
            'relacion_2_a_1': relacion_2_a_1,
            'es_reciproca': RelacionService._es_relacion_reciproca(relacion_1_a_2, relacion_2_a_1),
            'grado_consanguinidad': RelacionService._calcular_grado_consanguinidad(relacion_1_a_2)
        }

    @staticmethod
    def _es_relacion_reciproca(relacion_1: str, relacion_2: str) -> bool:
        """Verifica si una relación es recíproca entre dos personas"""
        relaciones_reciprocas = {
            'hermano': 'hermano',
            'hermana': 'hermana',
            'primo': 'primo',
            'prima': 'prima',
            'cónyuge': 'cónyuge',
            'padre': 'hijo',
            'madre': 'hija',
            'hijo': 'padre',
            'hija': 'madre',
            'abuelo': 'nieto',
            'abuela': 'nieta',
            'nieto': 'abuelo',
            'nieta': 'abuela',
            'tío': 'sobrino',
            'tía': 'sobrina',
            'sobrino': 'tío',
            'sobrina': 'tía'
        }
        
        for key, value in relaciones_reciprocas.items():
            if key in relacion_1.lower() and value in relacion_2.lower():
                return True
            if value in relacion_1.lower() and key in relacion_2.lower():
                return True
        
        return False

    @staticmethod
    def _calcular_grado_consanguinidad(relacion: str) -> int:
        """Calcula el grado de consanguinidad basado en la relación"""
        relacion_lower = relacion.lower()
        
        if 'yo mismo' in relacion_lower:
            return 0
        elif any(word in relacion_lower for word in ['padre', 'madre', 'hijo', 'hija']):
            return 1
        elif any(word in relacion_lower for word in ['hermano', 'hermana', 'abuelo', 'abuela', 'nieto', 'nieta']):
            return 2
        elif any(word in relacion_lower for word in ['tío', 'tía', 'sobrino', 'sobrina', 'bisabuelo', 'bisnieto']):
            return 3
        elif any(word in relacion_lower for word in ['primo', 'prima']):
            if 'segundo' in relacion_lower:
                return 5
            else:
                return 4
        else:
            return -1  # Relación por afinidad o no determinada