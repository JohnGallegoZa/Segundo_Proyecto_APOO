import unittest

from asignador import AsignadorEntregas
from bitacora import Bitacora, Evento
from carga import Alimento, Documento, Fragil, MaterialPeligroso
from clima import ServicioClimaOpenMeteo, ServicioClimaSimulado
from flota import Flota
from robot import Dron, RobotOrugas, RobotRuedas
from solicitud import Solicitud
from ubicacion import Ubicacion

CAMPUS = Ubicacion("Campus", 6.2672, -75.5688)


def armar_sistema(clima, robots):
    flota = Flota()
    for robot in robots:
        flota.registrar_robot(robot)
    bitacora = Bitacora()
    return AsignadorEntregas(flota, clima, bitacora, CAMPUS), bitacora


class TestPolimorfismo(unittest.TestCase):
    def test_cada_robot_calcula_su_propio_costo_y_tiempo(self):
        solicitud = Solicitud(1, "Decanatura", Documento("Actas", 1), "EDIFICIOS", 1.0)
        ruedas, orugas, dron = RobotRuedas("RW"), RobotOrugas("RO"), Dron("DR")
        # Misma solicitud, resultados distintos según el subtipo
        self.assertEqual(ruedas.calcular_costo(solicitud), 2500)   # 1000 + 1500
        self.assertEqual(orugas.calcular_costo(solicitud), 3500)   # 1000 + 2500
        self.assertEqual(dron.calcular_costo(solicitud), 6000)     # 1000 + 4000 + seguro 1000
        self.assertEqual(ruedas.calcular_tiempo_min(solicitud.distancia_km), 10)
        self.assertEqual(dron.calcular_tiempo_min(solicitud.distancia_km), 4.5)  # 1.5 + 3

    def test_cada_carga_decide_en_que_robots_viaja(self):
        ruedas, orugas, dron = RobotRuedas("RW"), RobotOrugas("RO"), Dron("DR")
        peligroso = MaterialPeligroso("Ácido", 1, 2)
        fragil = Fragil("Vidrio", 1)
        frio = Alimento("Helado", 1, requiere_frio=True)
        self.assertTrue(peligroso.admite_robot(ruedas))
        self.assertFalse(peligroso.admite_robot(orugas))
        self.assertFalse(peligroso.admite_robot(dron))
        self.assertFalse(fragil.admite_robot(orugas))
        self.assertTrue(fragil.admite_robot(dron))
        self.assertTrue(frio.admite_robot(ruedas))
        self.assertFalse(frio.admite_robot(dron))
        self.assertTrue(Documento("Hoja", 0.1).admite_robot(orugas))


class TestEncapsulamiento(unittest.TestCase):
    def test_bateria_invalida_se_rechaza(self):
        with self.assertRaises(ValueError):
            RobotRuedas("RW", bateria=150)

    def test_peso_invalido_se_rechaza(self):
        with self.assertRaises(ValueError):
            Documento("Hoja", -1)
        with self.assertRaises(ValueError):
            MaterialPeligroso("Ácido", 10, 1)  # supera el máximo de 5 kg

    def test_no_se_puede_modificar_la_bateria_desde_afuera(self):
        robot = RobotRuedas("RW")
        with self.assertRaises(AttributeError):
            robot.bateria = 5

    def test_zona_y_distancia_invalidas(self):
        with self.assertRaises(ValueError):
            Solicitud(1, "X", Documento("Hoja", 1), "LUNA", 1)
        with self.assertRaises(ValueError):
            Solicitud(1, "X", Documento("Hoja", 1), "EDIFICIOS", 0)

    def test_robot_ocupado_no_acepta_otra_reserva(self):
        robot = RobotRuedas("RW")
        s1 = Solicitud(1, "A", Documento("Hoja", 1), "EDIFICIOS", 0.5)
        s2 = Solicitud(2, "B", Documento("Hoja", 1), "EDIFICIOS", 0.5)
        robot.reservar(s1)
        with self.assertRaises(ValueError):
            robot.reservar(s2)


class TestAsignacionYClima(unittest.TestCase):
    def test_con_buen_clima_gana_el_dron_si_es_mas_barato(self):
        asignador, _ = armar_sistema(ServicioClimaSimulado(True), [RobotRuedas("RW"), Dron("DR")])
        solicitud = Solicitud(1, "A", Documento("Hoja", 1), "AZOTEA", 0.4)
        self.assertEqual(asignador.asignar(solicitud).id_robot, "DR")

    def test_con_mal_clima_el_dron_se_descarta_y_se_reasigna(self):
        asignador, bitacora = armar_sistema(ServicioClimaSimulado(False), [RobotRuedas("RW"), Dron("DR")])
        solicitud = Solicitud(1, "A", Documento("Hoja", 1), "EDIFICIOS", 0.4)
        self.assertEqual(asignador.asignar(solicitud).id_robot, "RW")
        self.assertEqual(bitacora.contar(Evento.RECHAZO_CLIMA), 1)

    def test_si_solo_hay_dron_y_mal_clima_queda_pendiente(self):
        asignador, _ = armar_sistema(ServicioClimaSimulado(False), [Dron("DR")])
        solicitud = Solicitud(1, "A", Documento("Hoja", 1), "AZOTEA", 0.4)
        self.assertIsNone(asignador.asignar(solicitud))
        self.assertEqual(solicitud.estado, Solicitud.PENDIENTE)

    def test_cambiar_el_proveedor_no_exige_tocar_el_asignador(self):
        clima = ServicioClimaSimulado(False)
        asignador, _ = armar_sistema(clima, [Dron("DR")])
        solicitud = Solicitud(1, "A", Documento("Hoja", 1), "AZOTEA", 0.4)
        self.assertIsNone(asignador.asignar(solicitud))
        clima.establecer_favorable(True)  # mejora el clima; mismo asignador
        self.assertEqual(asignador.asignar(solicitud).id_robot, "DR")

    def test_no_se_asigna_robot_con_bateria_insuficiente(self):
        asignador, _ = armar_sistema(ServicioClimaSimulado(True), [RobotRuedas("RW", bateria=12)])
        solicitud = Solicitud(1, "A", Documento("Hoja", 1), "EDIFICIOS", 1.0)  # gasta 5% + reserva 10%
        self.assertIsNone(asignador.asignar(solicitud))


class TestServicioClimaReal(unittest.TestCase):
    def test_api_caida_devuelve_false_y_guarda_el_error(self):
        servicio = ServicioClimaOpenMeteo(url_base="http://127.0.0.1:9/v1/forecast", timeout_seg=1)
        self.assertFalse(servicio.condiciones_favorables(CAMPUS))
        self.assertIsNotNone(servicio.ultimo_error)

    def test_umbrales_de_viento_y_lluvia(self):
        class Falso(ServicioClimaOpenMeteo):
            def __init__(self, viento, lluvia):
                super().__init__(umbral_viento_kmh=25, umbral_lluvia_pct=50)
                self._datos = {"current": {"wind_speed_10m": viento},
                               "hourly": {"precipitation_probability": [lluvia]}}

            def _consultar(self, ubicacion):
                return self._datos

        self.assertTrue(Falso(10, 20).condiciones_favorables(CAMPUS))
        self.assertFalse(Falso(30, 20).condiciones_favorables(CAMPUS))   # mucho viento
        self.assertFalse(Falso(10, 80).condiciones_favorables(CAMPUS))   # mucha lluvia

    def test_respuesta_incompleta_no_autoriza_vuelo(self):
        class Roto(ServicioClimaOpenMeteo):
            def _consultar(self, ubicacion):
                return {"current": {}}

        self.assertFalse(Roto().condiciones_favorables(CAMPUS))


class TestBitacoraYFlujo(unittest.TestCase):
    def test_entrega_exitosa_y_mantenimiento_por_bateria_baja(self):
        asignador, bitacora = armar_sistema(ServicioClimaSimulado(True), [RobotRuedas("RW", bateria=24)])
        solicitud = Solicitud(1, "A", Documento("Hoja", 1), "EDIFICIOS", 1.0)  # gasta 5% -> queda en 19%
        robot = asignador.asignar(solicitud)
        asignador.completar_entrega(solicitud)
        self.assertEqual(solicitud.estado, Solicitud.ENTREGADA)
        self.assertEqual(robot.estado, "MANTENIMIENTO")
        self.assertEqual(bitacora.contar(Evento.MANTENIMIENTO), 1)
        robot.terminar_mantenimiento()
        self.assertEqual(robot.bateria, 100)

    def test_entrega_fallida_libera_el_robot(self):
        asignador, bitacora = armar_sistema(ServicioClimaSimulado(True), [RobotRuedas("RW")])
        solicitud = Solicitud(1, "A", Documento("Hoja", 1), "EDIFICIOS", 0.5)
        robot = asignador.asignar(solicitud)
        asignador.completar_entrega(solicitud, exito=False)
        self.assertEqual(solicitud.estado, Solicitud.FALLIDA)
        self.assertEqual(robot.estado, "DISPONIBLE")
        self.assertEqual(bitacora.contar(Evento.ENTREGA_FALLIDA), 1)

    def test_el_reporte_incluye_los_eventos(self):
        bitacora = Bitacora()
        bitacora.registrar(Evento.MANTENIMIENTO, "RW a mantenimiento")
        self.assertIn("RW a mantenimiento", bitacora.generar_reporte())

    def test_flota_no_permite_ids_repetidos(self):
        flota = Flota()
        flota.registrar_robot(RobotRuedas("RW"))
        with self.assertRaises(ValueError):
            flota.registrar_robot(Dron("RW"))


if __name__ == "__main__":
    unittest.main()
