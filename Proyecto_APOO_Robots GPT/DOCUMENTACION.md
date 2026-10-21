# Práctica APOO — Sistema de gestión de una flota de robots de reparto universitario

**Propuesta académica para adaptar y defender.** Los supuestos, la reflexión personal y el historial de commits deben corresponder a las decisiones y trabajo reales del equipo.

## Fase 1 — Análisis del problema (días 1–2)

### Requisitos funcionales
1. Registrar robots y sus características.
2. Consultar batería y ubicación.
3. Registrar solicitudes de entrega.
4. Diferenciar cargas de documentos, alimentos, frágiles y peligrosas.
5. Validar peso, tipo permitido y zona accesible.
6. Validar batería suficiente antes de asignar.
7. Calcular costo estimado de entrega.
8. Calcular tiempo estimado según subtipo de robot.
9. Consultar el clima mediante una API antes de asignar drones.
10. Dejar pendiente una solicitud sin robot compatible.
11. Finalizar entregas como exitosas o fallidas.
12. Registrar asignaciones, fallos y mantenimiento en bitácora.

### Reglas de negocio
- Una solicitud solo puede asignarse si está pendiente y registrada.
- Un robot no puede llevar más de su capacidad máxima.
- Un robot no puede transportar tipos de carga fuera de su lista permitida.
- La zona de destino debe figurar en las zonas autorizadas del robot.
- Debe quedar una reserva de batería de al menos 10 puntos antes de la entrega.
- Un robot ocupado o en mantenimiento no recibe otra solicitud.
- Un dron no se asigna con viento superior a 25 km/h o lluvia de 60% o más.
- Si falla la consulta meteorológica, la asignación del dron se rechaza por precaución.
- Los tipos frágil y peligroso incrementan el costo en un factor de 1,5.
- El sistema intenta otros robots cuando uno no es compatible.

### Supuestos propios (validar con el cliente)
1. Las distancias llegan calculadas en kilómetros; no se implementa cartografía.
2. El campus se representa por coordenadas configurables y zonas nominales.
3. El viento límite es 25 km/h y la probabilidad de lluvia límite es 60%.
4. El consumo es un porcentaje fijo de batería por kilómetro y se reserva 10% adicional.
5. Se registra la temperatura requerida del alimento, pero no se simula un refrigerador real.
6. Se elige el primer robot compatible; no se garantiza el menor costo.

### Preguntas al cliente
- ¿Cuáles son las capacidades, velocidades y autonomías certificadas de cada robot?
- ¿Qué zonas están prohibidas para drones y materiales peligrosos?
- ¿Debe verificarse la temperatura con sensores o basta registrarla?
- ¿Cómo se obtiene la distancia real de cada trayecto?
- ¿Se prioriza rapidez, costo o nivel de batería?
- ¿Cómo se registran accidentes, entregas canceladas y carga no recuperada?

**Entregable parcial 1:** usar exclusivamente esta sección como documento de análisis; no anticipar clases en la entrega de fase 1.

## Fase 2 — Identificación de clases y responsabilidades (días 3–4)

### Técnica de sustantivos y verbos
Sustantivos extraídos del problema: universidad, robot, batería, ubicación, carga, solicitud, dron, ruedas, orugas, clima, evento, flota, zona, entrega. Verbos: registrar, transportar, asignar, calcular, consultar, autorizar, rechazar, finalizar y reportar.

Transformación: robot -> `Robot` y tres subtipos; carga -> `Carga`; solicitud -> `Solicitud`; asignar/registrar -> `GestorFlota`; consultar clima -> `ServicioClima`; reportar evento -> `Evento`. `ClimaSimulado` se agrega para verificar sustitución del proveedor. Batería, zona y ubicación se mantienen como atributos simples, no como clases adicionales.

### Tabla CRC (Clase — Responsabilidades — Colaboradores)
| Clase | Responsabilidades | Colaboradores |
|---|---|---|
| Robot | validar carga, batería y zona; calcular costo y tiempo | Carga, Solicitud |
| RobotRuedas | tiempo propio con maniobras | Robot |
| RobotOrugas | tiempo propio en terrenos difíciles | Robot |
| Dron | tiempo propio de vuelo | Robot |
| Carga | conservar tipo, peso y temperatura | Solicitud |
| Solicitud | conservar estado y detalles de entrega | Carga, Robot |
| GestorFlota | registrar, asignar, finalizar, reportar | Robot, Solicitud, Evento, ServicioClima |
| Evento | conservar descripción de un evento | GestorFlota |
| ServicioClima | consultar API y evaluar umbrales | GestorFlota |
| ClimaSimulado | devolver clima controlado en pruebas | GestorFlota |

### Elementos excluidos
No se modelan edificios, GPS, rutas, sensores físicos, autenticación, pagos ni bases de datos: añadirían complejidad no necesaria para demostrar el núcleo POO. El tipo de carga se expresa mediante un atributo y reglas simples, en lugar de cuatro clases adicionales.

## Fase 3 — Diseño UML (días 5–7)

Abrir `uml.puml` en PlantUML para consultar y editar el diagrama de clases. Contiene atributos públicos (`+`), batería y eventos privados (`-`), métodos y multiplicidades.

- Herencia: `Robot` es padre de `RobotRuedas`, `RobotOrugas` y `Dron`.
- Polimorfismo: los tres subtipos sobrescriben `calcular_tiempo()`.
- Composición: `GestorFlota` crea y conserva sus propios objetos `Evento`; no se registran por fuera del gestor.
- Agregación: `GestorFlota` recibe objetos `Robot` y `Solicitud` creados externamente.
- Asociación: el gestor recibe un servicio meteorológico externo intercambiable.
- Asociación: una `Solicitud` conserva una `Carga` y opcionalmente el robot asignado.

**Changelog propuesto:** v0.1: identificación de entidades y verbos. v0.2: consolidación de clases de carga en `Carga`. v0.3: inclusión de herencia de robots y eventos compuestos. v1.0: aislamiento de clima y multiplicidades. Este changelog es una propuesta de evolución, no evidencia de commits realizados.

## Fase 4 — Justificación de decisiones (día 8)

| Decisión | Alternativas consideradas | Elección y motivo | Principio |
|---|---|---|---|
| Tipos de robot | una sola clase con condicionales / herencia | Herencia: tiempo especializado por subtipo sin condicionales en el gestor | Abierto/cerrado, polimorfismo |
| Gestión de solicitudes | asignar dentro de Robot / gestor separado | Gestor: concentra la coordinación, robots conservan sus reglas propias | Responsabilidad única, cohesión |
| Cargas | cuatro subclases / clase con tipo | Una clase: menor complejidad; nuevas restricciones exigirían ampliar validaciones | Simplicidad y cohesión |
| Bitácora | lista de cadenas / objetos Evento creados por gestor | Evento propio: composición real, posibilidad de ampliar registros | Composición, responsabilidad única |
| Clima | HTTP dentro del gestor / servicio dedicado | Servicio separado: cambia proveedor sin tocar asignación | Inversión de dependencias por contrato de método, bajo acoplamiento |
| Selección | optimizar rutas / primer compatible | Primer compatible: verificable con lógica básica | Simplicidad, responsabilidad única |
| Fallo de API | permitir vuelo / dejar pendiente | Pendiente: evita aprobar vuelo sin información meteorológica | Diseño defensivo |

**Sustitución de clima:** tanto `ServicioClima` como `ClimaSimulado` exponen `condiciones_favorables(ubicacion)`. El gestor solo invoca ese método. Es una interfaz informal basada en comportamiento común (duck typing); no requiere herencia ni bibliotecas especiales.

## Fase 5 — Implementación (días 9–12)

### Correspondencia UML y código
Las clases, atributos, métodos y asociaciones documentados en `uml.puml` corresponden al archivo `robots.py`. `main.py` crea instancias y `test_robots.py` verifica reglas sin alterar el modelo.

### Pasos de ejecución
1. Abrir el proyecto en PyCharm o terminal.
2. Ejecutar `python main.py` para tres solicitudes (alimentos, carga peligrosa y documentos para azotea).
3. Ejecutar `python -m unittest -v` para seis pruebas automáticas.
4. Para simular el clima, reemplazar al construir el gestor `ServicioClima()` por `ClimaSimulado(True)` o `ClimaSimulado(False)`; importar la clase desde `robots`.

### Pruebas previstas
1. Clima desfavorable deja el dron sin asignación.
2. Servicio simulado favorable permite asignar el mismo dron.
3. Batería inválida dispara `ValueError`.
4. Subtipos producen distintos tiempos para la misma distancia.
5. Exceso de peso impide transporte.
6. Una entrega asignada puede terminar exitosamente.

### Propuesta de commits reales, en orden
- `git commit -m "Crear clases Carga y Solicitud"`
- `git commit -m "Implementar robots y reglas de bateria"`
- `git commit -m "Agregar gestor de flota y bitacora"`
- `git commit -m "Integrar servicio de clima intercambiable"`
- `git commit -m "Agregar pruebas y documentacion UML"`

Realizar cada commit cuando efectivamente se complete el cambio; no crear historial ficticio.

### Anexo: cambios de diseño
En esta propuesta inicial no se conocen desviaciones posteriores al UML v1.0. Si se cambia código o diagrama, documentar fecha, elemento anterior, elemento nuevo, motivo y aprendizaje, y actualizar el otro artefacto.

### Límites conocidos
- La API se consulta para el momento actual; no pronostica la hora exacta de una entrega futura.
- La batería se descuenta al completar entregas exitosas; no se calcula consumo parcial de fallos.
- No hay persistencia: al cerrar el programa se pierden los registros.
- La temperatura alimentaria se almacena, pero no se valida con sensores.
- El tiempo estimado no incluye obstáculos ni rutas reales.
- El registro de mantenimiento no implementa finalización de mantenimiento.

## Fase 6 — Reflexión crítica individual (días 13–14)

**Guía para redactar personalmente, no entregar como experiencia vivida sin verificar:**

1. **Qué cambiaría:** evaluar si convendría modelar clases separadas para alimentos y materiales peligrosos, pues tienen controles específicos que hoy se representan con etiquetas.
2. **Principio más difícil:** analizar si la composición fue más difícil que la herencia; explicar por qué `Evento` se crea dentro del gestor mientras los robots llegan desde fuera.
3. **Cambios futuros:** un nuevo robot puede heredar de `Robot` y redefinir `calcular_tiempo`; un nuevo tipo de carga puede requerir cambios en validaciones; un proveedor de clima nuevo solo debe conservar el método esperado.
4. **Autocrítica:** indicar un error real cometido por el integrante, cómo lo detectó y cómo lo corrigió.

Cada estudiante debe escribir su propia reflexión con experiencias verificables y diferentes de sus compañeros.

## Preparación de la defensa oral

**¿Dónde está el polimorfismo?** `robot.calcular_tiempo(distancia)` usa el método del subtipo real: ruedas agrega 3 minutos, orugas 5 y dron 2.

**¿Dónde está el encapsulamiento?** `Robot.__bateria` no se cambia directamente desde el gestor; `cambiar_bateria()` verifica el rango de 0 a 100.

**¿Por qué no hereda GestorFlota de ServicioClima?** Un gestor usa un servicio de clima, pero no es un servicio meteorológico.

**¿Qué pasa si la API falla?** `condiciones_favorables()` devuelve `False` y el gestor intenta otro robot o deja pendiente la solicitud.

**¿Cómo cambiar el proveedor?** Crear otra clase con `condiciones_favorables(ubicacion)` y pasarla al constructor de `GestorFlota`.

**¿Cómo agregar un nuevo robot?** Crear una subclase de `Robot`, por ejemplo `RobotAnfibio`, y sobrescribir `calcular_tiempo`; después registrarlo con sus zonas y cargas permitidas.

**¿Por qué el UML debe coincidir con el código?** El UML documenta el contrato estructural y permite comprobar que la implementación respeta las decisiones acordadas.
