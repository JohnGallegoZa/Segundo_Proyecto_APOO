class Flota:
    """Conjunto de robots registrados. Los robots existen independientemente de la flota."""

    def __init__(self):
        self._robots = []

    def registrar_robot(self, robot):
        if self.buscar_por_id(robot.id_robot) is not None:
            raise ValueError(f"Ya existe un robot con id {robot.id_robot}")
        self._robots.append(robot)

    def buscar_por_id(self, id_robot):
        for robot in self._robots:
            if robot.id_robot == id_robot:
                return robot
        return None

    def obtener_robots(self):
        return list(self._robots)  # copia: nadie de afuera modifica la lista interna

    def cantidad(self):
        return len(self._robots)
