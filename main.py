# main.py
import logging
import sys
import io
import traceback
from tkinter import messagebox

# Configurar logging para ver errores detallados
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    # File handler with UTF-8 encoding and a stream handler that wraps stdout with UTF-8
    handlers=[
        logging.FileHandler("app_error.log", encoding="utf-8"),
        logging.StreamHandler(stream=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace'))
    ]
)

try:
    # Intentar configurar matplotlib solo si es necesario
    try:
        import matplotlib
        matplotlib.use('TkAgg')  # Configurar el backend de matplotlib explícitamente
        logging.info("Matplotlib backend configurado correctamente")
    except Exception as e:
        logging.warning(f"No se pudo configurar matplotlib backend: {str(e)}")
    
    # Importar dependencias
    try:
        import customtkinter as ctk
        logging.info("CustomTkinter importado correctamente")
    except ImportError as e:
        logging.critical("No se pudo importar CustomTkinter. Instálalo con: pip install customtkinter")
        raise
    
    # Verificar estructura del proyecto
    try:
        from gui.app import GenealogyApp
        logging.info("Módulo gui.app importado correctamente")
    except ImportError as e:
        logging.critical(f"No se pudo importar GenealogyApp: {str(e)}")
        logging.critical("Verifica la estructura del proyecto:")
        logging.critical("Debe tener la siguiente estructura:")
        logging.critical("proyecto/")
        logging.critical("├── main.py")
        logging.critical("├── gui/")
        logging.critical("│   ├── __init__.py")
        logging.critical("│   ├── app.py")
        logging.critical("│   ├── forms.py")
        logging.critical("│   ├── simulation_panel.py")
        logging.critical("│   └── ...")
        logging.critical("└── services/")
        logging.critical("    ├── __init__.py")
        logging.critical("    ├── simulacion_service.py")
        logging.critical("    └── ...")
        raise
    
    if __name__ == "__main__":
        try:
            # Configuración adicional para resolver problemas comunes
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("blue")
            logging.info("Configuración de CustomTkinter establecida")
            
            # Inicializar ventana principal
            root = ctk.CTk()
            root.title("Simulador Genealógico")
            root.geometry("1200x800")
            logging.info("Ventana principal creada")
            
            # Intentar crear la aplicación con manejo de errores específico
            try:
                app = GenealogyApp(root)
                logging.info("GenealogyApp inicializada correctamente")
            except NameError as e:
                logging.error("Error de nombre: probablemente falta una clase o función")
                logging.error(f"Detalles: {str(e)}")
                logging.error("Posible causa: error en gui/app.py o dependencias faltantes")
                raise
            except AttributeError as e:
                logging.error("Error de atributo: probablemente uso incorrecto de métodos o propiedades")
                logging.error(f"Detalles: {str(e)}")
                logging.error("Posible causa: uso de calculate_age() en lugar de calculate_virtual_age()")
                logging.error("Verifica los archivos simulation_panel.py y person.py")
                raise
            except Exception as e:
                logging.error("Error inesperado al inicializar GenealogyApp")
                logging.error(f"Detalles: {str(e)}")
                logging.error("Pila de llamadas:\n" + traceback.format_exc())
                raise
            
            # Iniciar bucle principal
            logging.info("Iniciando bucle principal de la aplicación...")
            root.mainloop()
            
        except Exception as e:
            logging.error(f"Error crítico al iniciar la aplicación: {str(e)}", exc_info=True)
            
            # Crear una ventana básica para mostrar el error
            try:
                error_root = ctk.CTk()
                error_root.title("Error de aplicación")
                error_root.geometry("600x400")
                error_root.attributes("-topmost", True)
                
                error_frame = ctk.CTkFrame(error_root)
                error_frame.pack(fill="both", expand=True, padx=20, pady=20)
                
                ctk.CTkLabel(error_frame,
                            text="¡Error al iniciar la aplicación!",
                            font=("Arial", 16, "bold"),
                            text_color="red").pack(pady=10)
                
                # Mensaje de error específico basado en el tipo de excepción
                error_message = str(e)
                if "calculate_age" in error_message:
                    specific_msg = (
                        "Error común: Uso incorrecto de calculate_age() en lugar de calculate_virtual_age()\n\n"
                        "Solución:\n"
                        "1. Abre simulation_panel.py\n"
                        "2. Busca 'calculate_age()' y reemplázalo con 'calculate_virtual_age()'\n"
                        "3. Guarda los cambios y reinicia la aplicación"
                    )
                elif "has no attribute" in error_message:
                    attr_name = error_message.split("'")[1] if "'" in error_message else "atributo desconocido"
                    specific_msg = (
                        f"Error: El objeto no tiene el atributo '{attr_name}'\n\n"
                        "Posibles causas:\n"
                        "1. Error en la definición de la clase Person\n"
                        "2. Uso de propiedades que no existen\n"
                        "3. Problema en la inicialización de objetos\n\n"
                        "Verifica los archivos:\n"
                        "- person.py\n"
                        "- simulation_services.py"
                    )
                else:
                    specific_msg = (
                        "Error desconocido. Revisa el archivo de log para más detalles.\n\n"
                        "Pasos para solucionar:\n"
                        "1. Abre el archivo 'app_error.log'\n"
                        "2. Busca el error específico\n"
                        "3. Corrige el problema en los archivos correspondientes"
                    )
                
                ctk.CTkLabel(error_frame,
                            text=f"Detalles del error:\n{error_message}",
                            wraplength=550,
                            justify="left",
                            text_color="white").pack(pady=5, anchor="w")
                
                ctk.CTkLabel(error_frame,
                            text="\nSOLUCIÓN SUGERIDA:",
                            font=("Arial", 12, "bold"),
                            text_color="#1db954").pack(pady=5, anchor="w")
                
                ctk.CTkLabel(error_frame,
                            text=specific_msg,
                            wraplength=550,
                            justify="left",
                            text_color="#e6e6e6").pack(pady=5, anchor="w")
                
                ctk.CTkButton(error_frame,
                            text="Ver Archivo de Log",
                            command=lambda: open_log_file(),
                            fg_color="#3498db").pack(pady=10)
                
                ctk.CTkButton(error_frame,
                            text="Cerrar",
                            command=error_root.destroy,
                            fg_color="#e74c3c").pack(pady=10)
                
                def open_log_file():
                    import os
                    if os.path.exists("app_error.log"):
                        try:
                            # Para Windows
                            if sys.platform == "win32":
                                os.startfile("app_error.log")
                            # Para macOS
                            elif sys.platform == "darwin":
                                os.system("open app_error.log")
                            # Para Linux
                            else:
                                os.system("xdg-open app_error.log")
                        except Exception as log_error:
                            logging.error(f"No se pudo abrir el archivo de log: {str(log_error)}")
                            messagebox.showerror("Error", f"No se pudo abrir el archivo de log: {str(log_error)}")
                    else:
                        messagebox.showerror("Error", "El archivo de log no existe")
                
                error_root.mainloop()
            except Exception as gui_error:
                # Si no podemos mostrar el error con GUI, imprimir en consola
                logging.error(f"Error al mostrar ventana de error: {str(gui_error)}", exc_info=True)
                print("\n" + "="*70)
                print("ERROR CRÍTICO AL INICIAR LA APLICACIÓN - NO SE PUDO MOSTRAR LA VENTANA DE ERROR")
                print("="*70)
                print(f"Detalles del error principal:\n{str(e)}")
                print("\n" + "-"*70)
                print("Detalles del error al mostrar la ventana de error:")
                print(f"{str(gui_error)}")
                print("\n" + "-"*70)
                print("Pasos para solucionar:")
                print("1. Revisa el archivo 'app_error.log' para detalles completos")
                print("2. Busca estos errores comunes:")
                print("   - Uso de calculate_age() en lugar de calculate_virtual_age()")
                print("   - Métodos no definidos en services/simulacion_service.py")
                print("   - Errores en la definición de la clase Person")
                print("3. Corrige los archivos correspondientes y reinicia la aplicación")
                print("="*70)
                sys.exit(1)

except Exception as import_error:
    # Manejar errores en los imports iniciales
    logging.critical(f"Error FATAL al importar módulos: {str(import_error)}", exc_info=True)
    print("\n" + "="*70)
    print("ERROR FATAL AL IMPORTAR MÓDULOS - IMPOSIBLE INICIAR LA APLICACIÓN")
    print("="*70)
    print(f"Detalles del error:\n{str(import_error)}")
    print("\nPosibles causas:")
    print("1. customtkinter no está instalado correctamente")
    print("2. Falta una dependencia crítica")
    print("3. Error en la estructura del proyecto")
    print("4. Archivos faltantes o corruptos")
    print("="*70)
    print("Pasos para solucionar:")
    print("1. Instala las dependencias: pip install -r requirements.txt")
    print("   Si no tienes requirements.txt, instala:")
    print("   - customtkinter")
    print("   - networkx")
    print("   - matplotlib")
    print("   - Pillow")
    print("2. Verifica la estructura del proyecto:")
    print("   proyecto/")
    print("   ├── main.py")
    print("   ├── gui/")
    print("   │   ├── __init__.py")
    print("   │   ├── app.py")
    print("   │   ├── forms.py")
    print("   │   ├── simulation_panel.py")
    print("   │   └── ...")
    print("   └── services/")
    print("       ├── __init__.py")
    print("       ├── simulacion_service.py")
    print("       └── ...")
    print("3. Asegúrate de tener todos los archivos necesarios")
    print("="*70)
    sys.exit(1)