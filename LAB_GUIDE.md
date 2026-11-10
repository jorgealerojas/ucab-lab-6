# Guia del laboratorio: operar un portal bajo demanda

**Unidad:** VI — Gestion y Operaciones  
**Semana:** 1 de 2 — Operar y escalar  
**Duracion:** 1 h 45 min (105 minutos)  
**Modalidad:** individual  
**Region obligatoria:** US East (Ohio), `us-east-2`

## Reto

Un portal universitario recibe trafico moderado durante el semestre y un pico durante las inscripciones. Debe responder sin mantener permanentemente la capacidad maxima.

Desplegara una version inicial, medira su comportamiento, provocara demanda y utilizara evidencia de AWS para explicar si hubo escalabilidad, elasticidad y operacion observable.

## Reglas de operacion

- Use solamente `us-east-2`.
- Mantenga el tipo de instancia y los limites del Auto Scaling Group.
- No cambie ni escriba manualmente el identificador aleatorio.
- No exceda los limites que impone el generador de carga.
- No capture credenciales, cookies, identificadores de cuenta ni URLs sensibles.
- Elimine el stack mediante el script de limpieza al finalizar.

## Evidencias durante la practica

Tome las capturas necesarias para demostrar cada paso importante. Cada captura debe incluir una explicacion breve de que se observa y por que es relevante. No es necesario capturar cada comando si una sola evidencia demuestra el hito completo.

Hitos minimos:

1. Diagnostico aprobado.
2. Stack en `CREATE_COMPLETE` y arquitectura identificada.
3. Target saludable y respuesta del portal.
4. Resultado de carga base.
5. Carga pico y capturas obligatorias de las actividades de scale-out y scale-in.
6. Dashboard con solicitudes, p95, capacidad y salud.
7. Muestra de un log de acceso.
8. Verificacion integral y limpieza final.

## 0–10 min — Definir el servicio que se desea operar

Antes de abrir AWS, escriba en su informe una hipotesis con esta estructura:

| Elemento | Hipotesis inicial |
|---|---|
| Necesidad empresarial | |
| SLI de disponibilidad | Porcentaje de solicitudes HTTP exitosas |
| SLI de rendimiento | Latencia p95 |
| SLO durante el pico | |
| Senal que deberia provocar scale-out | |
| Riesgo de escalar sin limite | |

Elija un SLO numerico para tasa de exito y p95. Al final debera contrastarlo con sus mediciones.

## 10–22 min — Preparar y comprobar el entorno

### 1. Seleccionar Ohio y abrir CloudShell

En la consola de AWS seleccione **US East (Ohio)**. Abra CloudShell y compruebe que la terminal pertenece a esa region.

### 2. Definir la region principal

Este comando indica a AWS CLI donde debe realizar las operaciones. No crea recursos.

```bash
export AWS_REGION=us-east-2
```

No produce salida. El prompt vuelve inmediatamente.

### 3. Definir la region predeterminada

Algunas herramientas consultan `AWS_DEFAULT_REGION`. Se define el mismo valor para evitar que dos comandos utilicen regiones diferentes.

```bash
export AWS_DEFAULT_REGION=us-east-2
```

Tampoco produce salida.

### 4. Comprobar la configuracion efectiva

La consulta muestra de donde provienen las credenciales y la region. Es una operacion de lectura.

```bash
aws configure list
```

La fila `region` debe mostrar `us-east-2`. Las credenciales aparecen ocultas; no las incluya en el informe.

### 5. Descargar el repositorio

`git clone` copia la aplicacion, IaC, scripts, pruebas y guia en el almacenamiento de CloudShell. Todavia no crea recursos AWS.

```bash
git clone https://github.com/jorgealerojas/ucab-lab-6.git
```

La salida comienza con `Cloning into 'ucab-lab-6'` y termina sin errores.

### 6. Entrar en el repositorio

Este cambio de directorio hace que los siguientes comandos utilicen los archivos descargados.

```bash
cd ucab-lab-6
```

No produce salida.

### 7. Ejecutar el diagnostico

El diagnostico comprueba herramientas, credenciales, region, sintaxis de CloudFormation y pruebas unitarias. Las comprobaciones locales no crean infraestructura.

```bash
./scripts/doctor.sh
```

La salida debe contener varias lineas `OK`, las pruebas deben finalizar correctamente y la ultima linea debe ser:

```text
DIAGNOSTICO APROBADO: entorno listo en us-east-2
```

No continue si aparece `ERROR` o una prueba falla. Consulte `TROUBLESHOOTING.md`.

## 22–35 min — Crear e identificar la arquitectura

### 8. Crear un stack nuevo

El script genera 16 digitos hexadecimales aleatorios, solicita a CloudFormation un stack nuevo y guarda el identificador aceptado. AWS crea la VPC, dos subredes, ALB, Target Group, Launch Template, Auto Scaling Group, dashboard, alarma y bucket de logs.

La operacion puede tardar entre 4 y 8 minutos. La espera es intencional: el script no informa exito hasta que CloudFormation confirma `CREATE_COMPLETE`.

```bash
./scripts/deploy-lab.sh
```

Anote el valor de `Identificador generado`. La salida final debe tener esta forma:

```text
LABORATORIO LISTO: ucab-lab-6-<16 digitos hexadecimales>
Portal: http://<dns-del-alb>
Siguiente paso: ./scripts/status.sh
```

Mientras espera, abra **CloudFormation → Stacks → Events**. Localice el identificador exacto y observe el orden de creacion. No inicie otra ejecucion del script.

### 9. Comprobar capacidad y salud

El script consulta el Auto Scaling Group y el Target Group. No modifica capacidad.

```bash
./scripts/status.sh
```

Debe mostrar minimo 1, deseado 1, maximo 3 y al menos una instancia `InService`. El target debe aparecer como `healthy`. Si aun dice `initial`, espere un minuto y repita solamente este comando.

## 35–48 min — Mision de descubrimiento

En esta parte no se entrega una secuencia de comandos. Utilice la consola, la ayuda de AWS CLI o la documentacion oficial para localizar:

1. El output `PortalUrl` de CloudFormation.
2. El nombre del Auto Scaling Group.
3. Las politicas de scale-out y scale-in y sus umbrales.
4. La metrica que alimenta esa politica.
5. La capacidad minima, deseada y maxima.
6. El dashboard y la alarma de latencia.

Registre donde encontro cada dato y explique para que sirve.

### 10. Recuperar la URL para las pruebas

Despues de completar la busqueda, el siguiente script recupera `PortalUrl` y permite comprobar el valor sin copiarlo manualmente.

```bash
LAB_URL="$(./scripts/get-url.sh)"
```

La asignacion no muestra salida.

### 11. Visualizar la URL guardada

`echo` permite verificar que la variable contiene una URL HTTP del balanceador antes de usarla.

```bash
echo "$LAB_URL"
```

Debe mostrar una sola URL que comienza por `http://`.

### 12. Solicitar una respuesta

`curl` realiza una solicitud HTTP y `python3 -m json.tool` presenta el JSON de manera legible. La tuberia transforma la salida; no realiza solicitudes adicionales.

```bash
curl --fail --silent --show-error "$LAB_URL/" | python3 -m json.tool
```

La respuesta debe incluir `service`, `version`, `instance`, `request_id` y `timestamp`. El campo `instance` permite reconocer que replica atendio la solicitud.

## 48–68 min — Medir y provocar elasticidad

### 13. Consultar las opciones del generador

La ayuda explica los parametros y sus limites sin enviar trafico.

```bash
python3 scripts/load_test.py --help
```

Revise especialmente `duration`, `concurrency` y `work-ms`.

### 14. Establecer una linea base

Esta ejecucion mantiene cuatro solicitudes concurrentes durante 30 segundos. Cada solicitud pide 25 ms de trabajo simulado. El objetivo es medir el servicio antes del pico.

```bash
python3 scripts/load_test.py --url "$LAB_URL" --duration 30 --concurrency 4 --work-ms 25
```

La salida es un JSON con solicitudes totales, errores, tasa de exito, throughput, p50, p95 e instancias observadas. Guarde el resultado completo.

### 15. Disenar la carga pico

La alarma de scale-out se activa al superar 300 solicitudes por target durante un minuto. CloudWatch puede publicar la metrica con retraso; por eso el pico debe sostenerse durante 180 segundos. Elija la concurrencia y el trabajo simulado necesarios para superar el umbral.

No se proporciona el comando final. Construyalo con las opciones consultadas en `--help` y respete estos limites:

- duracion exactamente de 180 segundos;
- concurrencia entre 8 y 50;
- trabajo entre 0 y 500 ms;
- una sola ejecucion pico activa.

Antes de ejecutarlo, escriba en el informe por que espera que su configuracion supere el objetivo. Conserve el comando elegido y su salida.

La ejecucion tardara varios minutos según la combinacion elegida y debe esperar hasta que termine. No la interrumpa cuando empiece a observar cambios de capacidad: el trafico sostenido es lo que permite que CloudWatch evalúe la alarma y que el autoscaler actúe.

Mientras el generador ocupa la terminal, mantenga abierta la consola de EC2 para observar como aparecen nuevas instancias. También puede abrir otra pestaña del navegador con la URL del portal y agregar la ruta `/work?ms=<valor elegido>`. Al recargar esa pagina, observe el campo `instance` de la respuesta: cuando las nuevas replicas estén saludables, el balanceador puede distribuir las solicitudes entre distintos nombres de instancia.

### 16. Observar la decision del autoscaler

Mientras la carga sigue activa o inmediatamente despues, consulte nuevamente el estado.

```bash
./scripts/status.sh
```

Puede observar capacidad deseada 2 o 3, una instancia `Pending` o varios targets. El cambio no es instantaneo: CloudWatch agrega la metrica, la politica decide y la nueva instancia debe iniciar y superar health checks.

Abra **EC2 → Auto Scaling Groups → Activity** y observe el proceso completo. Primero deben aparecer actividades que aumentan la capacidad y crean instancias. Cuando termine la carga y la demanda permanezca baja, el autoscaler evaluara la alarma de scale-in y comenzara a retirar las replicas adicionales.

La reduccion tampoco es instantanea: espere varios minutos, actualice la lista de actividades y relacione cada evento con la capacidad deseada y las instancias visibles. No inicie la limpieza mientras este observando este ciclo.

Son evidencias obligatorias de la practica:

1. Una captura de **Activity** que muestre la creacion automatica de al menos una instancia.
2. Una captura de las instancias o targets durante la capacidad ampliada.
3. Una captura posterior de **Activity** que muestre la eliminacion automatica de las replicas adicionales.

En cada captura deben distinguirse la hora, el estado y la causa de la actividad. La primera actividad puede aparecer durante la carga o pocos minutos despues debido a la agregacion y publicacion de metricas. Si no aparece despues de cinco minutos, revise `TROUBLESHOOTING.md` antes de cambiar parametros.

## 68–85 min — Correlacionar metricas y logs

### 17. Analizar el dashboard

Abra **CloudWatch → Dashboards** y seleccione el nombre que comienza por su identificador. Ajuste el intervalo a la ultima hora.

Relacione en una misma linea temporal:

- `RequestCount`;
- `TargetResponseTime` p95;
- `GroupInServiceInstances`;
- `HealthyHostCount`.

Una replica nueva no aparece saludable en el mismo instante en que cambia la capacidad deseada. Explique esa diferencia temporal.

### 18. Consultar una muestra de logs

El ALB entrega archivos de acceso a S3 en intervalos, por lo que pueden tardar entre 5 y 10 minutos. El script localiza el objeto mas reciente, lo descomprime y muestra sus ultimas diez lineas. Es una consulta de lectura.

```bash
./scripts/show-access-logs.sh
```

La primera linea identifica el objeto S3. Despues aparecen solicitudes con timestamp, codigo HTTP, tiempos del balanceador y del target. Seleccione una linea y explique que informacion aporta que no se ve en el contador agregado de solicitudes.

Si todavia no hay objetos, avance al analisis y repita el comando antes de la verificacion final.

## 85–98 min — Verificar y responder

### 19. Ejecutar la verificacion integral

El verificador comprueba el stack, las politicas de escalado, targets saludables, contrato HTTP, dashboard y entrega de logs. No genera carga ni cambia capacidad.

```bash
./scripts/verify-lab.sh
```

Debe finalizar con:

```text
VERIFICACION DE SEMANA 1 APROBADA
```

## Preguntas para el informe

Responda con sus propias palabras, conserve la numeracion y cite las capturas o resultados que respaldan cada respuesta.

1. ¿Cumplio el portal el SLO propuesto antes, durante y despues del pico? Compare tasa de exito y p95 con valores concretos.
2. Reconstruya el orden temporal entre aumento de solicitudes, metrica, decision del autoscaler, cambio de capacidad, nuevo target saludable y resultado para el usuario.
3. ¿Que evidencia corresponde a escalabilidad y cual demuestra elasticidad? Explique por que no son sinonimos.
4. ¿Por que `RequestCount` total no describe por si solo la carga que soporta cada replica? Relacione su respuesta con `RequestCountPerTarget`.
5. Compare una metrica del dashboard con una linea del log de acceso. ¿Que pregunta responde cada fuente?
6. Identifique un cuello de botella que no se resolveria agregando instancias web. Indique una metrica que permitiria detectarlo.
7. ¿Que limite evita crecimiento indefinido y que riesgo empresarial controla? Mencione tambien la contrapartida de alcanzar ese limite durante un pico mayor.

## 98–105 min — Eliminar los recursos

### 20. Confirmar el identificador seleccionado

El siguiente comando muestra el unico stack registrado por esta copia del repositorio. Es una comprobacion de seguridad previa a la eliminacion.

```bash
cat .ucab-lab-6-stack
```

Debe coincidir exactamente con el identificador anotado al desplegar. Si no coincide, detengase y revise antes de continuar.

### 21. Eliminar el laboratorio

El script obtiene el bucket desde los outputs del stack registrado, elimina sus logs, solicita la eliminacion del stack exacto y espera la confirmacion. No elimina otros stacks por prefijo.

```bash
./scripts/cleanup-lab.sh
```

La eliminacion puede tardar varios minutos. La ultima linea debe tener esta forma:

```text
LIMPIEZA COMPLETA: ucab-lab-6-<16 digitos hexadecimales> ya no existe
```

Conserve una captura de esta confirmacion.

## Informe a entregar

Entregue un documento individual de formato libre, como documento de texto, presentacion exportada o PDF. Debe ser legible y mantener la secuencia del experimento.

Incluya:

1. Nombre, cedula, seccion, fecha e identificador del stack.
2. Hipotesis inicial y SLO numerico.
3. Las capturas necesarias de cada paso importante, acompañadas por una explicacion de lo que demuestran.
4. Comando y resultado de la carga base.
5. Justificacion, comando y resultado de la carga pico elegida.
6. Linea temporal del escalado basada en metricas y actividades, con capturas de la creacion y eliminacion automatica de instancias.
7. Analisis de al menos una linea de log.
8. Respuestas numeradas a todas las preguntas de la seccion anterior.
9. Evidencia de la verificacion integral y de la limpieza final.

`evidence/evidence-template.md` sirve como lista de control opcional; no impone el formato del documento.
