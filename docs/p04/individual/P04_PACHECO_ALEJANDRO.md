# P04 - Registro individual de aportacion y decisiones tecnicas

| | |
|---|---|
| Estudiante | Alejandro Pacheco Luna |
| Cuenta de GitHub | `zywoxxx` |
| Equipo | DSW-E01 |
| Proyecto | PR09 - Monitoreo de huerto o ambiente |
| Actividad | P04 - Arquitectura Web 3.0 (rubrica R04, criterio de aportacion individual) |
| Responsabilidad en el acta | Evidencia y documentacion |
| Fecha | 2026-09-29 |

## 1. Que aporte

Mi parte en el acta es evidencia y documentacion, y en este incremento tambien hice la integracion en el
repositorio. Lo que sigue se puede revisar en los commits de P04, que estan a nombre de mi cuenta.

| Aportacion | Donde se ve |
|---|---|
| Contrato de la API escrito antes que el codigo, con las diez operaciones y el cuerpo comun de error | `docs/p04/openapi.yaml` |
| Esqueleto de la API integrado en el repositorio, con el flujo principal funcionando | `api-spring/` |
| Esqueleto del cliente integrado, con acceso, captura e historial | `frontend-angular/` |
| Pruebas del contrato contra la API en marcha, validando cada respuesta contra su esquema | `scripts/pruebas_api.py`, `docs/p04/evidencia/txt/pruebas_api.txt` |
| Recorrido del cliente en navegador y capturas | `scripts/recorrido_angular.py`, `docs/p04/evidencia/img/` |
| Modulo `M04` del verificador y prueba con la base detenida | `scripts/verify-m04.sh`, `scripts/prueba_base_detenida.sh` |
| Diagramas de componentes, secuencia y despliegue | `scripts/diagramas_p04.py`, `docs/p04/diagramas/` |
| Documentos de arquitectura, modelo, endpoints, trazabilidad, verificacion e indice de evidencia | `docs/p04/*.md` |

## 2. Decision que justifico: Spring JDBC en lugar de JPA

Es la decision D3 del documento de arquitectura. La desarrollo aqui porque es la que mas afecta a lo que ya
teniamos hecho en P02 y P03.

### El problema

La API necesita leer sensores y lecturas y escribir una lectura con su alerta. La base ya existe: son siete tablas
creadas por `sql/01_schema.sql`, con datos, y las usan tambien las aplicaciones de P02 y P03. Habia que decidir como
llega Spring Boot a esas tablas.

### Las opciones

| Criterio | JDBC puro (como P02 y P03) | Spring JDBC (`NamedParameterJdbcTemplate`) | Spring Data JPA (Hibernate) |
|---|---|---|---|
| SQL | escrito a mano | escrito a mano | lo genera Hibernate; se puede escribir con `@Query` |
| Conexiones | abrir y cerrar en cada metodo | las administra Spring con un *pool* (HikariCP) | igual |
| Transacciones | `setAutoCommit(false)`, `commit`, `rollback` | `@Transactional` | `@Transactional` |
| Codigo por tabla | consulta + recorrer el `ResultSet` | consulta + `RowMapper` | clase `@Entity` + interfaz de repositorio |
| Relacion con el esquema | ninguna: usa lo que haya | ninguna: usa lo que haya | mapea clases a tablas; mal configurado puede intentar crear o alterar tablas |
| Reutiliza el SQL de P02 y P03 | si | si, casi sin cambios | no |
| Lo que hay que aprender | nada nuevo | poco | entidades, relaciones, carga perezosa, estados de una entidad |

### Por que Spring JDBC

1. **El SQL ya estaba probado.** Las consultas del historial y la insercion con `RETURNING id` venian de P02. Con
   Spring JDBC pasaron a la API cambiando los `?` por parametros con nombre.
2. **Las respuestas de la API no son tablas.** El esquema `Lectura` del contrato junta cinco tablas (`lectura`,
   `sensor`, `zona`, `variable`, `alerta`). Con SQL es un `SELECT` con joins y un `RowMapper`. Con JPA habria que
   mapear las cinco entidades con sus relaciones y luego convertirlas a otro objeto para la respuesta.
3. **La base es compartida.** Tres aplicaciones escriben en las mismas tablas. Prefiero que ninguna herramienta
   tenga la posibilidad de modificar el esquema; con JDBC eso no puede pasar, y ademas dejamos
   `spring.sql.init.mode=never`.
4. **Frente al JDBC puro, quita lo repetitivo.** En P03 cada repositorio abria su conexion y la transaccion de
   lectura mas alerta se manejaba a mano. Ahora la transaccion es una anotacion en `LecturaService.registrar` y el
   *pool* evita abrir una conexion por peticion, que era una limitacion anotada en P03.

### Lo que cuesta

- Los `RowMapper` se escriben a mano; si se agrega una columna hay que tocar la consulta y el mapeo.
- No hay paginacion automatica: `LecturaRepository` tiene una consulta para los datos y otra para el total.
- Si el modelo creciera mucho, o hubiera muchas pantallas de alta y edicion, JPA ahorraria mas de lo que cuesta.
  Con siete tablas y dos recursos implementados no es el caso.

### Como se comprobo que funciona

| Comprobacion | Evidencia |
|---|---|
| Una lectura valida suma exactamente una fila | casos 12 y 16 de `pruebas_api.txt` (conteo antes y despues) |
| Una lectura fuera de umbral suma una fila en `lectura` y una en `alerta` | casos 14 y 15 |
| Una lectura rechazada no deja nada | casos 17 a 25 |
| Con la base detenida no se guarda nada y la API responde 503 | `txt/14_base_detenida.txt` |
| El jar lleva `spring-jdbc` y el driver de PostgreSQL, y no lleva Hibernate | `txt/03_jar_contenido.txt` |

## 3. Un error que me toco diagnosticar

Al probar con la base detenida, `GET /api/sensores` respondia 503 como dice el contrato, pero `POST /api/lecturas`
respondia 500. La diferencia es que el registro es transaccional: Spring intenta abrir la transaccion antes de
entrar al metodo, y cuando no hay conexion lanza `CannotCreateTransactionException`, que pertenece a la jerarquia
de transacciones y no a la de acceso a datos. El manejador solo atendia `DataAccessException`, asi que el error
caia en el caso generico. Se corrigio agregando `TransactionException` al mismo manejador y una prueba
(`LecturaControllerTest.baseNoDisponible`) para que no vuelva a pasar. Lo que aprendi es que una consecuencia de
usar `@Transactional` es que aparece un tipo de fallo que con JDBC puro no existia por separado.

## 4. Lo que no hice o queda pendiente

- No implemente zonas, alertas ni anotaciones en la API; estan en el contrato y marcadas como PENDIENTE.
- No probe el despliegue en Linux ni la reproduccion en otra maquina.
- Este registro es solo mio. Las aportaciones de mis companeros las escribe cada uno en su archivo.
