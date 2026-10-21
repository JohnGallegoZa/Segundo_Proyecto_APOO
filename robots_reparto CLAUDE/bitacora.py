from datetime import datetime


class Evento:
    """Un registro de la bitácora. Solo la Bitacora lo crea (composición)."""

    ASIGNACION = "ASIGNACION"
    PENDIENTE = "PENDIENTE"
    RECHAZO_CLIMA = "RECHAZO_CLIMA"
    ENTREGA_EXITOSA = "ENTREGA_EXITOSA"
    ENTREGA_FALLIDA = "ENTREGA_FALLIDA"
    MANTENIMIENTO = "MANTENIMIENTO"

    def __init__(self, tipo, detalle):
        self._fecha = datetime.now()
        self._tipo = tipo
        self._detalle = detalle

    @property
    def tipo(self):
        return self._tipo

    @property
    def detalle(self):
        return self._detalle

    def __str__(self):
        return f"[{self._fecha:%H:%M:%S}] {self._tipo:<16} {self._detalle}"


class Bitacora:
    def __init__(self):
        self._eventos = []

    def registrar(self, tipo, detalle):
        self._eventos.append(Evento(tipo, detalle))

    def contar(self, tipo):
        total = 0
        for evento in self._eventos:
            if evento.tipo == tipo:
                total += 1
        return total

    def cantidad_eventos(self):
        return len(self._eventos)

    def generar_reporte(self):
        lineas = ["===== BITÁCORA DE EVENTOS ====="]
        for evento in self._eventos:
            lineas.append(str(evento))
        lineas.append(f"Entregas exitosas: {self.contar(Evento.ENTREGA_EXITOSA)} | "
                      f"fallidas: {self.contar(Evento.ENTREGA_FALLIDA)} | "
                      f"mantenimientos: {self.contar(Evento.MANTENIMIENTO)}")
        return "\n".join(lineas)
