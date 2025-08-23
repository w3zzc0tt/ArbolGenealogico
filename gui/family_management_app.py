import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import datetime
import sys
import os

# Add the parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from utils.validators import (
        validar_cedula, validar_fecha, validar_fechas_coherentes,
        validar_nombre, validar_persona_completa, validar_genero,
        validar_provincia, validar_estado_civil
    )
    HAS_VALIDATORS = True
except ImportError:
    HAS_VALIDATORS = False
    print("Advertencia: No se pudieron importar las utilidades de validación")

class PersonForm(ctk.CTkToplevel):
    def __init__(self, parent, title="Agregar Persona", on_save=None, data=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("500x650")
        self.resizable(False, False)
        self.on_save = on_save
        self.data = data or {}

        # Centrar ventana
        self.transient(parent)
        self.grab_set()

        self.setup_ui()

    def setup_ui(self):
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ctk.CTkLabel(form_frame, text="📋 Registrar Persona", font=("Arial", 18, "bold")).pack(pady=15)

        form = ctk.CTkFrame(form_frame)
        form.pack(fill=tk.X, padx=10, pady=10)
        form.columnconfigure(1, weight=1)

        # Cédula
        ctk.CTkLabel(form, text="Cédula:", font=("Arial", 12)).grid(row=0, column=0, sticky="w", padx=10, pady=8)
        self.cedula_entry = ctk.CTkEntry(form, placeholder_text="9-12 dígitos, solo números", width=220)
        self.cedula_entry.grid(row=0, column=1, padx=10, pady=8, sticky="ew")
        self.cedula_entry.insert(0, self.data.get("cedula", ""))

        # Nombre
        ctk.CTkLabel(form, text="Nombre:", font=("Arial", 12)).grid(row=1, column=0, sticky="w", padx=10, pady=8)
        self.first_name_entry = ctk.CTkEntry(form, placeholder_text="Ej: María", width=220)
        self.first_name_entry.grid(row=1, column=1, padx=10, pady=8, sticky="ew")
        self.first_name_entry.insert(0, self.data.get("first_name", ""))

        # Apellidos
        ctk.CTkLabel(form, text="Apellidos:", font=("Arial", 12)).grid(row=2, column=0, sticky="w", padx=10, pady=8)
        self.last_name_entry = ctk.CTkEntry(form, placeholder_text="Ej: López Fernández", width=220)
        self.last_name_entry.grid(row=2, column=1, padx=10, pady=8, sticky="ew")
        self.last_name_entry.insert(0, self.data.get("last_name", ""))

        # Fecha nacimiento
        ctk.CTkLabel(form, text="Fecha Nac.:", font=("Arial", 12)).grid(row=3, column=0, sticky="w", padx=10, pady=8)
        self.birth_entry = ctk.CTkEntry(form, placeholder_text="YYYY-MM-DD", width=220)
        self.birth_entry.grid(row=3, column=1, padx=10, pady=8, sticky="ew")
        self.birth_entry.insert(0, self.data.get("birth_date", ""))

        # Género
        ctk.CTkLabel(form, text="Género:", font=("Arial", 12)).grid(row=4, column=0, sticky="w", padx=10, pady=8)
        self.gender_var = ctk.StringVar(value=self.data.get("gender", "Masculino"))
        gender_combo = ctk.CTkComboBox(form, values=["Masculino", "Femenino"], variable=self.gender_var, width=220, state="readonly")
        gender_combo.grid(row=4, column=1, padx=10, pady=8, sticky="ew")

        # Provincia
        ctk.CTkLabel(form, text="Provincia:", font=("Arial", 12)).grid(row=5, column=0, sticky="w", padx=10, pady=8)
        self.province_var = ctk.StringVar(value=self.data.get("province", "San José"))
        province_combo = ctk.CTkComboBox(form, values=[
            "San José", "Alajuela", "Cartago", "Heredia", "Guanacaste", "Puntarenas", "Limón"
        ], variable=self.province_var, width=220, state="readonly")
        province_combo.grid(row=5, column=1, padx=10, pady=8, sticky="ew")
            person.marital_status = data["marital_status"]
            self.family.members.append(person)
            if hasattr(self, 'add_ego_button'):
                self.add_ego_button.destroy()
            self.draw_tree()

        form = PersonForm(self.root, title="Agregar Persona Principal (Ego)", on_save=on_save)
        form.focus()

    def draw_tree(self):
        """Dibuja el árbol genealógico"""
        self.tree_canvas.delete("all")
        if not self.family.members:
            self.tree_canvas.create_text(
                600, 400,
                text="No hay personas en el árbol",
                font=("Arial", 16),
                fill="white"
            )
            return

        # Usar el visualizador de grafos para dibujar el árbol
        visualizer = FamilyGraphVisualizer()
        visualizer.draw_family_tree(self.family, self.tree_canvas)

        # Conectar el menú contextual a los nodos
        self._connect_menu_to_nodes()

    def _connect_menu_to_nodes(self):
        """Conecta el menú contextual a todos los nodos del canvas"""
        for person in self.family.members:
            # Los eventos ya están vinculados en draw_person_node
            pass

# === PUNTO DE ENTRADA ===
if __name__ == "__main__":
    root = ctk.CTk()
    app = GenealogyApp(root)
    root.mainloop()
