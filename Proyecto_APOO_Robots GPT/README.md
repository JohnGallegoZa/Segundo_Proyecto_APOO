# Flota de robots universitarios — APOO

## Requisitos
Python 3.9 o superior, conexión a Internet solo para consultar clima real. No requiere instalar librerías externas.

## Ejecutar
Desde la carpeta del proyecto:

```bash
python main.py
python -m unittest -v
```

En PyCharm: abrir la carpeta, ejecutar `main.py` y después `test_robots.py`.

## Archivos
- `robots.py`: clases del sistema.
- `main.py`: demostración con tres solicitudes.
- `test_robots.py`: seis pruebas automáticas sin Internet.
- `uml.puml`: UML editable en PlantUML.
- `DOCUMENTACION.md`: fases 1–6, decisiones, defensa y limitaciones.

## Reglas elegidas
- Distancias en km, velocidades en km/h, tiempo en minutos y tarifas en COP por km.
- Consumo de batería en puntos porcentuales por km; reserva mínima de 10 puntos para autorizar.
- Viento máximo: 25 km/h; lluvia inferior a 60%.
- La temperatura de alimentos se registra, pero el sistema no incorpora sensor físico.
- Las zonas son etiquetas (`pavimento`, `verde`, `azotea`).
- La asignación usa el primer robot compatible registrado, no optimización de rutas.
- Si falla la API, no se autoriza el dron.
- El simulador sustituye el servicio real usando el mismo método.

## Nota importante
Es un prototipo académico, no un sistema de seguridad operacional. Las restricciones de carga y el consumo son supuestos del equipo que deben validarse con la universidad. La demostración completa requiere acceso a la API; las pruebas aisladas se verifican sin Internet.
