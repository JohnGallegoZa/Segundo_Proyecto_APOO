class Solicitud:
    """Pedido de entrega hecho a la universidad."""

    PENDIENTE = "PENDIENTE"
    ASIGNADA = "ASIGNADA"
    ENTREGADA = "ENTREGADA"
    FALLIDA = "FALLIDA"

    ZONAS_VALIDAS = ("EDIFICIOS", "CAFETERIA", "ZONA_VERDE", "AZOTEA")

    def __init__(self, id_solicitud, solicitante, carga, zona_destino, distancia_km):
        if zona_destino not in Solicitud.ZONAS_VALIDAS:
            raise ValueError(f"Zona desconocida: {zona_destino}")
        if distancia_km <= 0:
            raise ValueError("La distancia debe ser mayor que 0")
        self._id_solicitud = id_solicitud
        self._solicitante = solicitante
        self._carga = carga
        self._zona_destino = zona_destino
        self._distancia_km = distancia_km
        self._estado = Solicitud.PENDIENTE
        self._robot_asignado = None

    @property
    def id_solicitud(self):
        return self._id_solicitud

    @property
    def solicitante(self):
        return self._solicitante

    @property
    def carga(self):
        return self._carga

    @property
    def zona_destino(self):
        return self._zona_destino

    @property
    def distancia_km(self):
        return self._distancia_km

    @property
    def estado(self):
        return self._estado

    @property
    def robot_asignado(self):
        return self._robot_asignado

    def asignar_a(self, robot):
        self._robot_asignado = robot
        self._estado = Solicitud.ASIGNADA

    def marcar_pendiente(self):
        self._robot_asignado = None
        self._estado = Solicitud.PENDIENTE

    def marcar_entregada(self):
        self._estado = Solicitud.ENTREGADA

    def marcar_fallida(self):
        self._estado = Solicitud.FALLIDA
