# UCAB Lab 6: operar un portal bajo demanda

Laboratorio de la Unidad VI de **Computacion en la Nube (INFO-02028)**. El caso sigue un portal universitario cuya demanda aumenta durante el periodo de inscripciones. La meta no es solamente crear servidores: es operar un servicio medible y adaptar su capacidad a la demanda.

La unidad se desarrolla como una historia continua de dos semanas:

- **Semana 1 — Operar y escalar:** adopcion empresarial, escalabilidad, elasticidad, automatizacion, configuracion, administracion y monitoreo.
- **Semana 2 — Proteger y decidir:** seguridad, proveedores y consolidacion de la arquitectura. Su material se agregara en una iteracion posterior.

Este repositorio contiene actualmente **solo la Semana 1**.

## Reto de la Semana 1

Desplegar un portal web detras de un Application Load Balancer, generar demanda controlada y comprobar con evidencia si EC2 Auto Scaling ajusta la capacidad. El analisis usa indicadores del servicio —tasa de exito y latencia p95— junto con metricas, actividades de escalado y logs.

```text
Cliente / generador de carga
              |
              v
 Application Load Balancer
              |
              v
       Target Group
              |
              v
 Auto Scaling Group (1 a 3 EC2)

 CloudWatch: metricas, dashboard y alarma
 S3: logs de acceso del balanceador
 CloudFormation: infraestructura como codigo
```

## Resultados de aprendizaje

Al completar la primera semana podra:

1. Relacionar la adopcion de nube con una necesidad empresarial medible.
2. Distinguir escalabilidad de elasticidad mediante un experimento.
3. Explicar como alarmas y politicas de escalado observan, deciden y actuan.
4. Interpretar solicitudes, latencia p95, targets saludables y capacidad en servicio.
5. Usar logs y metricas para respaldar un diagnostico.
6. Reconocer limites que no se resuelven agregando replicas web.

## Servicios y conceptos

| Elemento | Funcion en la practica | Concepto |
|---|---|---|
| AWS CloudFormation | Crea y elimina la arquitectura como una unidad | Infraestructura como codigo |
| Amazon VPC | Aloja subredes y reglas de red | Configuracion de red |
| Application Load Balancer | Distribuye solicitudes y comprueba salud | Balanceo y health checks |
| EC2 Launch Template | Define como nace cada replica | Configuracion repetible |
| EC2 Auto Scaling | Mantiene y ajusta la cantidad de instancias | Escalabilidad y elasticidad |
| Amazon CloudWatch | Presenta metricas, dashboard y alarma p95 | Monitoreo y SLI |
| Amazon S3 | Conserva los logs de acceso del ALB | Evidencia operativa |
| Generador de carga | Produce demanda acotada y calcula indicadores | Prueba de capacidad |

Las alarmas usan `RequestCountPerTarget`: scale-out sobre 300 solicitudes por target en un minuto y scale-in por debajo de 60 durante tres minutos. Estos umbrales son didacticos, no numeros universales de capacidad. En un sistema real deben calibrarse mediante pruebas y requisitos del servicio.

## Diseño seguro para cuentas compartidas

Cada despliegue genera localmente un identificador aleatorio de 64 bits, por ejemplo:

```text
ucab-lab-6-7f03c9a4d621be80
```

La creacion usa la operacion atomica `CreateStack`. Si el nombre ya existiera, AWS rechaza la solicitud y el script no actualiza el stack encontrado. El identificador aceptado se guarda en `.ucab-lab-6-stack`; los scripts posteriores consultan exclusivamente ese stack.

La limpieza obtiene desde sus outputs el bucket de logs correspondiente, lo vacia y elimina esa unidad de CloudFormation. No busca ni borra otros stacks con nombres parecidos.

## Limites de costo y operacion

- Region obligatoria: **US East (Ohio), `us-east-2`**.
- Capacidad minima 1, deseada 1 y maxima 3 instancias `t3.micro`.
- Duracion maxima permitida por una ejecucion del generador: 180 segundos.
- Concurrencia maxima permitida: 50.
- El Application Load Balancer, las instancias y las direcciones IPv4 pueden generar cargos mientras existan.
- La limpieza al terminar es obligatoria.

## Organizacion

| Ruta | Contenido |
|---|---|
| `LAB_GUIDE.md` | Unico paso a paso de la practica, con comandos, explicaciones y resultados esperados |
| `app/server.py` | Aplicacion web stateless que identifica la replica que responde |
| `infra/lab-stack.yaml` | VPC, ALB, Launch Template, Auto Scaling, CloudWatch y bucket de logs |
| `scripts/doctor.sh` | Comprueba herramientas, credenciales, region, plantilla y pruebas locales |
| `scripts/deploy-lab.sh` | Genera el identificador y crea un stack nuevo |
| `scripts/get-url.sh` | Recupera la URL desde los outputs de CloudFormation |
| `scripts/status.sh` | Muestra capacidad, instancias y salud de los targets |
| `scripts/load_test.py` | Genera trafico y calcula throughput, exito, p50 y p95 |
| `scripts/show-access-logs.sh` | Presenta una muestra del log mas reciente del ALB |
| `scripts/verify-lab.sh` | Comprueba integralmente la Semana 1 |
| `scripts/cleanup-lab.sh` | Vacia el bucket propio y elimina el stack registrado |
| `evidence/evidence-template.md` | Lista de control opcional para el informe |
| `TROUBLESHOOTING.md` | Diagnostico de problemas frecuentes |
| `tests/` | Pruebas unitarias y validaciones del repositorio |

## Realizacion de la practica

Siga [LAB_GUIDE.md](LAB_GUIDE.md). El README no repite comandos ni pasos para evitar dos recorridos distintos.
