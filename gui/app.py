# app.py
import customtkinter as ctk
import tkinter as tk
import sys
import os

# Añadir raíz del proyecto para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.family import Family
from models.person import Person
from gui.forms import PersonForm

try:
    from utils.graph_visualizer import FamilyGraphVisualizer
    HAS_VISUALIZER = True
except ImportError:
    HAS_VISUALIZER = False
    print("Advertencia: No se pudo importar FamilyGraphVisualizer")


class GenealogyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌳 Árbol Genealógico Familiar")
        self.root.geometry("1200x800")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.family = Family(1, "Mi Familia")
        self.selected_person = None
        self.create_widgets()

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Pestañas
        self.notebook = ctk.CTkTabview(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tree_tab = self.notebook.add("Árbol Genealógico")
        self.history_tab = self.notebook.add("Historial")

        self.setup_tree_tab()
        self.setup_history_tab()

    def setup_tree_tab(self):
        frame = ctk.CTkFrame(self.tree_tab)
        frame.pack(fill=tk.BOTH, expand=True)

        # Botón agregar Ego
        if not self.family.members:
            self.add_ego_button = ctk.CTkButton(
                frame,
                text="➕ Agregar Persona Principal (Ego)",
                command=self.open_person_form_for_ego,
                font=("Arial", 14, "bold"),
                fg_color="#1db954",
                hover_color="#1ed760"
            )
            self.add_ego_button.pack(pady=20)
        else:
            self.add_ego_button = None

        # Canvas para el árbol
        self.tree_canvas = tk.Canvas(frame, bg="#2a2a2a", highlightthickness=0)
        self.tree_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.draw_tree()

    def open_person_form_for_ego(self):
        def on_save(data):
            person = Person(
                cedula=data["cedula"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                birth_date=data["birth_date"],
                gender=data["gender"],
                province=data["province"],
                death_date=data["death_date"],
                marital_status=data["marital_status"]
            )
            self.family.add_member(person)
            if self.add_ego_button:
                self.add_ego_button.destroy()
            self.draw_tree()
            self.update_history_tab()

        PersonForm(self.root, title="Agregar Persona Principal", on_save=on_save)

    def draw_tree(self):
        self.tree_canvas.delete("all")
        if not self.family.members:
            self.tree_canvas.create_text(600, 400, text="No hay personas en el árbol", fill="white", font=("Arial", 16))
            return

        if HAS_VISUALIZER:
            visualizer = FamilyGraphVisualizer()
            visualizer.draw_family_tree(self.family, self.tree_canvas)
        else:
            self._draw_basic_tree()

    def _draw_basic_tree(self):
        canvas_width = self.tree_canvas.winfo_width() or 1200
        x_step = canvas_width / (len(self.family.members) + 1)
        y = 400

        for i, person in enumerate(self.family.members):
            x = (i + 1) * x_step
            color = "#3b8ed0" if person.alive else "#d35f5f"
            self.tree_canvas.create_oval(x-30, y-30, x+30, y+30, fill=color, outline="#1f7dbf", width=2)
            self.tree_canvas.create_text(x, y, text=f"{person.first_name}\n{person.last_name}", fill="white", font=("Arial", 10, "bold"))
            self.tree_canvas.create_text(x, y+25, text=person.cedula, fill="lightgray", font=("Arial", 8))

    def setup_history_tab(self):
        self.history_text = tk.Text(self.history_tab, bg="#2a2a2a", fg="white", font=("Consolas", 10))
        self.history_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.update_history_tab()

    def update_history_tab(self):
        self.history_text.delete(1.0, tk.END)
        for person in self.family.members:
            self.history_text.insert(tk.END, f"👤 {person}\n", "person")
            for event in person.history:
                self.history_text.insert(tk.END, f"  • {event}\n", "event")
            self.history_text.insert(tk.END, "\n")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    root = ctk.CTk()
    app = GenealogyApp(root)
    app.run()