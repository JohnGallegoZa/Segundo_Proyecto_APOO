# Sistema de gestión de flota de robots de reparto universitario

Práctica de Programación Orientada a Objetos. Python 3.9+ (solo librería estándar, no hay que instalar nada).

## Ejecución
```bash
python main.py          # demo con clima simulado (no necesita internet)
python main.py --real   # demo con clima real (Open-Meteo, necesita internet)
python -m unittest -v   # pruebas
```

## Archivos
| Archivo | Contenido |
|---|---|
| `carga.py` | `Carga` (abstracta) + `Documento`, `Alimento`, `Fragil`, `MaterialPeligroso` |
| `robot.py` | `Robot` (abstracta) + `RobotRuedas`, `RobotOrugas`, `Dron` |
| `solicitud.py` | `Solicitud` |
| `clima.py` | `ProveedorClima` (abstracta) + `ServicioClimaOpenMeteo`, `ServicioClimaSimulado` |
| `asignador.py` | `AsignadorEntregas` (reglas de asignación) |
| `flota.py`, `bitacora.py`, `ubicacion.py` | `Flota`, `Bitacora` + `Evento`, `Ubicacion` |
| `uml.mmd` | Diagrama de clases (Mermaid) |
| `test_sistema.py` | Pruebas de polimorfismo, encapsulamiento, clima y flujo |

## Cambiar de proveedor de clima
En `main.py` solo cambia la línea que crea `clima`. `AsignadorEntregas` no se modifica porque solo conoce `ProveedorClima`.

## Anexo: Cambios de diseño (UML Fase 3 -> código)
| Qué cambió | Por qué | Qué se aprendió |
|---|---|---|
| (Escribir aquí cada diferencia real entre su UML y el código. Si no hay ninguna, indicar "Sin diferencias respecto al UML v1.0".) | | |
