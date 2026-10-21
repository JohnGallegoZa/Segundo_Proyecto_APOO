import json
import urllib.request
from abc import ABC, abstractmethod


class ProveedorClima(ABC):
    """Contrato que debe cumplir cualquier fuente de clima.
    El asignador solo conoce esta clase, nunca la API real."""

    @abstractmethod
    def condiciones_favorables(self, ubicacion):
        """True si es seguro volar en esa ubicación."""


class ServicioClimaOpenMeteo(ProveedorClima):
    """Implementación real: consulta la API pública Open-Meteo (sin autenticación)."""

    URL_BASE = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, umbral_viento_kmh=25, umbral_lluvia_pct=50,
                 url_base=URL_BASE, timeout_seg=5):
        self._umbral_viento_kmh = umbral_viento_kmh
        self._umbral_lluvia_pct = umbral_lluvia_pct
        self._url_base = url_base
        self._timeout_seg = timeout_seg
        self._ultimo_error = None

    @property
    def ultimo_error(self):
        return self._ultimo_error

    def condiciones_favorables(self, ubicacion):
        try:
            datos = self._consultar(ubicacion)
            viento = datos["current"]["wind_speed_10m"]
            lluvia = datos["hourly"]["precipitation_probability"][0]
            self._ultimo_error = None
            return viento <= self._umbral_viento_kmh and lluvia < self._umbral_lluvia_pct
        except (OSError, ValueError, KeyError, IndexError, TypeError) as error:
            # Sin red, timeout, JSON roto o campos faltantes: por seguridad NO se autoriza el vuelo
            self._ultimo_error = str(error)
            return False

    def _consultar(self, ubicacion):
        url = (f"{self._url_base}?latitude={ubicacion.latitud}&longitude={ubicacion.longitud}"
               "&current=wind_speed_10m&hourly=precipitation_probability&forecast_hours=1")
        with urllib.request.urlopen(url, timeout=self._timeout_seg) as respuesta:
            return json.loads(respuesta.read().decode("utf-8"))


class ServicioClimaSimulado(ProveedorClima):
    """Implementación falsa para pruebas y demostraciones (sin internet)."""

    def __init__(self, favorable=True):
        self._favorable = favorable

    def establecer_favorable(self, favorable):
        self._favorable = favorable

    def condiciones_favorables(self, ubicacion):
        return self._favorable
