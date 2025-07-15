import serial
import pynmea2
import time
from collections import deque

class GNSSManager:
    def __init__(self, porta='/dev/serial0', baudrate=9600):
        self.porta = porta
        self.baudrate = baudrate
        self.serial_connection = None
        self.ultimo_ponto_valido = None
        self.historico_pontos = deque(maxlen=10)
        self.tentativas_conexao = 0
        self.max_tentativas = 5
        self.timeout_conexao = 2.0
        
        # Estatísticas
        self.total_leituras = 0
        self.leituras_validas = 0
        self.ultimo_erro = None
        self.tempo_ultimo_ponto = None
        
        # Modo simulação para desenvolvimento
        self.modo_simulacao = False
        self.posicao_simulada = (-15.7801, -47.9292)  # Brasília
        
    def conectar(self):
        """Estabelece conexão com o módulo GNSS"""
        try:
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()
                
            self.serial_connection = serial.Serial(
                self.porta, 
                self.baudrate, 
                timeout=self.timeout_conexao
            )
            
            self.tentativas_conexao = 0
            self.ultimo_erro = None
            return True
            
        except Exception as e:
            self.tentativas_conexao += 1
            self.ultimo_erro = f"Erro de conexão: {str(e)}"
            return False
    
    def desconectar(self):
        """Fecha conexão com o módulo GNSS"""
        try:
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()
                self.serial_connection = None
        except:
            pass
    
    def ler_ponto_gnss(self):
        """
        Lê ponto GNSS com tratamento de erros robusto
        
        Returns:
            tuple: (latitude, longitude) ou None se não conseguir ler
        """
        self.total_leituras += 1
        
        # Modo simulação
        if self.modo_simulacao:
            return self._simular_ponto()
        
        try:
            # Conectar se necessário
            if not self.serial_connection or not self.serial_connection.is_open:
                if not self.conectar():
                    return self._fallback_ponto()
            
            # Tentar ler várias linhas para encontrar uma válida
            for tentativa in range(5):
                try:
                    if self.serial_connection and self.serial_connection.is_open:
                        linha = self.serial_connection.readline().decode('ascii', errors='replace').strip()
                        
                        if not linha:
                            continue
                            
                        # Processar diferentes tipos de mensagens NMEA
                        if linha.startswith('$GPRMC') or linha.startswith('$GNRMC'):
                            return self._processar_rmc(linha)
                        elif linha.startswith('$GPGGA') or linha.startswith('$GNGGA'):
                            return self._processar_gga(linha)
                    else:
                        break
                        
                except Exception as e:
                    self.ultimo_erro = f"Erro na leitura {tentativa + 1}: {str(e)}"
                    continue
            
            # Se chegou aqui, não conseguiu ler
            return self._fallback_ponto()
            
        except Exception as e:
            self.ultimo_erro = f"Erro geral: {str(e)}"
            return self._fallback_ponto()
    
    def _processar_rmc(self, linha):
        """Processa mensagem RMC"""
        try:
            msg = pynmea2.parse(linha)
            
            # Verificar se o fix é válido
            if msg.status != 'A':  # 'A' = ativo, 'V' = inválido
                return None
                
            if msg.latitude is None or msg.longitude is None:
                return None
            
            # Extrair velocidade da mensagem NMEA (em nós)
            velocidade_nos = 0
            if hasattr(msg, 'spd_over_grnd') and msg.spd_over_grnd is not None:
                try:
                    velocidade_nos = float(msg.spd_over_grnd)
                except (ValueError, TypeError):
                    velocidade_nos = 0
            
            velocidade_kmh = velocidade_nos * 1.852  # Converter nós para km/h
            
            # Extrair direção (course over ground)
            direcao = 0
            if hasattr(msg, 'true_course') and msg.true_course is not None:
                try:
                    direcao = float(msg.true_course)
                except (ValueError, TypeError):
                    direcao = 0
                
            ponto = (float(msg.latitude), float(msg.longitude), velocidade_kmh, direcao)
            return self._validar_ponto(ponto)
            
        except Exception as e:
            self.ultimo_erro = f"Erro RMC: {str(e)}"
            return None
    
    def _processar_gga(self, linha):
        """Processa mensagem GGA"""
        try:
            msg = pynmea2.parse(linha)
            
            # Verificar qualidade do fix
            if msg.gps_qual == 0:  # 0 = sem fix
                return None
                
            if msg.latitude is None or msg.longitude is None:
                return None
                
            # GGA não tem velocidade, então usar valores padrão
            ponto = (float(msg.latitude), float(msg.longitude), 0, 0)
            return self._validar_ponto(ponto)
            
        except Exception as e:
            self.ultimo_erro = f"Erro GGA: {str(e)}"
            return None
    
    def _validar_ponto(self, ponto):
        """Valida se o ponto é razoável"""
        if len(ponto) >= 2:
            lat, lon = ponto[0], ponto[1]
        else:
            return None
        
        # Verificar se está dentro de limites razoáveis
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return None
            
        # Verificar se não é muito diferente do último ponto
        if self.ultimo_ponto_valido:
            from utils.haversine import haversine
            dist = haversine(self.ultimo_ponto_valido[0], self.ultimo_ponto_valido[1], lat, lon)
            
            # Se a distância for muito grande, provavelmente é erro
            if dist > 1000:  # 1km
                return None
        
        # Ponto válido
        self.ultimo_ponto_valido = ponto
        self.tempo_ultimo_ponto = time.time()
        self.leituras_validas += 1
        self.historico_pontos.append(ponto)
        
        return ponto
    
    def _fallback_ponto(self):
        """Retorna ponto de fallback em caso de erro"""
        # Se temos pontos recentes, pode usar extrapolação simples
        if len(self.historico_pontos) >= 2:
            return self._extrapolar_posicao()
            
        # Usar último ponto válido se foi recente
        if (self.ultimo_ponto_valido and self.tempo_ultimo_ponto and 
            time.time() - self.tempo_ultimo_ponto < 10):
            return self.ultimo_ponto_valido
            
        return None
    
    def _extrapolar_posicao(self):
        """Extrapola posição baseada nos últimos pontos"""
        if len(self.historico_pontos) < 2:
            return None
            
        # Usar os dois últimos pontos para calcular direção
        p1 = self.historico_pontos[-2]
        p2 = self.historico_pontos[-1]
        
        # Calcular deslocamento
        delta_lat = p2[0] - p1[0]
        delta_lon = p2[1] - p1[1]
        
        # Extrapolar (movimento muito pequeno)
        nova_lat = p2[0] + delta_lat * 0.1
        nova_lon = p2[1] + delta_lon * 0.1
        
        # Estimar velocidade e direção baseado no movimento
        velocidade_estimada = 0
        direcao_estimada = 0
        
        return (nova_lat, nova_lon, velocidade_estimada, direcao_estimada)
    
    def _simular_ponto(self):
        """Simula ponto GPS para desenvolvimento"""
        import random
        
        # Adicionar pequeno ruído à posição
        ruido_lat = random.uniform(-0.0001, 0.0001)
        ruido_lon = random.uniform(-0.0001, 0.0001)
        
        lat = self.posicao_simulada[0] + ruido_lat
        lon = self.posicao_simulada[1] + ruido_lon
        
        # Simular velocidade (0-20 km/h)
        velocidade_simulada = random.uniform(0, 20)
        
        # Simular direção (0-360 graus)
        direcao_simulada = random.uniform(0, 360)
        
        # Simular movimento lento
        self.posicao_simulada = (lat, lon)
        
        return (lat, lon, velocidade_simulada, direcao_simulada)
    
    def obter_status(self):
        """Retorna status detalhado do GNSS"""
        taxa_sucesso = 0
        if self.total_leituras > 0:
            taxa_sucesso = (self.leituras_validas / self.total_leituras) * 100
        
        tempo_desde_ultimo = None
        if self.tempo_ultimo_ponto:
            tempo_desde_ultimo = time.time() - self.tempo_ultimo_ponto
        
        return {
            'conectado': self.serial_connection and self.serial_connection.is_open,
            'modo_simulacao': self.modo_simulacao,
            'total_leituras': self.total_leituras,
            'leituras_validas': self.leituras_validas,
            'taxa_sucesso': taxa_sucesso,
            'ultimo_erro': self.ultimo_erro,
            'tempo_desde_ultimo': tempo_desde_ultimo,
            'tentativas_conexao': self.tentativas_conexao,
            'pontos_historico': len(self.historico_pontos)
        }
    
    def ativar_modo_simulacao(self, posicao_inicial=None):
        """Ativa modo simulação para desenvolvimento"""
        self.modo_simulacao = True
        if posicao_inicial:
            self.posicao_simulada = posicao_inicial
    
    def desativar_modo_simulacao(self):
        """Desativa modo simulação"""
        self.modo_simulacao = False
    
    def resetar_estatisticas(self):
        """Reseta estatísticas"""
        self.total_leituras = 0
        self.leituras_validas = 0
        self.ultimo_erro = None
        self.tentativas_conexao = 0

# Manter compatibilidade com código existente
def ler_ponto_gnss(porta='/dev/serial0', baudrate=9600):
    """Função de compatibilidade - retorna apenas lat, lon"""
    manager = GNSSManager(porta, baudrate)
    dados_completos = manager.ler_ponto_gnss()
    if dados_completos:
        return (dados_completos[0], dados_completos[1])  # Apenas lat, lon
    return None
