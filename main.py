import customtkinter as ctk
from gui.app import GenealogyApp

if __name__ == "__main__":
    root = ctk.CTk()  
    app = GenealogyApp(root)
    root.mainloop()