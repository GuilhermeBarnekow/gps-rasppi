import serial
import serial.tools.list_ports
import time

def detectar_porta_gps(timeout=2.0):
    """
    Detecta a porta serial onde o GPS está conectado.
    Tenta abrir cada porta serial disponível e verifica se recebe mensagens NMEA válidas
    ou dados UBX (protocolo binário da u-blox).
    Retorna o nome da porta se encontrada, ou None caso contrário.
    """
    portas = serial.tools.list_ports.comports()
    portas_possiveis = [porta.device for porta in portas]

    for porta in portas_possiveis:
        try:
            with serial.Serial(porta, 115200, timeout=timeout) as ser:
                start_time = time.time()
                while time.time() - start_time < timeout:
                    linha = ser.readline()
                    if not linha:
                        continue
                    try:
                        linha_decoded = linha.decode('ascii', errors='ignore').strip()
                    except Exception:
                        linha_decoded = ''
                    # Verifica mensagens NMEA
                    if linha_decoded.startswith(('$GPRMC', '$GPGGA', '$GNRMC', '$GNGGA')):
                        return porta
                    # Verifica dados UBX (binário começa com 0xB5 0x62)
                    if len(linha) >= 2 and linha[0] == 0xB5 and linha[1] == 0x62:
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
