from msvcrt import kbhit, getch
from time import sleep
from config import config
from mqtt_controlador import AdafruitPublisher
from plc_controlador import plc_controlador

def check_exit():
    # Revisa si se presionó la tecla 'q' de forma no bloqueante
    if kbhit():
        char = getch().decode('utf-8').lower()
        return char == 'q'
    return False

try:
    stop_loop = False
    # Inicializar PLC
    plc = plc_controlador(config.PLC_IP, config.PLC_RACK, config.PLC_SLOT)
    plc.conectar()
    bandera_conexion_plc = plc.plc_core.get_connected()
    # Inicializar MQTT
    mqtt_pub = AdafruitPublisher(config.ADAFRUIT_USERNAME, config.ADAFRUIT_KEY)
    mqtt_pub.connect()
    bandera_conexion_mqtt = True

    # Loop principal
    while True:

        for var_name, (DB, START, BIT_INDEX, TIPO, RANGO_MIN, RANGO_MAX, CANAL_ERRORES, VALORES_ESPECIALES) in config.VARIABLES.items():
            if TIPO == "BOOL":
                value = plc.leer_bool(DB, START, 0, BIT_INDEX)  # Asumiendo byte 0 y bit 0 para BOOL
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
            if value == -101 and value not in [v[0] for v in VALORES_ESPECIALES]:  # Solo publicar error si no es un valor especial
                mqtt_pub.publish(CANAL_ERRORES, f"Valor fuera de rango para {var_name}: {value}")
            if value in [v[0] for v in VALORES_ESPECIALES]:  # Publicar error si es un valor especial
                error_desc = next((v[1] for v in VALORES_ESPECIALES if v[0] == value), "Valor especial desconocido")
                mqtt_pub.publish(CANAL_ERRORES, f"ERROR. Valor especial para {var_name}: {error_desc} ({value})")

            # Esperar 5 segundos antes de la siguiente lectura
            for _ in range(50):  # 50 * 0.1 segundos = 5 segundos totales
                if check_exit():
                    stop_loop = True
                    break
                sleep(0.1)

except Exception as e:
    print(f"Error: {e}")
    print("Asegúrate de que el PLC esté encendido y que la configuración sea correcta.")

finally:
    if stop_loop:
        print("Saliendo del programa...")
        try:
            if bandera_conexion_mqtt:    
                plc.disconnect()
                mqtt_pub.stop()
            elif bandera_conexion_plc:
                plc.disconnect()    
        except Exception as e:
            print(f"Error en la desconexión: {e}")