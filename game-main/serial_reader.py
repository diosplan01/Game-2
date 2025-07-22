import serial
import threading
import time
from config import SERIAL_PORT, BAUD_RATE

class SerialReader:
    def __init__(self):
        self.ser = None
        self.teclas = [False] * 4
        self.last_teclas = [False] * 4
        self.hilo = None
        self.corriendo = False
        self.reset_request = False

    def start(self):
        try:
            self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.01)
            self.corriendo = True
            self.hilo = threading.Thread(target=self.leer_serial, daemon=True)
            self.hilo.start()
            print(f"Puerto serie {SERIAL_PORT} abierto correctamente.")
        except serial.SerialException:
            print(f"No se pudo abrir el puerto serie {SERIAL_PORT}.")
            self.ser = None

    def stop(self):
        self.corriendo = False
        if self.hilo:
            self.hilo.join()
        if self.ser and self.ser.is_open:
            self.ser.close()
            print(f"Puerto serie {SERIAL_PORT} cerrado.")

    def leer_serial(self):
        while self.corriendo:
            if self.ser and self.ser.in_waiting:
                try:
                    data = self.ser.readline().decode().strip()
                    
                    # Manejar comando de reinicio
                    if data == "RESET":
                        self.reset_request = True
                        print("Solicitud de reinicio recibida")
                    # Manejar teclas normales
                    elif data.isdigit():
                        i = int(data)
                        if 0 <= i < len(self.teclas):
                            self.teclas[i] = True
                except Exception as e:
                    print(f"Error al leer del puerto serie: {e}")
            
            # Restablecer estados de teclas si no hay datos
            else:
                for i in range(4):
                    self.teclas[i] = False
            
            time.sleep(0.01)

    def get_key_states(self):
        return self.teclas

    def get_key_presses(self):
        key_presses = []
        for i in range(len(self.teclas)):
            if self.teclas[i] and not self.last_teclas[i]:
                key_presses.append(i)
        self.last_teclas = list(self.teclas)
        return key_presses
        
    def get_reset_request(self):
        if self.reset_request:
            self.reset_request = False
            return True
        return False