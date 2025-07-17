import threading
import time
from gnss import GNSSManager
from utils.detect_gps_port import detectar_porta_gps

class GNSSController:
    def __init__(self):
        self.gnss_manager = None
        self.position = None  # (lat, lon, speed, direction)
        self.connected = False
        self.running = False
        self.thread = None

    def start(self):
        port = detectar_porta_gps()
        if port is None:
            print("GNSSController: GPS port not detected.")
            self.connected = False
            return

        self.gnss_manager = GNSSManager(porta=port)
        if not self.gnss_manager.conectar():
            print("GNSSController: Failed to connect to GPS.")
            self.connected = False
            return

        self.connected = True
        self.running = True
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()
        print(f"GNSSController: Connected to GPS on port {port}.")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        if self.gnss_manager:
            self.gnss_manager.desconectar()
        self.connected = False

    def _read_loop(self):
        while self.running:
            ponto = self.gnss_manager.ler_ponto_gnss()
            if ponto:
                self.position = ponto
            else:
                self.position = None
            time.sleep(0.5)

    def get_position(self):
        return self.position

    def is_connected(self):
        return self.connected
