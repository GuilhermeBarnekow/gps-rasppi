import serial
import serial.tools.list_ports
import time

def detectar_porta_gps(timeout=2.0):
    """
    Detecta a porta serial onde o GPS está conectado.
    Tenta abrir cada porta serial disponível e verifica se recebe mensagens NMEA válidas.
    Retorna o nome da porta se encontrada, ou None caso contrário.
    """
    portas = serial.tools.list_ports.comports()
    portas_possiveis = [porta.device for porta in portas]

    for porta in portas_possiveis:
        try:
            with serial.Serial(porta, 115200, timeout=timeout) as ser:
                start_time = time.time()
                while time.time() - start_time < timeout:
                    linha = ser.readline().decode('ascii', errors='ignore').strip()
                    if linha.startswith(('$GPRMC', '$GPGGA', '$GNRMC', '$GNGGA')):
                        return porta
        except (serial.SerialException, OSError):
            continue
    return None

if __name__ == "__main__":
    porta_encontrada = detectar_porta_gps()
    if porta_encontrada:
        print(f"GPS detectado na porta: {porta_encontrada}")
    else:
        print("GPS não detectado em nenhuma porta serial.")
