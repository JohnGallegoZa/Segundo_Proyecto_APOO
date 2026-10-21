import unittest
from robots import *

class Pruebas(unittest.TestCase):
    def setUp(self):
        self.gestor = GestorFlota(ClimaSimulado(False), (6.23, -75.61))
        self.dron = Dron('D', 100, 'A', 3, 20, 5, ['azotea'], ['documentos'], 100)
        self.gestor.registrar_robot(self.dron)
        self.s = Solicitud('S', Carga('documentos', 1), 'A', 'B', 1, 'azotea')
        self.gestor.registrar_solicitud(self.s)

    def test_clima_desfavorable(self):
        self.assertFalse(self.gestor.asignar(self.s))
        self.assertEqual(self.s.estado, 'pendiente')

    def test_cambio_servicio(self):
        self.gestor.servicio_clima = ClimaSimulado(True)
        self.assertTrue(self.gestor.asignar(self.s))

    def test_encapsulamiento(self):
        with self.assertRaises(ValueError):
            self.dron.cambiar_bateria(120)

    def test_polimorfismo(self):
        ruedas = RobotRuedas('R', 100, 'A', 3, 20, 5, ['pavimento'], ['documentos'], 100)
        self.assertNotEqual(ruedas.calcular_tiempo(1), self.dron.calcular_tiempo(1))

    def test_capacidad(self):
        self.assertFalse(self.dron.puede_transportar(Carga('documentos', 4)))

    def test_entrega(self):
        self.gestor.servicio_clima = ClimaSimulado(True)
        self.gestor.asignar(self.s)
        self.assertTrue(self.gestor.finalizar(self.s, True))
        self.assertEqual(self.s.estado, 'exitosa')

if __name__ == '__main__':
    unittest.main()
