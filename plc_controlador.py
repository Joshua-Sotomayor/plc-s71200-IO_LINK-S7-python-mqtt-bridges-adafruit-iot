import snap7
from snap7.util import get_bool, get_int, get_real, get_string

class plc_controlador:
    def __init__(self, IP: str, RACK: int, SLOT: int):
        self.plc_ip : str = IP
        self.plc_rack : int = RACK
        self.plc_slot : int = SLOT
        self.plc : snap7.client.Client = None

    def conectar(self):
        self.plc = snap7.client.Client()
        self.plc.connect(self.plc_ip, self.plc_rack, self.plc_slot)
        print(f"Conectado al PLC en {self.plc_ip} (Rack: {self.plc_rack}, Slot: {self.plc_slot})")

    def leer_datos(self, DB: int, START: int, SIZE: int):
        return self.plc.db_read(DB, START, SIZE)

    def leer_bool(self, DB: int, START: int, BYTE_INDEX: int, BIT_INDEX: int):
        data = self.leer_datos(DB, START, 1)
        return get_bool(data, BYTE_INDEX, BIT_INDEX)

    def leer_int(self, DB: int, START: int, BYTE_INDEX: int):
        data = self.leer_datos(DB, START, 2)
        return get_int(data, BYTE_INDEX)

    def leer_real(self, DB: int, START: int, BYTE_INDEX: int):
        data = self.leer_datos(DB, START, 4)
        return get_real(data, BYTE_INDEX)

    def leer_string(self, DB: int, START: int, BYTE_INDEX: int, LENGTH: int):
        data = self.leer_datos(DB, START, LENGTH) # Ya se considera el byte de longitud y cabecera
        return get_string(data, BYTE_INDEX)
    
    def disconnect(self):
        self.plc.disconnect()