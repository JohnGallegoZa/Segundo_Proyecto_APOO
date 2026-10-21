from abc import ABC


class Robot(ABC):
    """Clase base abstracta de los robots. Las subclases cambian reglas y datos."""

    DISPONIBLE = "DISPONIBLE"
    OCUPADO = "OCUPADO"
    MANTENIMIENTO = "MANTENIMIENTO"

    _RESERVA_BATERIA = 10      # % que siempre debe sobrar después de una entrega
    _COSTO_BASE = 1000         # COP, costo fijo por entrega
    _COSTO_POR_KM = 0
    _CONSUMO_POR_KM = 0        # % de batería por km
    _ZONAS_PERMITIDAS = ()

    def __init__(self, id_robot, zona_actual, capacidad_kg, velocidad_kmh, bateria=100):
        if capacidad_kg <= 0 or velocidad_kmh <= 0:
            raise ValueError("Capacidad y velocidad deben ser mayores que 0")
        if not 0 <= bateria <= 100:
            raise ValueError("La batería debe estar entre 0 y 100")
        self._id_robot = id_robot
        self._zona_actual = zona_actual
        self._capacidad_kg = capacidad_kg
        self._velocidad_kmh = velocidad_kmh
        self._bateria = bateria
        self._estado = Robot.DISPONIBLE
        self._carga_actual = None

    # ---- Solo lectura desde afuera (no hay setters: se cambian con métodos) ----
    @property
    def id_robot(self):
        return self._id_robot

    @property
    def bateria(self):
        return self._bateria

    @property
    def zona_actual(self):
        return self._zona_actual

    @property
    def capacidad_kg(self):
        return self._capacidad_kg

    @property
    def estado(self):
        return self._estado

    @property
    def carga_actual(self):
        return self._carga_actual

    # ---- Características que cada subclase puede cambiar ----
    def es_aereo(self):
        return False

    def es_todoterreno(self):
        return False

    def tiene_refrigeracion(self):
        return False

    def nombre_tipo(self):
        return "Robot"

    # ---- Cálculos (polimórficos) ----
    def calcular_consumo(self, distancia_km):
        return self._CONSUMO_POR_KM * distancia_km

    def calcular_tiempo_min(self, distancia_km):
        return distancia_km / self._velocidad_kmh * 60

    def calcular_costo(self, solicitud):
        costo = self._COSTO_BASE + self._COSTO_POR_KM * solicitud.distancia_km
        return costo + solicitud.carga.recargo_costo()

    # ---- Reglas de compatibilidad ----
    def motivo_rechazo(self, solicitud):
        """Devuelve el motivo por el que NO puede hacer la entrega, o None si puede."""
        carga = solicitud.carga
        if self._estado != Robot.DISPONIBLE:
            return f"{self._id_robot} no está disponible ({self._estado})"
        if carga.peso_kg > self._capacidad_kg:
            return f"{self._id_robot}: la carga supera su capacidad de {self._capacidad_kg} kg"
        if solicitud.zona_destino not in self._ZONAS_PERMITIDAS:
            return f"{self._id_robot}: no puede acceder a la zona {solicitud.zona_destino}"
        if not carga.admite_robot(self):
            return f"{self._id_robot}: no es apto para carga tipo {carga.nombre_tipo()}"
        necesaria = self.calcular_consumo(solicitud.distancia_km) + self._RESERVA_BATERIA
        if self._bateria < necesaria:
            return f"{self._id_robot}: batería insuficiente ({self._bateria}% < {necesaria:.0f}%)"
        return None

    def puede_transportar(self, solicitud):
        return self.motivo_rechazo(solicitud) is None

    # ---- Operación del robot ----
    def reservar(self, solicitud):
        motivo = self.motivo_rechazo(solicitud)
        if motivo is not None:
            raise ValueError(motivo)
        self._estado = Robot.OCUPADO
        self._carga_actual = solicitud.carga

    def finalizar_entrega(self, solicitud):
        consumo = self.calcular_consumo(solicitud.distancia_km)
        self._bateria = max(0, self._bateria - consumo)
        self._zona_actual = solicitud.zona_destino
        self._carga_actual = None
        self._estado = Robot.DISPONIBLE

    def cancelar_entrega(self):
        self._carga_actual = None
        self._estado = Robot.DISPONIBLE

    def poner_en_mantenimiento(self):
        if self._estado == Robot.OCUPADO:
            raise ValueError("No se puede enviar a mantenimiento un robot ocupado")
        self._estado = Robot.MANTENIMIENTO

    def terminar_mantenimiento(self):
        self._bateria = 100
        self._estado = Robot.DISPONIBLE

    def __str__(self):
        return f"{self.nombre_tipo()} {self._id_robot} [{self._estado}, batería {self._bateria:.0f}%]"


class RobotRuedas(Robot):
    _COSTO_POR_KM = 1500
    _CONSUMO_POR_KM = 5
    _ZONAS_PERMITIDAS = ("EDIFICIOS", "CAFETERIA")

    def __init__(self, id_robot, zona_actual="EDIFICIOS", bateria=100):
        super().__init__(id_robot, zona_actual, capacidad_kg=15, velocidad_kmh=6, bateria=bateria)

    def tiene_refrigeracion(self):
        return True

    def nombre_tipo(self):
        return "Robot de ruedas"


class RobotOrugas(Robot):
    _COSTO_POR_KM = 2500
    _CONSUMO_POR_KM = 8
    _ZONAS_PERMITIDAS = ("EDIFICIOS", "ZONA_VERDE")

    def __init__(self, id_robot, zona_actual="ZONA_VERDE", bateria=100):
        super().__init__(id_robot, zona_actual, capacidad_kg=20, velocidad_kmh=4, bateria=bateria)

    def es_todoterreno(self):
        return True

    def nombre_tipo(self):
        return "Robot de orugas"


class Dron(Robot):
    _COSTO_POR_KM = 4000
    _CONSUMO_POR_KM = 15
    _ZONAS_PERMITIDAS = ("EDIFICIOS", "ZONA_VERDE", "AZOTEA")
    _MINUTOS_DESPEGUE_ATERRIZAJE = 3
    _SEGURO_VUELO = 1000

    def __init__(self, id_robot, zona_actual="AZOTEA", bateria=100):
        super().__init__(id_robot, zona_actual, capacidad_kg=2, velocidad_kmh=40, bateria=bateria)

    def es_aereo(self):
        return True

    def calcular_tiempo_min(self, distancia_km):
        # Además del vuelo, gasta tiempo despegando y aterrizando
        return super().calcular_tiempo_min(distancia_km) + self._MINUTOS_DESPEGUE_ATERRIZAJE

    def calcular_costo(self, solicitud):
        return super().calcular_costo(solicitud) + self._SEGURO_VUELO

    def nombre_tipo(self):
        return "Dron"
