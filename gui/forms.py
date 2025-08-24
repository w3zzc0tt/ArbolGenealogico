# forms.py
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import datetime
import sys
import os

# Añadir el directorio raíz del proyecto para importar utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.person import Person

try:
    from utils.validators import (
        validar_cedula,
        validar_fecha,
        validar_fechas_coherentes,
        validar_nombre,
        validar_genero,
        validar_provincia,
        validar_estado_civil,
    )
    HAS_VALIDATORS = True
except ImportError:
    HAS_VALIDATORS = False
    print("Advertencia: No se pudieron importar las utilidades de validación")


class PersonForm(ctk.CTkToplevel):
    def __init__(self, parent, title="Agregar Persona", on_save=None, data=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("500x700")
        self.resizable(False, False)
        self.on_save = on_save
        self.data = data or {}

        # Centrar y bloquear ventana principal
        self.transient(parent)
        self.grab_set()

        self.setup_ui()

    def setup_ui(self):
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            form_frame,
            text="📋 Registrar Persona",
            font=("Arial", 18, "bold")
        ).pack(pady=15)

        form = ctk.CTkFrame(form_frame)
        form.pack(fill=tk.X, padx=10, pady=10)
        form.columnconfigure(1, weight=1)

        # Cédula
        ctk.CTkLabel(form, text="Cédula:", font=("Arial", 12)).grid(
            row=0, column=0, sticky="w", padx=10, pady=6
        )
        self.cedula_entry = ctk.CTkEntry(
            form, placeholder_text="9-12 dígitos", width=220
        )
        self.cedula_entry.grid(row=0, column=1, padx=10, pady=6, sticky="ew")
        self.cedula_entry.insert(0, self.data.get("cedula", ""))

        # Nombre
        ctk.CTkLabel(form, text="Nombre:", font=("Arial", 12)).grid(
            row=1, column=0, sticky="w", padx=10, pady=6
        )
        self.first_name_entry = ctk.CTkEntry(
            form, placeholder_text="Ej: María", width=220
        )
        self.first_name_entry.grid(row=1, column=1, padx=10, pady=6, sticky="ew")
        self.first_name_entry.insert(0, self.data.get("first_name", ""))

        # Apellidos
        ctk.CTkLabel(form, text="Apellidos:", font=("Arial", 12)).grid(
            row=2, column=0, sticky="w", padx=10, pady=6
        )
        self.last_name_entry = ctk.CTkEntry(
            form, placeholder_text="Ej: López Fernández", width=220
        )
        self.last_name_entry.grid(row=2, column=1, padx=10, pady=6, sticky="ew")
        self.last_name_entry.insert(0, self.data.get("last_name", ""))

        # Fecha de nacimiento
        ctk.CTkLabel(form, text="Fecha Nac.:", font=("Arial", 12)).grid(
            row=3, column=0, sticky="w", padx=10, pady=6
        )
        self.birth_entry = ctk.CTkEntry(
            form, placeholder_text="YYYY-MM-DD", width=220
        )
        self.birth_entry.grid(row=3, column=1, padx=10, pady=6, sticky="ew")
        self.birth_entry.insert(0, self.data.get("birth_date", ""))

        # Género
        ctk.CTkLabel(form, text="Género:", font=("Arial", 12)).grid(
            row=4, column=0, sticky="w", padx=10, pady=6
        )
        self.gender_var = ctk.StringVar(
            value=self.data.get("gender", "Masculino")
        )
        gender_combo = ctk.CTkComboBox(
            form,
            values=["Masculino", "Femenino"],
            variable=self.gender_var,
            width=220,
            state="readonly",
        )
        gender_combo.grid(row=4, column=1, padx=10, pady=6, sticky="ew")

        # Provincia
        ctk.CTkLabel(form, text="Provincia:", font=("Arial", 12)).grid(
            row=5, column=0, sticky="w", padx=10, pady=6
        )
        self.province_var = ctk.StringVar(
            value=self.data.get("province", "San José")
        )
        province_combo = ctk.CTkComboBox(
            form,
            values=[
                "San José",
                "Alajuela",
                "Cartago",
                "Heredia",
                "Guanacaste",
                "Puntarenas",
                "Limón",
            ],
            variable=self.province_var,
            width=220,
            state="readonly",
        )
        province_combo.grid(row=5, column=1, padx=10, pady=6, sticky="ew")

        # Estado civil
        ctk.CTkLabel(form, text="Estado Civil:", font=("Arial", 12)).grid(
            row=6, column=0, sticky="w", padx=10, pady=6
        )
        self.marital_status_var = ctk.StringVar(
            value=self.data.get("marital_status", "Soltero/a")
        )
        marital_status_combo = ctk.CTkComboBox(
            form,
            values=[
                "Soltero/a",
                "Casado/a",
                "Divorciado/a",
                "Viudo/a",
                "Unión Libre",
            ],
            variable=self.marital_status_var,
            width=220,
            state="readonly",
        )
        marital_status_combo.grid(row=6, column=1, padx=10, pady=6, sticky="ew")

        # Estado: Vivo / Fallecido
        ctk.CTkLabel(form, text="Estado:", font=("Arial", 12)).grid(
            row=7, column=0, sticky="w", padx=10, pady=6
        )
        self.status_var = ctk.StringVar(
            value="Vivo" if self.data.get("death_date") is None else "Fallecido"
        )
        status_frame = ctk.CTkFrame(form)
        status_frame.grid(row=7, column=1, sticky="w", padx=10, pady=6)
        ctk.CTkRadioButton(
            status_frame,
            text="Vivo",
            variable=self.status_var,
            value="Vivo",
            command=self.toggle_death_field,
        ).pack(side="left", padx=5)
        ctk.CTkRadioButton(
            status_frame,
            text="Fallecido",
            variable=self.status_var,
            value="Fallecido",
            command=self.toggle_death_field,
        ).pack(side="left", padx=5)

        # Fecha de fallecimiento
        self.death_frame = ctk.CTkFrame(form)
        self.death_frame.grid(row=8, column=1, sticky="ew", padx=10, pady=5)
        ctk.CTkLabel(self.death_frame, text="Fecha Fallec.:").pack(side="left")
        self.death_entry = ctk.CTkEntry(
            self.death_frame, placeholder_text="YYYY-MM-DD", width=150
        )
        self.death_entry.pack(side="left", padx=5)
        if self.data.get("death_date"):
            self.death_entry.insert(0, self.data["death_date"])

        # Ocultar si está vivo
        if self.status_var.get() == "Vivo":
            self.death_frame.grid_remove()

        # Botones
        button_frame = ctk.CTkFrame(form_frame)
        button_frame.pack(pady=20)

        ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=self.destroy,
            fg_color="gray",
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            button_frame,
            text="Guardar",
            command=self.save,
            fg_color="#1db954",
        ).pack(side="left", padx=5)

    def toggle_death_field(self):
        """Muestra u oculta el campo de fecha de fallecimiento"""
        if self.status_var.get() == "Fallecido":
            self.death_frame.grid()
        else:
            self.death_entry.delete(0, "end")  # Limpiar si se cambia a "Vivo"
            self.death_frame.grid_remove()

    def save(self):
        """Valida y guarda los datos del formulario"""
        cedula = self.cedula_entry.get().strip()
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        birth_date = self.birth_entry.get().strip()
        gender = self.gender_var.get()
        province = self.province_var.get()
        marital_status = self.marital_status_var.get()
        status = self.status_var.get()
        death_date = self.death_entry.get().strip() if status == "Fallecido" else None

        # Validación de campos obligatorios
        if not all([cedula, first_name, last_name, birth_date]):
            messagebox.showerror("Error", "Todos los campos obligatorios deben llenarse")
            return

        # === Validaciones: Usa utils si están disponibles ===
        if HAS_VALIDATORS:
            try:
                if not validar_cedula(cedula):
                    messagebox.showerror("Error", "Cédula inválida")
                    return

                if not validar_nombre(first_name):
                    messagebox.showerror("Error", "Nombre inválido")
                    return

                if not validar_nombre(last_name):
                    messagebox.showerror("Error", "Apellidos inválidos")
                    return

                if not validar_fecha(birth_date):
                    messagebox.showerror("Error", "Fecha de nacimiento inválida")
                    return

                if death_date and not validar_fecha(death_date):
                    messagebox.showerror("Error", "Fecha de defunción inválida")
                    return

                if death_date and not validar_fechas_coherentes(birth_date, death_date):
                    messagebox.showerror(
                        "Error", "La fecha de defunción debe ser posterior a la de nacimiento"
                    )
                    return

                if not validar_genero(gender):
                    messagebox.showerror("Error", "Género inválido")
                    return

                if not validar_provincia(province):
                    messagebox.showerror("Error", "Provincia inválida")
                    return

                if not validar_estado_civil(marital_status):
                    messagebox.showerror("Error", "Estado civil inválido")
                    return

            except Exception as e:
                messagebox.showerror("Error", f"Error en validación: {str(e)}")
                return
        else:
            # === Validaciones fallback (sin utils) ===
            if not cedula.isdigit() or not (9 <= len(cedula) <= 12):
                messagebox.showerror(
                    "Error", "La cédula debe tener entre 9 y 12 dígitos y contener solo números"
                )
                return

            if not first_name.isalpha() or len(first_name) < 2:
                messagebox.showerror("Error", "Nombre inválido")
                return

            if not all(c.isalpha() or c.isspace() for c in last_name) or len(last_name.strip()) < 2:
                messagebox.showerror("Error", "Apellidos inválidos")
                return

            try:
                datetime.datetime.strptime(birth_date, "%Y-%m-%d")
                if death_date:
                    datetime.datetime.strptime(death_date, "%Y-%m-%d")
                    if birth_date >= death_date:
                        messagebox.showerror(
                            "Error", "La fecha de defunción debe ser posterior a la de nacimiento"
                        )
                        return
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD")
                return

        # === Todos los datos son válidos ===
        data = {
            "cedula": cedula,
            "first_name": first_name,
            "last_name": last_name,
            "birth_date": birth_date,
            "gender": gender,
            "province": province,
            "marital_status": marital_status,
            "death_date": death_date,
        }

        if self.on_save:
            self.on_save(data)
            self.destroy()
        else:
            messagebox.showerror("Error", "No se puede guardar: falta función on_save")