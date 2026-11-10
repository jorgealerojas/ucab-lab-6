# Solucion de problemas

Consulte esta pagina solamente cuando un paso de `LAB_GUIDE.md` no produzca el resultado esperado.

## El diagnostico informa una region diferente

Confirme que ambas variables de region tengan el valor `us-east-2`. El laboratorio rechaza otras regiones para evitar recursos dispersos.

## CloudFormation termina en `CREATE_FAILED`

Abra **CloudFormation → Stacks**, seleccione el identificador exacto y revise **Events** desde el evento mas antiguo que tenga estado de error. No ejecute nuevamente el despliegue: el archivo local conserva el identificador necesario para limpiar ese intento.

Las causas mas frecuentes son permisos insuficientes, limites de EC2 o falta de capacidad temporal para el tipo `t3.micro`.

## El stack finaliza, pero no hay targets saludables

Espere dos minutos y ejecute nuevamente el script de estado. La instancia necesita iniciar el servicio y superar dos health checks consecutivos.

Si el problema persiste, revise en **EC2 → Target Groups → Targets** la razon que muestra AWS.

## La carga no produce scale-out

Una sola ventana corta puede no superar el objetivo durante suficiente tiempo. Revise primero `RequestCount`, la actividad del Auto Scaling Group y la ayuda del generador. Aumente de forma gradual la duración o concurrencia sin superar los limites permitidos por la herramienta.

## Todavia no aparecen logs

Los logs del Application Load Balancer no son inmediatos. Genere solicitudes, espere entre 5 y 10 minutos y vuelva a consultar. La ausencia momentanea de un archivo no implica que el balanceador haya dejado de atender trafico.

## La limpieza falla porque el bucket no esta vacio

Ejecute otra vez el script de limpieza. Este vacia solamente el bucket obtenido desde los outputs del stack registrado localmente y luego vuelve a solicitar la eliminacion.

## Se cerro CloudShell y no aparece el archivo de estado

No escriba un identificador aproximado. Localice en CloudFormation el stack cuyo nombre empieza por `ucab-lab-6-` y que tenga sus etiquetas del curso. Copie el nombre exacto y solicite ayuda antes de borrar recursos en una cuenta compartida.

