#!/usr/bin/env python3
"""
Script de prueba para verificar que los elementos de UI están visibles
"""
import customtkinter as ctk
import tkinter as tk
from models.family import Family
from gui.consultas_panel import ConsultasPanel

# Configurar CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Crear ventana de prueba
root = ctk.CTk()
root.title("Prueba UI - Panel de Consultas")
root.geometry("1400x900")

# Crear familia de prueba con algunas personas
family = Family("Familia de Prueba")

# Simular algunas personas para prueba
class PersonaPrueba:
    def __init__(self, nombre, apellido, cedula):
        self.first_name = nombre
        self.last_name = apellido
        self.cedula = cedula
        self.alive = True
    
    def calculate_age(self):
        return 30

# Agregar personas de prueba
family.members = [
    PersonaPrueba("Juan", "Pérez", "001"),
    PersonaPrueba("María", "González", "002"),
    PersonaPrueba("Carlos", "Rodríguez", "003")
]

# Crear panel de consultas
consultas_panel = ConsultasPanel(root, family)

print("✅ Panel de consultas creado")
print(f"📊 Personas cargadas: {len(family.members)}")
print("🎯 Si puedes ver los comboboxes y el botón, la UI está funcionando correctamente")

root.mainloop()
