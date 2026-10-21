from robots import Carga, Solicitud, RobotRuedas, RobotOrugas, Dron, ServicioClima, GestorFlota

# Coordenadas aproximadas del campus, configurables por la universidad.
gestor = GestorFlota(ServicioClima(), (6.23, -75.61))
gestor.registrar_robot(RobotRuedas('R1', 90, 'Biblioteca', 8, 6, 5,
                                  ['pavimento'], ['documentos', 'alimentos', 'fragil'], 3000))
gestor.registrar_robot(RobotOrugas('O1', 85, 'Laboratorio', 12, 3, 8,
                                  ['pavimento', 'verde'], ['documentos', 'fragil', 'peligroso'], 4500))
gestor.registrar_robot(Dron('D1', 100, 'Azotea', 2, 20, 12,
                            ['azotea'], ['documentos'], 6000))

solicitudes = [
    Solicitud('S1', Carga('alimentos', 2, 5), 'Cafetería', 'Biblioteca', 1, 'pavimento'),
    Solicitud('S2', Carga('peligroso', 3), 'Laboratorio', 'Bloque B', 1.5, 'verde'),
    Solicitud('S3', Carga('documentos', 1), 'Rectoría', 'Azotea', 2, 'azotea'),
]
for solicitud in solicitudes:
    gestor.registrar_solicitud(solicitud)
    if gestor.asignar(solicitud):
        print(solicitud.codigo, solicitud.robot.codigo, 'minutos:', solicitud.tiempo,
              'costo COP:', solicitud.costo)
        gestor.finalizar(solicitud, True)
    else:
        print(solicitud.codigo, 'PENDIENTE')
print('\nBITÁCORA')
for evento in gestor.reporte():
    print('-', evento)
