# test_simulacion.py
import sys
import os
import time
import logging
from datetime import datetime
from typing import List

# Añadir el directorio raíz al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.family import Family
from models.person import Person
from services.simulacion_service import SimulacionService
from models.simulation_config import SimulationConfig
from services.persona_service import PersonaService
from services.relacion_service import RelacionService
from utils.gedcom_parser import GedcomParser

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def crear_arbol_familiar_prueba() -> Family:
    """Crea un árbol familiar de prueba CON EL ORDEN CORRECTO"""
    family = Family(1, "Familia de Prueba")
    family.current_year = 2023
    
    # Crear personas
    abuelo1 = Person(
        cedula="100000001",
        first_name="José",
        last_name="García",
        birth_date="1950-01-01",
        gender="Masculino",
        province="San José"
    )
    abuela1 = Person(
        cedula="200000001",
        first_name="María",
        last_name="López",
        birth_date="1952-05-15",
        gender="Femenino",
        province="San José"
    )
    padre = Person(
        cedula="300000001",
        first_name="Carlos",
        last_name="García",
        birth_date="1980-03-20",
        gender="Masculino",
        province="San José"
    )
    madre = Person(
        cedula="400000001",
        first_name="Ana",
        last_name="Martínez",
        birth_date="1982-07-10",
        gender="Femenino",
        province="San José"
    )
    hijo1 = Person(
        cedula="500000001",
        first_name="Juan",
        last_name="García",
        birth_date="2005-04-15",
        gender="Masculino",
        province="San José"
    )
    hijo2 = Person(
        cedula="600000001",
        first_name="Lucía",
        last_name="García",
        birth_date="2008-08-20",
        gender="Femenino",
        province="San José"
    )
    
    # ✅ PRIMERO: Agregar todas las personas a la familia
    for person in [abuelo1, abuela1, padre, madre, hijo1, hijo2]:
        family.add_or_update_member(person)
    
    # ✅ SEGUNDO: Registrar relaciones
    # Registrar pareja (abuelos)
    RelacionService.registrar_pareja(family, "100000001", "200000001")
    
    # Registrar pareja (padres)
    RelacionService.registrar_pareja(family, "300000001", "400000001")
    
    # Registrar padres de los padres (abuelos)
    RelacionService.registrar_padres(family, "300000001", "200000001", "100000001")
    
    # Registrar hijos
    RelacionService.registrar_padres(family, "500000001", "400000001", "300000001")
    RelacionService.registrar_padres(family, "600000001", "400000001", "300000001")
    
    logger.info("Árbol familiar de prueba creado con éxito")

    if not family.verificar_integridad():
        logger.error("ERROR: El árbol familiar tiene problemas de integridad")
    return family

def verificar_relaciones(family: Family):
    """Verifica que las relaciones se hayan establecido correctamente"""
    # Verificar pareja de abuelos
    abuelo = family.get_member_by_cedula("100000001")
    abuela = family.get_member_by_cedula("200000001")
    if abuelo and abuela:
        if not abuelo.spouse or abuelo.spouse.cedula != abuela.cedula:
            logger.error("ERROR: La relación de pareja de abuelos no se estableció correctamente (abuelo)")
        if not abuela.spouse or abuela.spouse.cedula != abuelo.cedula:
            logger.error("ERROR: La relación de pareja de abuelos no se estableció correctamente (abuela)")
    
    # Verificar pareja de padres
    padre = family.get_member_by_cedula("300000001")
    madre = family.get_member_by_cedula("400000001")
    if padre and madre:
        if not padre.spouse or padre.spouse.cedula != madre.cedula:
            logger.error("ERROR: La relación de pareja de padres no se estableció correctamente (padre)")
        if not madre.spouse or madre.spouse.cedula != padre.cedula:
            logger.error("ERROR: La relación de pareja de padres no se estableció correctamente (madre)")
        
        # Verificar que los padres estén registrados correctamente para los hijos
        hijo1 = family.get_member_by_cedula("500000001")
        if hijo1:
            if hijo1.father != padre or hijo1.mother != madre:
                logger.error("ERROR: Los padres no están correctamente registrados para Juan")
        
        hijo2 = family.get_member_by_cedula("600000001")
        if hijo2:
            if hijo2.father != padre or hijo2.mother != madre:
                logger.error("ERROR: Los padres no están correctamente registrados para Lucía")
    
    # Verificar que los abuelos estén registrados para los padres
    if padre and abuelo and abuela:
        if padre.father != abuelo or padre.mother != abuela:
            logger.error("ERROR: Los abuelos no están correctamente registrados para Carlos")

def mostrar_estado_actual(family: Family, year: int):
    """Muestra el estado actual del árbol familiar"""
    print(f"\n{'='*50}")
    print(f"AÑO {year} - Estado Actual")
    print(f"{'='*50}")
    
    for person in family.members:
        status = "VIVO" if person.alive else "FALLECIDO"
        age = person.calculate_age() if person.alive else f"{person.calculate_age()} (al fallecer)"
        
        print(f"\n{person.first_name} {person.last_name} [{status}]")
        print(f"Edad: {age} años")
        print(f"Género: {person.gender}")
        print(f"Salud emocional: {person.emotional_health}")
        print(f"Estado civil: {person.marital_status}")
        
        if person.father:
            print(f"Padre: {person.father.first_name} {person.father.last_name}")
        if person.mother:
            print(f"Madre: {person.mother.first_name} {person.mother.last_name}")
        if person.spouse:
            print(f"Pareja: {person.spouse.first_name} {person.spouse.last_name}")
        if person.children:
            children = ", ".join([f"{c.first_name}" for c in person.children])
            print(f"Hijos: {children}")
    
    print(f"\nTotal de miembros: {len(family.members)}")
    print(f"Personas vivas: {len([p for p in family.members if p.alive])}")
    print(f"Personas fallecidas: {len([p for p in family.members if not p.alive])}")

def test_simulacion_completa():
    """Prueba la simulación con un árbol familiar de ejemplo"""
    print("="*70)
    print("INICIANDO PRUEBA DE SIMULACIÓN FAMILIAR")
    print("="*70)
    
    # Crear árbol familiar de prueba
    family = crear_arbol_familiar_prueba()
    
    # Configuración de simulación
    config = SimulationConfig()
    config.real_time_per_year = 0.5  # 0.5 segundos reales por año de simulación
    config.events_interval = 1  # 1 año entre eventos
    config.birth_probability = 0.4  # 40% de probabilidad de nacimiento (aumentado)
    config.death_probability_base = 0.002  # Probabilidad base de fallecimiento (aumentado)
    config.find_partner_probability = 0.1  # 10% de probabilidad de encontrar pareja
    
    # Mostrar estado inicial
    mostrar_estado_actual(family, family.current_year)
    
    print("\nIniciando simulación...")
    print(f"Velocidad: {1.0/config.real_time_per_year:.1f}x (1 año de simulación = {config.real_time_per_year} segundos reales)")
    print(f"Probabilidad de nacimiento: {config.birth_probability*100:.0f}%")
    print(f"Probabilidad base de fallecimiento: {config.death_probability_base*100:.2f}%")
    print(f"Probabilidad de encontrar pareja: {config.find_partner_probability*100:.0f}%")
    
    # Simular 40 años
    total_years = 40
    for i in range(total_years):
        year = family.current_year + 1
        
        print(f"\n{'-'*50}")
        print(f"PROCESANDO AÑO {year}")
        print(f"{'-'*50}")
        
        # Ejecutar ciclo de simulación
        eventos = SimulacionService.ejecutar_ciclo_simulacion(family, config)
        
        # Mostrar eventos
        if eventos and len(eventos) > 1:  # El primer evento es siempre el año de simulación
            print("\nEVENTOS DEL AÑO:")
            for evento in eventos[1:]:  # Saltar el primer evento (año de simulación)
                print(f"- {evento}")
        else:
            print("\nNo hubo eventos significativos este año.")
        
        # Mostrar estado actual
        mostrar_estado_actual(family, year)
        
        # Pausa para ver los resultados
        if i < total_years - 1:  # No pausar después del último año
            print(f"\nEsperando {config.real_time_per_year:.1f} segundos antes del próximo año...")
            time.sleep(config.real_time_per_year)
    
    print("\n" + "="*70)
    print("SIMULACIÓN COMPLETADA")
    print("="*70)
    
    # Exportar a GEDCOM para verificar
    from services.persona_service import exportar_a_gedcom
    gedcom_content = exportar_a_gedcom(family)
    
    with open('simulacion_result.ged', 'w', encoding='utf-8') as f:
        f.write(gedcom_content)
    
    print("\nResultado de la simulación exportado a 'simulacion_result.ged'")
    print(f"Total de personas al final: {len(family.members)}")
    print(f"Personas vivas: {len([p for p in family.members if p.alive])}")
    print(f"Personas fallecidas: {len([p for p in family.members if not p.alive])}")
    
    # Verificaciones finales
    verificar_resultados(family, total_years)

def verificar_resultados(family: Family, years: int):
    """Verifica que la simulación haya producido resultados realistas"""
    logger.info("Verificando resultados de la simulación...")
    
    # Calcular año final de simulación
    end_year = 2023 + years
    
    # Verificar que haya nuevos nacimientos
    initial_children = 2  # Juan y Lucía
    current_children = sum(1 for p in family.members 
                          if p.birth_date > "2023-01-01" and 
                          p.birth_date <= f"{end_year}-12-31")
    
    if current_children < 1:  # Esperamos al menos 1 nuevo nacimiento
        logger.error(f"ERROR: Deberían haber nuevos nacimientos (actual: {current_children}, esperado: al menos 1)")
    else:
        logger.info(f"✓ Nacimientos: {current_children} nuevos hijos")
    
    # Verificar fallecimientos
    initial_deceased = 0  # Nadie fallecido inicialmente
    current_deceased = len(family.get_deceased_members())
    # Los abuelos deberían haber fallecido
    expected_deceased = min(2, max(1, int(years * 0.05 * 2)))  # Entre 1-2 fallecimientos
    if current_deceased < expected_deceased:
        logger.error(f"ERROR: Deberían haber más fallecimientos (actual: {current_deceased}, esperado: {expected_deceased})")
    else:
        logger.info(f"✓ Fallecimientos: {current_deceased} personas fallecidas")
    
    # ✅ CORRECCIÓN: Verificar nuevas parejas de manera más robusta
    # Contar parejas que se formaron durante la simulación
    nuevas_parejas = 0
    juan = family.get_member_by_cedula("500000001")
    lucia = family.get_member_by_cedula("600000001")
    
    # Verificar si Juan y Lucía formaron pareja durante la simulación
    if juan and lucia and juan.spouse == lucia and lucia.spouse == juan:
        nuevas_parejas += 1
    
    # Verificar si hay otras nuevas parejas
    for person in family.members:
        if (person.alive and 
            person.has_partner() and 
            person.calculate_age() >= 18 and
            person.marital_status == "Casado/a"):
            
            # Verificar si la pareja se formó durante la simulación
            if person.birth_date <= "2023-12-31" and person.spouse.birth_date <= "2023-12-31":
                nuevas_parejas += 1
    
    if nuevas_parejas < 1:
        logger.error(f"ERROR: Deberían haber nuevas parejas (actual: {nuevas_parejas}, esperado: al menos 1)")
    else:
        logger.info(f"✓ Nuevas parejas: {nuevas_parejas} nuevas parejas formadas")
    
    # ✅ CORRECCIÓN: Verificar que Carlos y Ana estén registrados como pareja
    carlos = family.get_member_by_cedula("300000001")
    ana = family.get_member_by_cedula("400000001")
    if carlos and ana and carlos.has_partner() and ana.has_partner() and carlos.spouse == ana and ana.spouse == carlos:
        logger.info("✓ Carlos y Ana están correctamente registrados como pareja")
    else:
        logger.error("ERROR: Carlos y Ana no están registrados como pareja")
    
    # ✅ CORRECCIÓN: Verificar nuevos nacimientos
    if current_children >= 1:
        logger.info(f"✓ Nacimientos: {current_children} nuevos hijos")
    else:
        logger.error(f"ERROR: Deberían haber nuevos nacimientos (actual: {current_children}, esperado: al menos 1)")
    
    # ✅ CORRECCIÓN: Verificar el estado civil de las personas
    for person in family.members:
        if person.has_partner() and "Casado" not in person.marital_status:
            logger.error(f"ERROR: {person.first_name} tiene pareja pero estado civil es '{person.marital_status}'")
        elif not person.has_partner() and "Casado" in person.marital_status:
            logger.error(f"ERROR: {person.first_name} no tiene pareja pero estado civil es '{person.marital_status}'")
    
    # ✅ CORRECCIÓN: Verificar que los nacimientos se hayan registrado correctamente
    for person in family.members:
        if person.birth_date > "2023-12-31":
            if person.father or person.mother:
                logger.info(f"✓ Nacimiento registrado: {person.first_name} ({person.birth_date})")
            else:
                logger.error(f"ERROR: {person.first_name} nació pero no tiene padres registrados")
    
    if all([
        current_children >= 1,
        current_deceased >= expected_deceased,
        nuevas_parejas >= 1,
        (carlos and ana and carlos.has_partner() and ana.has_partner() and carlos.spouse == ana and ana.spouse == carlos)
    ]):
        logger.info("✓ Todas las verificaciones de simulación pasaron correctamente")
    else:
        logger.error("✗ Algunas verificaciones de simulación fallaron")

def test_gedcom_parser():
    """Prueba el parser GEDCOM con un árbol familiar de prueba"""
    print("\n" + "="*70)
    print("PRUEBA DEL PARSER GEDCOM")
    print("="*70)
    
    # Crear un árbol familiar de prueba
    family = crear_arbol_familiar_prueba()
    
    # Exportar a GEDCOM
    from services.persona_service import exportar_a_gedcom
    gedcom_content = exportar_a_gedcom(family)
    
    # Guardar para referencia
    with open('prueba.ged', 'w', encoding='utf-8') as f:
        f.write(gedcom_content)
    
    print("Árbol familiar de prueba exportado a 'prueba.ged'")
    
    # Crear una nueva familia para importar
    new_family = Family(2, "Familia Importada")
    
    # Parsear el GEDCOM
    try:
        GedcomParser.parse(new_family, gedcom_content)
        print("\nÁrbol familiar importado con éxito")
        print(f"Total de miembros importados: {len(new_family.members)}")
        
        # Verificar relaciones importadas
        verificar_relaciones_importadas(new_family)
        
        # Mostrar algunos detalles
        for person in new_family.members[:3]:  # Mostrar solo los primeros 3
            print(f"\n{person.first_name} {person.last_name}:")
            print(f"  Cédula: {person.cedula}")
            print(f"  Edad: {person.calculate_age()}")
            print(f"  Estado civil: {person.marital_status}")
            if person.spouse:
                print(f"  Pareja: {person.spouse.first_name} {person.spouse.last_name}")
            if person.children:
                print(f"  Hijos: {len(person.children)}")
    except Exception as e:
        logger.error(f"Error al importar GEDCOM: {str(e)}")

def verificar_relaciones_importadas(family: Family):
    """Verifica que las relaciones se hayan importado correctamente"""
    # Verificar pareja de abuelos
    abuelo = family.get_member_by_cedula("100000001")
    abuela = family.get_member_by_cedula("200000001")
    if abuelo and abuela:
        if not abuelo.spouse or abuelo.spouse.cedula != abuela.cedula:
            logger.error("ERROR: La relación de pareja de abuelos no se importó correctamente (abuelo)")
        if not abuela.spouse or abuela.spouse.cedula != abuelo.cedula:
            logger.error("ERROR: La relación de pareja de abuelos no se importó correctamente (abuela)")
    
    # Verificar pareja de padres
    padre = family.get_member_by_cedula("300000001")
    madre = family.get_member_by_cedula("400000001")
    if padre and madre:
        if not padre.spouse or padre.spouse.cedula != madre.cedula:
            logger.error("ERROR: La relación de pareja de padres no se importó correctamente (padre)")
        if not madre.spouse or madre.spouse.cedula != padre.cedula:
            logger.error("ERROR: La relación de pareja de padres no se importó correctamente (madre)")
        
        # Verificar que los padres estén registrados correctamente para los hijos
        hijo1 = family.get_member_by_cedula("500000001")
        if hijo1:
            if hijo1.father != padre or hijo1.mother != madre:
                logger.error("ERROR: Los padres no están correctamente registrados para Juan después de la importación")
        
        hijo2 = family.get_member_by_cedula("600000001")
        if hijo2:
            if hijo2.father != padre or hijo2.mother != madre:
                logger.error("ERROR: Los padres no están correctamente registrados para Lucía después de la importación")

if __name__ == "__main__":
    # Ejecutar prueba de simulación
    test_simulacion_completa()
    
    # Ejecutar prueba del parser GEDCOM
    test_gedcom_parser()
    
    print("\n" + "="*70)
    print("TODAS LAS PRUEBAS COMPLETADAS")
    print("="*70)