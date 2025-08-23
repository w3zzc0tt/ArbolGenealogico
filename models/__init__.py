# Este archivo indica que el directorio models es un paquete de Python.
# models/__init__.py
from .person import Person
from .family import Family

__all__ = ["Person", "Family"]  