from time import sleep
from config import config
from mqtt_controlador import AdafruitPublisher
from plc_controlador import plc_controlador



try:
    # Inicializar PLC
    plc = plc_controlador(config.PLC_IP, config.PLC_RACK, config.PLC_SLOT)
    plc.conectar()

    # Inicializar MQTT
    mqtt_pub = AdafruitPublisher(config.ADAFRUIT_USERNAME, config.ADAFRUIT_KEY)
    mqtt_pub.connect()

    # Loop principal
    while True:
        for var_name, (DB, START, TIPO, RANGO_MIN, RANGO_MAX) in config.VARIABLES.items():
            if TIPO == "BOOL":
                value = plc.leer_bool(DB, START, 0, 0)  # Asumiendo byte 0 y bit 0 para BOOL
                if value != RANGO_MIN and value != RANGO_MAX: 
                    value = -101 # Valor fuera de rango para indicar que no se publica
            elif TIPO == "INT":
                value = plc.leer_int(DB, START, 0)  # Asumiendo byte 0 para INT
                if value < RANGO_MIN or value > RANGO_MAX:
                    value = -101 # Valor fuera de rango para indicar que no se publica
            elif TIPO == "REAL":
                value = plc.leer_real(DB, START, 0)  # Asumiendo byte 0 para REAL
                if value < RANGO_MIN or value > RANGO_MAX:
                    value = -101 # Valor fuera de rango para indicar que no se publica
            elif TIPO == "STRING":
                value = plc.leer_string(DB, START, 0, RANGO_MAX)  # Asumiendo byte 0 para STRING
            else:
                print(f"Tipo de dato no soportado: {TIPO}")
                continue

            mqtt_pub.publish(var_name, value)

            sleep(5)  # Esperar 5 segundos antes de la siguiente lectura
            
except Exception as e:
    print(f"Error: {e}")
    print("Asegúrate de que el PLC esté encendido y que la configuración sea correcta.")