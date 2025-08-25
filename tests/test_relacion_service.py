import unittest
from models.family import Family
from models.person import Person
from services.relacion_service import RelacionService

class TestRelacionService(unittest.TestCase):
    def setUp(self):
        # Proporcionar id y name al crear la familia
        self.family = Family(id="1", name="Familia Campos")
        self.father = Person("123456789", "Jose", "Campos", "2006-05-24", "Masculino", "Provincia")
        self.mother = Person("987654321", "Nelsy", "Dinarte", "1975-02-13", "Femenino", "Provincia")
        self.child = Person("111111111", "Zack", "Campos", "2030-06-19", "Masculino", "Provincia")
        
        self.family.add_or_update_member(self.father)
        self.family.add_or_update_member(self.mother)
        self.family.add_or_update_member(self.child)

        # Registrar la pareja
        RelacionService.registrar_pareja(self.family, self.father.cedula, self.mother.cedula)

    def test_registrar_hijo_con_pareja(self):
        # Registrar al hijo
        result, message = RelacionService.registrar_hijo_con_pareja(self.family, self.father.cedula, self.child.cedula)
        
        # Verificar que el registro fue exitoso
        self.assertTrue(result)
        self.assertIn(self.child, self.father.children)
        self.assertIn(self.child, self.mother.children)

if __name__ == "__main__":
    unittest.main()
