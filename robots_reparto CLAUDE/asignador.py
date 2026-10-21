from bitacora import Evento
from solicitud import Solicitud


class AsignadorEntregas:
    """Decide qué robot hace cada entrega. Recibe sus dependencias por el constructor."""

    _BATERIA_MINIMA_OPERAR = 20  # por debajo de esto el robot va a mantenimiento

    def __init__(self, flota, proveedor_clima, bitacora, ubicacion_campus):
        self._flota = flota
        self._clima = proveedor_clima      # puede ser real o simulado: no importa
        self._bitacora = bitacora
        self._ubicacion_campus = ubicacion_campus

    def asignar(self, solicitud):
        """Devuelve el robot asignado o None si la solicitud queda pendiente."""
        mejor_robot = None
        mejor_costo = None
        clima_favorable = None  # se consulta una sola vez y solo si hace falta

        for robot in self._flota.obtener_robots():
            if not robot.puede_transportar(solicitud):
                continue

            if robot.es_aereo():
                if clima_favorable is None:
                    clima_favorable = self._clima.condiciones_favorables(self._ubicacion_campus)
                if not clima_favorable:
                    self._bitacora.registrar(
                        Evento.RECHAZO_CLIMA,
                        f"{robot.id_robot} descartado para solicitud {solicitud.id_solicitud}: clima no favorable")
                    continue

            costo = robot.calcular_costo(solicitud)
            if mejor_robot is None or costo < mejor_costo:
                mejor_robot = robot
                mejor_costo = costo

        if mejor_robot is None:
            solicitud.marcar_pendiente()
            self._bitacora.registrar(
                Evento.PENDIENTE, f"Solicitud {solicitud.id_solicitud} sin robot disponible: queda pendiente")
            return None

        mejor_robot.reservar(solicitud)
        solicitud.asignar_a(mejor_robot)
        tiempo = mejor_robot.calcular_tiempo_min(solicitud.distancia_km)
        self._bitacora.registrar(
            Evento.ASIGNACION,
            f"Solicitud {solicitud.id_solicitud} -> {mejor_robot.id_robot} "
            f"(costo ${mejor_costo:,.0f}, tiempo {tiempo:.1f} min)")
        return mejor_robot

    def completar_entrega(self, solicitud, exito=True):
        robot = solicitud.robot_asignado
        if solicitud.estado != Solicitud.ASIGNADA or robot is None:
            raise ValueError("Solo se puede completar una solicitud que esté asignada")

        if exito:
            robot.finalizar_entrega(solicitud)
            solicitud.marcar_entregada()
            self._bitacora.registrar(
                Evento.ENTREGA_EXITOSA, f"Solicitud {solicitud.id_solicitud} entregada por {robot.id_robot}")
            if robot.bateria < self._BATERIA_MINIMA_OPERAR:
                robot.poner_en_mantenimiento()
                self._bitacora.registrar(
                    Evento.MANTENIMIENTO, f"{robot.id_robot} a mantenimiento (batería {robot.bateria:.0f}%)")
        else:
            robot.cancelar_entrega()
            solicitud.marcar_fallida()
            self._bitacora.registrar(
                Evento.ENTREGA_FALLIDA, f"Solicitud {solicitud.id_solicitud} falló con {robot.id_robot}")
