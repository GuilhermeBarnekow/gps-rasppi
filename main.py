from gnss import GNSSManager
from utils.area_calc import calcular_area
from utils.haversine import haversine
from utils.velocimetro import Velocimetro
from utils.exportacao import ExportadorDados
import db
from utils.detect_gps_port import detectar_porta_gps
from ui.kivy_interface import GPSApp
import sys

def main():
    # Launch the Kivy GPS app directly
    GPSApp().run()

def draw_status_info(screen, gnss_manager, velocimetro):
    """Desenha informações de status no canto inferior esquerdo"""
    # This function is pygame-specific and can be removed or refactored if pygame is removed
    pass

if __name__ == '__main__':
    main()
