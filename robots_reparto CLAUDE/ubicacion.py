class Ubicacion:
    """Punto geográfico (nombre + coordenadas). Se usa para consultar el clima."""

    def __init__(self, nombre, latitud, longitud):
        if not -90 <= latitud <= 90:
            raise ValueError("La latitud debe estar entre -90 y 90")
        if not -180 <= longitud <= 180:
            raise ValueError("La longitud debe estar entre -180 y 180")
        self._nombre = nombre
        self._latitud = latitud
        self._longitud = longitud

    @property
    def nombre(self):
        return self._nombre

    @property
    def latitud(self):
        return self._latitud

    @property
    def longitud(self):
        return self._longitud
