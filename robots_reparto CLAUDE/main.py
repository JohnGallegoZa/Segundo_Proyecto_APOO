"""Demostración. Uso:  python main.py          (clima simulado)
                      python main.py --real   (clima real con Open-Meteo)"""
import sys

from asignador import AsignadorEntregas
from bitacora import Bitacora
from carga import Alimento, Documento, Fragil, MaterialPeligroso
from clima import ServicioClimaOpenMeteo, ServicioClimaSimulado
from flota import Flota
from robot import Dron, RobotOrugas, RobotRuedas
from solicitud import Solicitud
from ubicacion import Ubicacion


def main():
    campus = Ubicacion("Campus universitario", 6.2672, -75.5688)  # ajustar al campus real

    if "--real" in sys.argv:
        clima = ServicioClimaOpenMeteo(umbral_viento_kmh=25, umbral_lluvia_pct=50)
    else:
        clima = ServicioClimaSimulado(favorable=True)

    flota = Flota()
    flota.registrar_robot(RobotRuedas("RW-01"))
    flota.registrar_robot(RobotOrugas("RO-01"))
    flota.registrar_robot(Dron("DR-01"))

    bitacora = Bitacora()
    asignador = AsignadorEntregas(flota, clima, bitacora, campus)

    solicitudes = [
        Solicitud(1, "Decanatura", Documento("Actas", 0.5), "AZOTEA", 0.4),
        Solicitud(2, "Cafetería", Alimento("Almuerzos fríos", 3, requiere_frio=True), "EDIFICIOS", 0.8),
        Solicitud(3, "Laboratorio", MaterialPeligroso("Ácido diluido", 2, nivel_riesgo=2), "EDIFICIOS", 0.6),
        Solicitud(4, "Biblioteca", Fragil("Microscopio", 4), "ZONA_VERDE", 0.9),
    ]

    for solicitud in solicitudes:
        robot = asignador.asignar(solicitud)
        if robot is not None:
            asignador.completar_entrega(solicitud, exito=True)

    print(bitacora.generar_reporte())
    print()
    for robot in flota.obtener_robots():
        print(robot)


if __name__ == "__main__":
    main()
