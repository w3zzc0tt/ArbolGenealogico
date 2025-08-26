# gui/forms.py - VERSIÓN SIN LÍMITES DE FECHA
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import datetime
import sys
import os
import re

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
            form, placeholder_text="YYYY-MM-DD (cualquier año)", width=220
        )
        self.birth_entry.grid(row=3, column=1, padx=10, pady=6, sticky="ew")
        self.birth_entry.insert(0, self.data.get("birth_date", ""))

        # Género - CÓDIGO CORREGIDO
        ctk.CTkLabel(form, text="Género:", font=("Arial", 12)).grid(
            row=4, column=0, sticky="w", padx=10, pady=6
        )
        
        # Configurar los valores del combobox
        gender_values = ["Masculino", "Femenino"]
        
        # Determinar el valor inicial
        initial_gender = "Masculino"  # Valor por defecto
        if self.data and "gender" in self.data:
            # Manejar diferentes formatos de género
            data_gender = self.data["gender"]
            if data_gender in ["M", "Masculino"]:
                initial_gender = "Masculino"
            elif data_gender in ["F", "Femenino"]:
                initial_gender = "Femenino"
        
        # Crear la variable de control
        self.gender_var = ctk.StringVar(value=initial_gender)
        
        # Crear el combobox
        gender_combo = ctk.CTkComboBox(
            form,
            values=gender_values,
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
            self.death_frame, placeholder_text="YYYY-MM-DD (cualquier año)", width=150
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
            self.death_entry.delete(0, "end")
            self.death_frame.grid_remove()

    def save(self):
        """Valida y guarda los datos del formulario - SIN LÍMITES DE FECHA"""
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
        missing_fields = []
        if not cedula: 
            missing_fields.append("Cédula")
        if not first_name: 
            missing_fields.append("Nombre")
        if not last_name: 
            missing_fields.append("Apellidos")
        if not birth_date: 
            missing_fields.append("Fecha de Nacimiento")
        if not gender or gender == "Seleccionar género": 
            missing_fields.append("Género")
        
        if missing_fields:
            error_msg = "Los siguientes campos son obligatorios:\n" + "\n".join(f"- {field}" for field in missing_fields)
            messagebox.showerror("Campos obligatorios", error_msg)
            return

        # === Validaciones mejoradas ===
        if HAS_VALIDATORS:
            try:
                # Validar cédula con provincia
                valido_cedula, mensaje_cedula = validar_cedula(cedula, province)
                if not valido_cedula:
                    messagebox.showerror("Error de validación", mensaje_cedula)
                    return

                # Validar nombre
                valido_nombre, mensaje_nombre = validar_nombre(first_name, "nombre")
                if not valido_nombre:
                    messagebox.showerror("Error de validación", mensaje_nombre)
                    return

                # Validar apellido
                valido_apellido, mensaje_apellido = validar_nombre(last_name, "apellido")
                if not valido_apellido:
                    messagebox.showerror("Error de validación", mensaje_apellido)
                    return

                # Validar fecha de nacimiento
                valido_nacimiento, mensaje_nacimiento = validar_fecha(birth_date, "nacimiento")
                if not valido_nacimiento:
                    messagebox.showerror("Error de validación", mensaje_nacimiento)
                    return

                # Validar fecha de fallecimiento (si existe)
                if death_date:
                    valido_fallecimiento, mensaje_fallecimiento = validar_fecha(death_date, "fallecimiento")
                    if not valido_fallecimiento:
                        messagebox.showerror("Error de validación", mensaje_fallecimiento)
                        return
                    
                    # Validar coherencia entre fechas
                    valido_coherencia, mensaje_coherencia = validar_fechas_coherentes(birth_date, death_date)
                    if not valido_coherencia:
                        messagebox.showerror("Error de validación", mensaje_coherencia)
                        return

                # Validar género - CORREGIDO: Ahora acepta "Masculino"/"Femenino"
                valido_genero, mensaje_genero = validar_genero(gender)
                if not valido_genero:
                    messagebox.showerror("Error de validación", "Debe seleccionar un género válido")
                    return

                # Validar provincia
                valido_provincia, mensaje_provincia = validar_provincia(province)
                if not valido_provincia:
                    messagebox.showerror("Error de validación", mensaje_provincia)
                    return

                # Validar estado civil
                valido_estado, mensaje_estado = validar_estado_civil(marital_status)
                if not valido_estado:
                    messagebox.showerror("Error de validación", mensaje_estado)
                    return

            except Exception as e:
                messagebox.showerror("Error", f"Error en validación: {str(e)}")
                return
        else:
            # === Validaciones fallback SIN LÍMITES DE FECHA ===
            # Validar cédula
            if not cedula.isdigit():
                messagebox.showerror("Error de validación", "La cédula debe contener solo números")
                return
            if not (9 <= len(cedula) <= 12):
                messagebox.showerror("Error de validación", "La cédula debe tener entre 9 y 12 dígitos")
                return
                
            # Verificar que el primer dígito coincida con la provincia
            provincia_digitos = {
                "San José": "1",
                "Alajuela": "2", 
                "Cartago": "3",
                "Heredia": "4",
                "Guanacaste": "5",
                "Puntarenas": "6",
                "Limón": "7"
            }
            
            if province in provincia_digitos:
                digito_esperado = provincia_digitos[province]
                if cedula[0] != digito_esperado:
                    provincia_correcta = next((prov for prov, dig in provincia_digitos.items() 
                                            if dig == cedula[0]), None)
                    if provincia_correcta:
                        messagebox.showerror("Error de validación", 
                                        f"Error de provincia: La cédula {cedula} corresponde a {provincia_correcta}, no a {province}")
                    else:
                        messagebox.showerror("Error de validación", 
                                        f"El primer dígito de la cédula ({cedula[0]}) no corresponde a ninguna provincia válida")
                    return
            
            # Validar nombre
            if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-]+$", first_name) or len(first_name.strip()) < 2:
                messagebox.showerror("Error de validación", 
                                "Nombre inválido (solo letras, espacios y guiones, mínimo 2 caracteres)")
                return
            
            # Validar apellido
            if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-]+$", last_name) or len(last_name.strip()) < 2:
                messagebox.showerror("Error de validación", 
                                "Apellidos inválidos (solo letras, espacios y guiones, mínimo 2 caracteres)")
                return
            
            # ✅ VALIDACIÓN DE FECHAS SIN LÍMITES DE RANGO
            try:
                birth_datetime = datetime.datetime.strptime(birth_date, "%Y-%m-%d")
                    
                if death_date:
                    death_datetime = datetime.datetime.strptime(death_date, "%Y-%m-%d")
                    
                    # Verificar coherencia entre fechas
                    if birth_datetime >= death_datetime:
                        messagebox.showerror(
                            "Error de validación", 
                            "La fecha de fallecimiento debe ser posterior a la de nacimiento"
                        )
                        return
            except ValueError:
                messagebox.showerror("Error de validación", 
                                "Formato de fecha inválido. Use el formato YYYY-MM-DD")
                return

        # === Datos validados correctamente ===
        data = {
            "cedula": cedula,
            "first_name": first_name,
            "last_name": last_name,
            "birth_date": birth_date,
            "gender": gender,  # Mantener "Masculino"/"Femenino" 
            "province": province,
            "marital_status": marital_status,
            "death_date": death_date,
        }

        if self.on_save:
            self.on_save(data)
            self.destroy()
        else:
            messagebox.showerror("Error", "No se puede guardar: falta función on_save")