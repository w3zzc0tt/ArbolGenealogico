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
                año_nacimiento = persona.birth_date.year
                if año_nacimiento >= año_limite:
                    contador += 1
        
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
                edad_muerte = persona.death_date.year - persona.birth_date.year
                
                # Ajustar si no había cumplido años en la fecha de muerte
                if (persona.death_date.month < persona.birth_date.month or 
                    (persona.death_date.month == persona.birth_date.month and 
                     persona.death_date.day < persona.birth_date.day)):
                    edad_muerte -= 1
                
                if edad_muerte < 50:
                    contador += 1
        
        return contador
