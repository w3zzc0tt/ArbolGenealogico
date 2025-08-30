# gui/family_manager_panel.py
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, simpledialog
from models.family_manager import FamilyManager
from models.family import Family

class FamilyManagerPanel:
    """Panel para gestionar familias del árbol genealógico"""
    
    def __init__(self, parent, family_manager: FamilyManager, on_family_change_callback=None, app_instance=None):
        self.parent = parent
       def update_quick_stats(self):
        """Actualiza las estadísticas rápidas del header"""
        stats = self.family_manager.get_stats()
        quick_text = f"📊 {stats['total_families']} familia{'s' if stats['total_families'] != 1 else ''} • "
        quick_text += f"👥 {stats['total_members']} miembro{'s' if stats['total_members'] != 1 else ''} • "
        quick_text += f"📈 Próximo ID: {stats['next_id']:03d}"
        
        self.quick_stats_label.configure(text=quick_text)
    
    def manual_save(self):
        """Realiza un guardado manual de los datos"""
        if self.app_instance:
            success = self.app_instance.save_data()
            if success:
                messagebox.showinfo("Guardado", "💾 Datos guardados exitosamente")
            else:
                messagebox.showerror("Error", "❌ Error al guardar datos")
        else:
            messagebox.showwarning("Advertencia", "No se puede guardar: referencia a la aplicación no disponible")
    
    def create_backup(self):
        """Crea una copia de seguridad"""
        if self.app_instance:
            self.app_instance.create_backup()
        else:
            messagebox.showwarning("Advertencia", "No se puede crear backup: referencia a la aplicación no disponible")f.family_manager = family_manager
        self.on_family_change_callback = on_family_change_callback
        self.app_instance = app_instance  # Referencia a la aplicación principal
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.frame = ctk.CTkFrame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header con título
        self.setup_header()
        
        # Contenido principal en dos columnas
        main_container = ctk.CTkFrame(self.frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Columna izquierda - Gestión de familias
        left_frame = ctk.CTkFrame(main_container)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Columna derecha - Información y estadísticas
        right_frame = ctk.CTkFrame(main_container)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Configurar contenido de las columnas
        self.setup_family_management(left_frame)
        self.setup_info_panel(right_frame)
        
        # Actualizar la lista inicial
        self.refresh_family_list()
    
    def setup_header(self):
        """Configura el encabezado del panel"""
        header_frame = ctk.CTkFrame(self.frame, height=80)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        # Título principal
        title_label = ctk.CTkLabel(
            header_frame,
            text="👨‍👩‍👧‍👦 Gestor de Familias",
            font=("Arial", 24, "bold"),
            text_color="#1976d2"
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=20)
        
        # Frame para botones de guardado
        save_frame = ctk.CTkFrame(header_frame)
        save_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Botón de guardado manual
        save_btn = ctk.CTkButton(
            save_frame,
            text="💾 Guardar Datos",
            command=self.manual_save,
            fg_color="#28a745",
            hover_color="#218838",
            font=("Arial", 12, "bold"),
            width=120,
            height=30
        )
        save_btn.pack(side=tk.TOP, pady=2)
        
        # Botón de backup
        backup_btn = ctk.CTkButton(
            save_frame,
            text="📦 Backup",
            command=self.create_backup,
            fg_color="#17a2b8",
            hover_color="#138496",
            font=("Arial", 10),
            width=120,
            height=25
        )
        backup_btn.pack(side=tk.TOP, pady=2)
        
        # Estadísticas rápidas
        self.quick_stats_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=("Arial", 12),
            text_color="#555"
        )
        self.quick_stats_label.pack(side=tk.RIGHT, padx=20, pady=20)
    
    def setup_family_management(self, parent):
        """Configura el panel de gestión de familias"""
        # Título de la sección
        ctk.CTkLabel(
            parent,
            text="🏠 Gestión de Familias",
            font=("Arial", 16, "bold"),
            text_color="#1976d2"
        ).pack(pady=(10, 5))
        
        # Botón para crear nueva familia
        create_btn = ctk.CTkButton(
            parent,
            text="➕ Crear Nueva Familia",
            command=self.create_new_family,
            fg_color="#28a745",
            hover_color="#218838",
            font=("Arial", 12, "bold"),
            height=40
        )
        create_btn.pack(pady=10, padx=10, fill=tk.X)
        
        # Lista de familias
        list_frame = ctk.CTkFrame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            list_frame,
            text="📋 Lista de Familias",
            font=("Arial", 14, "bold")
        ).pack(pady=(10, 5))
        
        # Frame para la lista scrollable
        self.families_list_frame = ctk.CTkScrollableFrame(list_frame, height=300)
        self.families_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def setup_info_panel(self, parent):
        """Configura el panel de información y estadísticas"""
        # Título
        ctk.CTkLabel(
            parent,
            text="📊 Información del Sistema",
            font=("Arial", 16, "bold"),
            text_color="#1976d2"
        ).pack(pady=(10, 5))
        
        # Panel de familia actual
        current_family_frame = ctk.CTkFrame(parent)
        current_family_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ctk.CTkLabel(
            current_family_frame,
            text="👑 Familia Actual",
            font=("Arial", 14, "bold")
        ).pack(pady=(10, 5))
        
        self.current_family_label = ctk.CTkLabel(
            current_family_frame,
            text="Ninguna familia seleccionada",
            font=("Arial", 12),
            wraplength=300
        )
        self.current_family_label.pack(pady=(0, 10), padx=10)
        
        # Panel de estadísticas
        stats_frame = ctk.CTkFrame(parent)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ctk.CTkLabel(
            stats_frame,
            text="📈 Estadísticas",
            font=("Arial", 14, "bold")
        ).pack(pady=(10, 5))
        
        self.stats_text = ctk.CTkTextbox(
            stats_frame,
            height=200,
            font=("Consolas", 10)
        )
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Panel de compactación de IDs
        ids_frame = ctk.CTkFrame(parent)
        ids_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ctk.CTkLabel(
            ids_frame,
            text="🔄 Compactación Automática de IDs",
            font=("Arial", 14, "bold")
        ).pack(pady=(10, 5))
        
        self.compaction_info_label = ctk.CTkLabel(
            ids_frame,
            text="Los IDs se compactan automáticamente al eliminar familias.\nNo hay huecos en la numeración.",
            font=("Arial", 11),
            wraplength=300
        )
        self.compaction_info_label.pack(pady=(0, 10), padx=10)
    
    def create_new_family(self):
        """Crea una nueva familia"""
        # Solicitar nombre de la familia
        dialog = ctk.CTkInputDialog(
            text="Ingrese el nombre de la nueva familia:",
            title="Crear Nueva Familia"
        )
        family_name = dialog.get_input()
        
        if family_name and family_name.strip():
            family_name = family_name.strip()
            
            # Verificar que no exista una familia con el mismo nombre
            existing_families = self.family_manager.get_all_families()
            for family in existing_families.values():
                if family.name.lower() == family_name.lower():
                    messagebox.showerror("Error", f"Ya existe una familia con el nombre '{family_name}'")
                    return
            
            # Crear la familia
            family_id = self.family_manager.create_family(family_name)
            
            # Actualizar la interfaz
            self.refresh_family_list()
            
            # Mostrar mensaje de éxito
            messagebox.showinfo(
                "Éxito", 
                f"Familia '{family_name}' creada exitosamente con ID {family_id:03d}"
            )
            
            # Notificar cambio si hay callback
            if self.on_family_change_callback:
                self.on_family_change_callback()
    
    def delete_family(self, family_id: int):
        """Elimina una familia"""
        family = self.family_manager.get_family(family_id)
        if not family:
            return
        
        # Confirmar eliminación
        result = messagebox.askyesno(
            "Confirmar Eliminación",
            f"¿Está seguro de que desea eliminar la familia '{family.name}' (ID {family_id:03d})?\n\n"
            f"Esta acción eliminará {len(family.members)} miembros y no se puede deshacer.\n\n"
            f"⚠️  IMPORTANTE: Todas las familias con ID mayor se reasignarán:\n"
            f"• Sus IDs se reducirán en 1 para compactar la numeración\n"
            f"• Ejemplo: Si eliminas ID 002, la familia ID 003 pasará a ser ID 002"
        )
        
        if result:
            success = self.family_manager.delete_family(family_id)
            if success:
                self.refresh_family_list()
                messagebox.showinfo("Éxito", f"Familia eliminada e IDs compactados automáticamente.")
                
                # Notificar cambio si hay callback
                if self.on_family_change_callback:
                    self.on_family_change_callback()
    
    def select_family(self, family_id: int):
        """Selecciona una familia como actual"""
        success = self.family_manager.set_current_family(family_id)
        if success:
            self.refresh_family_list()
            family = self.family_manager.get_family(family_id)
            messagebox.showinfo("Familia Seleccionada", f"Familia '{family.name}' seleccionada como actual")
            
            # Notificar cambio si hay callback
            if self.on_family_change_callback:
                self.on_family_change_callback()
    
    def rename_family(self, family_id: int):
        """Renombra una familia"""
        family = self.family_manager.get_family(family_id)
        if not family:
            return
        
        # Solicitar nuevo nombre
        dialog = ctk.CTkInputDialog(
            text=f"Nuevo nombre para la familia (actual: '{family.name}'):",
            title="Renombrar Familia"
        )
        new_name = dialog.get_input()
        
        if new_name and new_name.strip():
            new_name = new_name.strip()
            
            # Verificar que no exista otra familia con el mismo nombre
            existing_families = self.family_manager.get_all_families()
            for fid, fam in existing_families.items():
                if fid != family_id and fam.name.lower() == new_name.lower():
                    messagebox.showerror("Error", f"Ya existe otra familia con el nombre '{new_name}'")
                    return
            
            # Renombrar
            success = self.family_manager.rename_family(family_id, new_name)
            if success:
                self.refresh_family_list()
                messagebox.showinfo("Éxito", f"Familia renombrada a '{new_name}'")
                
                # Notificar cambio si hay callback
                if self.on_family_change_callback:
                    self.on_family_change_callback()
    
    def refresh_family_list(self):
        """Actualiza la lista de familias y toda la información"""
        # Limpiar la lista actual
        for widget in self.families_list_frame.winfo_children():
            widget.destroy()
        
        # Obtener familias
        families_list = self.family_manager.get_families_list()
        current_family_id = self.family_manager.current_family_id
        
        if not families_list:
            # No hay familias
            no_families_label = ctk.CTkLabel(
                self.families_list_frame,
                text="No hay familias creadas.\nHaz clic en 'Crear Nueva Familia' para comenzar.",
                font=("Arial", 12),
                text_color="#666"
            )
            no_families_label.pack(pady=20)
        else:
            # Mostrar cada familia
            for family_id, family_name, member_count in families_list:
                self.create_family_item(family_id, family_name, member_count, current_family_id)
        
        # Actualizar información adicional
        self.update_current_family_info()
        self.update_stats()
        self.update_compaction_info()
        self.update_quick_stats()
    
    def create_family_item(self, family_id: int, family_name: str, member_count: int, current_family_id: int):
        """Crea un elemento de familia en la lista"""
        # Frame para la familia
        family_frame = ctk.CTkFrame(self.families_list_frame)
        family_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Determinar si es la familia actual
        is_current = family_id == current_family_id
        bg_color = "#e3f2fd" if is_current else None
        
        # Información de la familia
        info_frame = ctk.CTkFrame(family_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # ID y nombre
        id_name_text = f"👑 ID {family_id:03d}: {family_name}" if is_current else f"ID {family_id:03d}: {family_name}"
        id_label = ctk.CTkLabel(
            info_frame,
            text=id_name_text,
            font=("Arial", 12, "bold" if is_current else "normal"),
            text_color="#1976d2" if is_current else None
        )
        id_label.pack(anchor="w", padx=10, pady=(5, 0))
        
        # Número de miembros
        members_text = f"👥 {member_count} miembro{'s' if member_count != 1 else ''}"
        members_label = ctk.CTkLabel(
            info_frame,
            text=members_text,
            font=("Arial", 10),
            text_color="#666"
        )
        members_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        # Botones de acción
        buttons_frame = ctk.CTkFrame(family_frame)
        buttons_frame.pack(side=tk.RIGHT, padx=5, pady=5)
        
        if not is_current:
            select_btn = ctk.CTkButton(
                buttons_frame,
                text="Seleccionar",
                command=lambda: self.select_family(family_id),
                fg_color="#1976d2",
                hover_color="#1565c0",
                width=80,
                height=25,
                font=("Arial", 9)
            )
            select_btn.pack(side=tk.TOP, pady=2)
        
        rename_btn = ctk.CTkButton(
            buttons_frame,
            text="Renombrar",
            command=lambda: self.rename_family(family_id),
            fg_color="#ff9800",
            hover_color="#f57c00",
            width=80,
            height=25,
            font=("Arial", 9)
        )
        rename_btn.pack(side=tk.TOP, pady=2)
        
        delete_btn = ctk.CTkButton(
            buttons_frame,
            text="Eliminar",
            command=lambda: self.delete_family(family_id),
            fg_color="#f44336",
            hover_color="#d32f2f",
            width=80,
            height=25,
            font=("Arial", 9)
        )
        delete_btn.pack(side=tk.TOP, pady=2)
    
    def update_current_family_info(self):
        """Actualiza la información de la familia actual"""
        current_family = self.family_manager.get_current_family()
        if current_family:
            info_text = f"ID {self.family_manager.current_family_id:03d}: {current_family.name}\n"
            info_text += f"👥 {len(current_family.members)} miembro{'s' if len(current_family.members) != 1 else ''}\n"
            if current_family.description:
                info_text += f"📝 {current_family.description}"
        else:
            info_text = "Ninguna familia seleccionada\n\nCrea una nueva familia para comenzar."
        
        self.current_family_label.configure(text=info_text)
    
    def update_stats(self):
        """Actualiza las estadísticas del sistema"""
        stats = self.family_manager.get_stats()
        
        stats_text = "📊 ESTADÍSTICAS DEL SISTEMA\n"
        stats_text += "═" * 35 + "\n\n"
        stats_text += f"🏠 Total de familias: {stats['total_families']}\n"
        stats_text += f"👥 Total de miembros: {stats['total_members']}\n"
        stats_text += f" Próximo ID: {stats['next_id']:03d}\n"
        
        if stats['current_family_id']:
            stats_text += f"👑 Familia actual: ID {stats['current_family_id']:03d}\n"
        else:
            stats_text += "👑 Familia actual: Ninguna\n"
        
        stats_text += "\n" + "═" * 35 + "\n"
        stats_text += "� COMPACTACIÓN AUTOMÁTICA:\n"
        stats_text += "• Al eliminar una familia, los IDs\n"
        stats_text += "  posteriores se compactan hacia abajo\n"
        stats_text += "• No hay huecos en la numeración\n"
        stats_text += "• Los IDs siempre son consecutivos"
        
        self.stats_text.delete("1.0", "end")
        self.stats_text.insert("1.0", stats_text)
    
    def update_compaction_info(self):
        """Actualiza la información sobre compactación de IDs"""
        families_count = len(self.family_manager.get_all_families())
        if families_count > 0:
            info_text = f"IDs actuales: 001 - {families_count:03d} (consecutivos)\n"
            info_text += "Al eliminar una familia, los IDs se compactan automáticamente."
        else:
            info_text = "No hay familias creadas.\nLos IDs comenzarán desde 001."
        
        self.compaction_info_label.configure(text=info_text)
    
    def update_quick_stats(self):
        """Actualiza las estadísticas rápidas del header"""
        stats = self.family_manager.get_stats()
        quick_text = f"📊 {stats['total_families']} familia{'s' if stats['total_families'] != 1 else ''} • "
        quick_text += f"👥 {stats['total_members']} miembro{'s' if stats['total_members'] != 1 else ''} • "
        quick_text += f"� Próximo ID: {stats['next_id']:03d}"
        
        self.quick_stats_label.configure(text=quick_text)
