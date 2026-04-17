# Gateway de Monitoreo para Manufactura Integrada: S7-1200 y Adafruit IO

Este proyecto implementa una solución de telemetría industrial diseñada para cerrar la brecha entre el piso de control (OT) y los sistemas de información (IT). A través de una pasarela desarrollada en Python, se extraen variables de proceso de un controlador Siemens S7-1200 para su publicación en la nube mediante el protocolo MQTT, facilitando el monitoreo remoto y la gestión de datos en tiempo real.

---

## Organización del Proyecto

El sistema se divide en los siguientes módulos operativos para garantizar una gestión eficiente de los datos industriales:

| Capas | Descripción | Tecnología |
| :--- | :--- | :--- |
| **Control de Proceso** | Ejecución de la lógica de manufactura y seguridad de la celda. | Siemens S7-1200 (CPU 1215C) |
| **Interfaz Local** | Visualización y mando directo para el operador en planta. | HMI KTP700 Basic PN |
| **Puente de Datos** | Cliente encargado de la lectura de bloques de datos (DB) y procesamiento. | Python / Snap7 |
| **Broker de Mensajería** | Protocolo de transporte ligero para el envío de información a la nube. | MQTT / Adafruit IO |

---

## Instrumentación Física

El sistema integra dispositivos de medición de grado industrial para la captura de variables analógicas y digitales, permitiendo un control preciso sobre la celda de manufactura.

| Instrumento | Modelo | Función Técnica |
| :--- | :--- | :--- |
| **Transmisor de Temperatura** | IFM TA2512 | Monitoreo térmico mediante sensor de inmersión para procesos críticos. |
| **Sensor Óptico de Nivel** | IFM O1D300 | Medición de distancia por tiempo de vuelo (láser) para control de posición. |
| **Sensor Capacitivo** | IFM KG6000 | Detección de presencia y saturación de materiales en tolvas o bandas. |

---

## Lógica y Protocolos de Comunicación

La transferencia de datos se realiza en dos etapas fundamentales:

1. **Comunicación S7 (Local):** El script de Python actúa como un cliente que realiza peticiones al PLC a través de su IP estática. Se accede a los bloques de datos (DB) mediante direcciones de memoria específicas (**offsets**). Es indispensable que el PLC tenga habilitado el acceso **PUT/GET** y que los bloques de datos tengan desactivado el **Optimized block access**.
2. **Comunicación MQTT (Cloud):** Una vez validados los datos en el gateway, se empaquetan y envían al broker de Adafruit IO. Se utilizan canales separados para las variables de proceso y para los diagnósticos de error, lo que permite una visualización limpia en los dashboards.

---

## Guía de Configuración Local (config.py)

Por seguridad, el archivo de configuración que contiene las credenciales de acceso y las direcciones IP locales no está incluido en este repositorio (archivo excluido mediante `.gitignore`). Para que el sistema funcione, debe crear un archivo llamado `config.py` en la raíz del proyecto con la siguiente estructura:

### Estructura del archivo config.py

```python
class configuraciones_generales:
    def __init__(self):
        # CONFIGURACIÓN DE RED DEL PLC
        # IP del PLC físico o del puente NetToPLCSim
        self.PLC_IP = "192.168.0.10"
        self.PLC_RACK = 0
        self.PLC_SLOT = 1

        # CREDENCIALES ADAFRUIT MQTT BROKER
        self.ADAFRUIT_USERNAME = "tu_usuario"
        self.ADAFRUIT_KEY = "tu_aio_key_secreta"
        
        # MAPEO DE VARIABLES (PLC -> CLOUD)
        # Formato: "nombre": (DB, START, BIT, TIPO, MIN, MAX, FEED_ERRORES, ESPECIALES)
        self.VARIABLES = {
            "temperatura": (1, 12, None, "REAL", -54.5, 209.2, "errores.temperatura", [[2200, "OVERLOAD"], [-700, "UNDERLOAD"]]),
            "salida-1":    (1, 10, 0, "BOOL", False, True, "errores.salida-1", [[-32760, "UNDERLOAD"], [32760, "OVERLOAD"], [32764, "NODATA"]]),
            "salida-2":    (1, 10, 1, "BOOL", False, True, "errores.salida-2", []),
            "distancia":   (1, 0, None, "REAL", 0, 984.5, "errores.distancia", [])
        }