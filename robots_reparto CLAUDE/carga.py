from abc import ABC, abstractmethod


class Carga(ABC):
    """Clase base abstracta de todo lo que un robot puede transportar."""

    def __init__(self, descripcion, peso_kg):
        if peso_kg <= 0:
            raise ValueError("El peso de la carga debe ser mayor que 0")
        self._descripcion = descripcion
        self._peso_kg = peso_kg

    @property
    def descripcion(self):
        return self._descripcion

    @property
    def peso_kg(self):
        return self._peso_kg

    @abstractmethod
    def recargo_costo(self):
        """Dinero extra que cuesta transportar este tipo de carga."""

    @abstractmethod
    def admite_robot(self, robot):
        """True si este tipo de carga puede viajar en ese robot."""

    @abstractmethod
    def nombre_tipo(self):
        """Nombre legible del tipo de carga (para reportes)."""


class Documento(Carga):
    def recargo_costo(self):
        return 0

    def admite_robot(self, robot):
        return True  # un documento puede ir en cualquier robot

    def nombre_tipo(self):
        return "Documento"


class Alimento(Carga):
    def __init__(self, descripcion, peso_kg, requiere_frio=False):
        super().__init__(descripcion, peso_kg)
        self._requiere_frio = requiere_frio

    @property
    def requiere_frio(self):
        return self._requiere_frio

    def recargo_costo(self):
        return 2000 if self._requiere_frio else 500

    def admite_robot(self, robot):
        # Si necesita frío, solo viaja en robots con refrigeración
        if self._requiere_frio:
            return robot.tiene_refrigeracion()
        return True

    def nombre_tipo(self):
        return "Alimento"


class Fragil(Carga):
    def recargo_costo(self):
        return 1500

    def admite_robot(self, robot):
        # Las orugas vibran demasiado para cargas frágiles
        return not robot.es_todoterreno()

    def nombre_tipo(self):
        return "Frágil"


class MaterialPeligroso(Carga):
    PESO_MAXIMO_KG = 5

    def __init__(self, descripcion, peso_kg, nivel_riesgo):
        super().__init__(descripcion, peso_kg)
        if peso_kg > self.PESO_MAXIMO_KG:
            raise ValueError("El material peligroso no puede pesar más de 5 kg")
        if nivel_riesgo not in (1, 2, 3):
            raise ValueError("El nivel de riesgo debe ser 1, 2 o 3")
        self._nivel_riesgo = nivel_riesgo

    @property
    def nivel_riesgo(self):
        return self._nivel_riesgo

    def recargo_costo(self):
        return 5000 + 1000 * self._nivel_riesgo

    def admite_robot(self, robot):
        # Solo robots terrestres estables: ni drones ni orugas
        return not robot.es_aereo() and not robot.es_todoterreno()

    def nombre_tipo(self):
        return "Material peligroso"
