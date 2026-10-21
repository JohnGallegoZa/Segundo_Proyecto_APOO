class Carga:
    def __init__(self, tipo, peso, temperatura=None):
        if peso <= 0:
            raise ValueError('El peso debe ser positivo')
        self.tipo = tipo
        self.peso = peso
        self.temperatura = temperatura


class Solicitud:
    def __init__(self, codigo, carga, origen, destino, distancia, zona):
        if distancia <= 0:
            raise ValueError('La distancia debe ser positiva')
        self.codigo = codigo
        self.carga = carga
        self.origen = origen
        self.destino = destino
        self.distancia = distancia
        self.zona = zona
        self.estado = 'pendiente'
        self.robot = None
        self.tiempo = 0
        self.costo = 0


class Robot:
    def __init__(self, codigo, bateria, ubicacion, capacidad, velocidad, consumo, zonas, tipos, tarifa):
        if not 0 <= bateria <= 100 or capacidad <= 0 or velocidad <= 0 or consumo <= 0:
            raise ValueError('Datos del robot no válidos')
        self.codigo = codigo
        self.__bateria = bateria
        self.ubicacion = ubicacion
        self.capacidad = capacidad
        self.velocidad = velocidad
        self.consumo = consumo
        self.zonas = zonas
        self.tipos = tipos
        self.tarifa = tarifa
        self.carga_actual = None
        self.disponible = True

    def ver_bateria(self):
        return self.__bateria

    def cambiar_bateria(self, valor):
        if not 0 <= valor <= 100:
            raise ValueError('La batería debe estar entre 0 y 100')
        self.__bateria = valor

    def puede_transportar(self, carga):
        return carga.peso <= self.capacidad and carga.tipo in self.tipos

    def bateria_necesaria(self, distancia):
        return distancia * self.consumo + 10

    def puede_entregar(self, solicitud):
        return (self.disponible and self.carga_actual is None and
                self.puede_transportar(solicitud.carga) and
                solicitud.zona in self.zonas and
                self.ver_bateria() >= self.bateria_necesaria(solicitud.distancia))

    def calcular_tiempo(self, distancia):
        return distancia / self.velocidad * 60

    def calcular_costo(self, solicitud):
        extra = 1.5 if solicitud.carga.tipo in ('fragil', 'peligroso') else 1
        return round(solicitud.distancia * self.tarifa * extra, 2)

    def terminar_entrega(self, solicitud):
        self.cambiar_bateria(self.ver_bateria() - self.bateria_necesaria(solicitud.distancia) + 10)
        self.ubicacion = solicitud.destino
        self.carga_actual = None
        self.disponible = True


class RobotRuedas(Robot):
    def calcular_tiempo(self, distancia):
        return super().calcular_tiempo(distancia) + 3


class RobotOrugas(Robot):
    def calcular_tiempo(self, distancia):
        return super().calcular_tiempo(distancia) + 5


class Dron(Robot):
    def calcular_tiempo(self, distancia):
        return super().calcular_tiempo(distancia) + 2


class ServicioClima:
    def condiciones_favorables(self, ubicacion):
        import json
        from urllib.request import urlopen
        from urllib.parse import urlencode
        parametros = urlencode({'latitude': ubicacion[0], 'longitude': ubicacion[1],
                                'current': 'wind_speed_10m',
                                'hourly': 'precipitation_probability',
                                'forecast_days': 1, 'timezone': 'America/Bogota'})
        try:
            with urlopen('https://api.open-meteo.com/v1/forecast?' + parametros, timeout=8) as respuesta:
                datos = json.load(respuesta)
            viento = datos['current']['wind_speed_10m']
            hora = datos['current']['time'][:13]
            horas = datos['hourly']['time']
            indice = next(i for i, h in enumerate(horas) if h[:13] == hora)
            lluvia = datos['hourly']['precipitation_probability'][indice]
            return viento <= 25 and lluvia < 60
        except (Exception):
            return False  # Ante fallos de red o datos: no autorizar drones


class ClimaSimulado:
    def __init__(self, favorable):
        self.favorable = favorable

    def condiciones_favorables(self, ubicacion):
        return self.favorable


class Evento:
    def __init__(self, descripcion):
        self.descripcion = descripcion


class GestorFlota:
    def __init__(self, servicio_clima, ubicacion_campus):
        self.robots = []
        self.solicitudes = []
        self.__eventos = []  # Composición: eventos creados y administrados aquí
        self.servicio_clima = servicio_clima  # Asociación: servicio intercambiable
        self.ubicacion_campus = ubicacion_campus

    def registrar_robot(self, robot):
        if any(r.codigo == robot.codigo for r in self.robots):
            raise ValueError('Código de robot repetido')
        self.robots.append(robot)

    def registrar_solicitud(self, solicitud):
        if any(s.codigo == solicitud.codigo for s in self.solicitudes):
            raise ValueError('Código de solicitud repetido')
        self.solicitudes.append(solicitud)

    def registrar_evento(self, descripcion):
        self.__eventos.append(Evento(descripcion))

    def asignar(self, solicitud):
        if solicitud not in self.solicitudes or solicitud.estado != 'pendiente':
            return False
        for robot in self.robots:
            if not robot.puede_entregar(solicitud):
                continue
            if isinstance(robot, Dron) and not self.servicio_clima.condiciones_favorables(self.ubicacion_campus):
                continue
            robot.disponible = False
            robot.carga_actual = solicitud.carga
            solicitud.robot = robot
            solicitud.tiempo = round(robot.calcular_tiempo(solicitud.distancia), 2)
            solicitud.costo = robot.calcular_costo(solicitud)
            solicitud.estado = 'asignada'
            self.registrar_evento('Solicitud ' + solicitud.codigo + ' asignada a ' + robot.codigo)
            return True
        self.registrar_evento('Solicitud ' + solicitud.codigo + ' pendiente: sin robot compatible')
        return False

    def finalizar(self, solicitud, exito):
        if solicitud.estado != 'asignada':
            return False
        robot = solicitud.robot
        if exito:
            robot.terminar_entrega(solicitud)
            solicitud.estado = 'exitosa'
        else:
            robot.carga_actual = None
            robot.disponible = True
            solicitud.estado = 'fallida'
        self.registrar_evento('Entrega ' + solicitud.codigo + ': ' + solicitud.estado)
        return True

    def mantenimiento(self, robot):
        robot.disponible = False
        self.registrar_evento('Mantenimiento de ' + robot.codigo)

    def reporte(self):
        return [evento.descripcion for evento in self.__eventos]
