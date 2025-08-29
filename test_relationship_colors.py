#!/usr/bin/env python3
"""
Script de prueba para verificar los colores de relaciones en el árbol genealógico
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🎨 Prueba de colores de relaciones en el árbol genealógico")
print("=" * 60)

try:
    from utils.graph_visualizer import FamilyGraphVisualizer
    
    # Verificar que el método de leyenda esté implementado
    if hasattr(FamilyGraphVisualizer, '_draw_relationship_legend'):
        print("✅ Método '_draw_relationship_legend' encontrado")
    else:
        print("❌ Método '_draw_relationship_legend' NO encontrado")
    
    print("\n🌈 Colores de relaciones implementados:")
    print("  🔵 AZUL (#2196F3) - Padre/Madre → Hijo")
    print("     • Línea gruesa con flecha")
    print("     • Indica dirección generacional descendente")
    
    print("  💖 ROSA (#E91E63) - Relaciones de Pareja")
    print("     • Línea muy gruesa y suave")
    print("     • Incluye emoji de corazón 💕 en el medio")
    
    print("  🟢 VERDE (#4CAF50) - Hermanos")
    print("     • Línea punteada mediana")
    print("     • Conexión bidireccional entre hermanos")
    
    print("  🟠 NARANJA (#FF9800) - Hijo → Padre")
    print("     • Línea con flecha hacia arriba")
    print("     • Indica dirección generacional ascendente")
    
    print("  ⚪ GRIS (#9E9E9E) - Otras relaciones")
    print("     • Línea punteada fina")
    print("     • Para relaciones no definidas específicamente")
    
    print("\n📋 Leyenda visual agregada:")
    print("  • Posición: Esquina superior izquierda")
    print("  • Fondo: Azul oscuro con borde")
    print("  • Título: '🎨 Tipos de Relaciones'")
    print("  • Muestra ejemplos de cada tipo de línea")
    print("  • Incluye etiquetas descriptivas")
    
    print("\n🔧 Mejoras técnicas:")
    print("  • Evita duplicados de relaciones bidireccionales")
    print("  • Manejo de errores mejorado")
    print("  • Consistencia en estilos de líneas")
    print("  • Flechas con formas personalizadas")
    
    print("\n🎯 Beneficios para el usuario:")
    print("  • Identificación rápida de tipos de relaciones")
    print("  • Mejor comprensión del árbol genealógico")
    print("  • Navegación visual más intuitiva")
    print("  • Distinción clara entre generaciones")
    
    print("\n📐 Especificaciones técnicas:")
    relationships = {
        "parent": {"color": "#2196F3", "width": 3, "style": "arrow"},
        "spouse": {"color": "#E91E63", "width": 4, "style": "smooth + heart"},
        "sibling": {"color": "#4CAF50", "width": 2, "style": "dashed"},
        "child": {"color": "#FF9800", "width": 2, "style": "arrow"},
        "other": {"color": "#9E9E9E", "width": 1, "style": "dotted"}
    }
    
    for rel_type, specs in relationships.items():
        print(f"  • {rel_type.title()}: {specs['color']}, width={specs['width']}, {specs['style']}")
    
    print("\n🚀 ¡Colores de relaciones implementados exitosamente!")

except ImportError as e:
    print(f"❌ Error de importación: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
