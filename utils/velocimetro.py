import time
from collections import deque
from utils.haversine import haversine

class Velocimetro:
    def __init__(self, janela_tempo=5):
        """
        Inicializa o velocímetro
        
        Args:
            janela_tempo: Tempo em segundos para calcular velocidade média
        """
        self.janela_tempo = janela_tempo
        self.pontos = deque(maxlen=50)  # Máximo 50 pontos
        self.velocidade_atual = 0.0
        self.velocidade_media = 0.0
        self.velocidade_maxima = 0.0
        self.ultima_atualizacao = time.time()
        self.usando_gnss = False  # Flag para indicar se está usando velocidade do GNSS
        
    def adicionar_ponto(self, latitude, longitude):
        """
        Adiciona um novo ponto GNSS e calcula a velocidade
        
        Args:
            latitude: Latitude em graus decimais
            longitude: Longitude em graus decimais
        """
        timestamp = time.time()
        ponto = {
            'lat': latitude,
            'lon': longitude,
            'timestamp': timestamp
        }
        
        self.pontos.append(ponto)
        self._calcular_velocidade()
        
    def _calcular_velocidade(self):
        """Calcula a velocidade baseada nos pontos recentes"""
        if len(self.pontos) < 2:
            return
            
        # Velocidade instantânea (últimos 2 pontos)
        p1 = self.pontos[-2]
        p2 = self.pontos[-1]
        
        distancia = haversine(p1['lat'], p1['lon'], p2['lat'], p2['lon'])
        tempo_decorrido = p2['timestamp'] - p1['timestamp']
        
        if tempo_decorrido > 0:
            # Velocidade em m/s
            velocidade_ms = distancia / tempo_decorrido
            # Converter para km/h
            self.velocidade_atual = velocidade_ms * 3.6
            
            # Atualizar velocidade máxima
            if self.velocidade_atual > self.velocidade_maxima:
                self.velocidade_maxima = self.velocidade_atual
                
            # Calcular velocidade média na janela de tempo
            self._calcular_velocidade_media()
            
    def _calcular_velocidade_media(self):
        """Calcula velocidade média baseada na janela de tempo"""
        if len(self.pontos) < 2:
            return
            
        tempo_atual = time.time()
        tempo_limite = tempo_atual - self.janela_tempo
        
        # Encontrar pontos dentro da janela de tempo
        pontos_validos = [p for p in self.pontos if p['timestamp'] >= tempo_limite]
        
        if len(pontos_validos) < 2:
            return
            
        # Calcular distância total e tempo total
        distancia_total = 0
        tempo_total = pontos_validos[-1]['timestamp'] - pontos_validos[0]['timestamp']
        
        for i in range(1, len(pontos_validos)):
            p1 = pontos_validos[i-1]
            p2 = pontos_validos[i]
            distancia_total += haversine(p1['lat'], p1['lon'], p2['lat'], p2['lon'])
            
        if tempo_total > 0:
            velocidade_ms = distancia_total / tempo_total
            self.velocidade_media = velocidade_ms * 3.6
            
    def obter_velocidade(self):
        """
        Retorna velocidades calculadas
        
        Returns:
            dict: {'atual': float, 'media': float, 'maxima': float}
        """
        return {
            'atual': round(self.velocidade_atual, 1),
            'media': round(self.velocidade_media, 1),
            'maxima': round(self.velocidade_maxima, 1)
        }
        
    def reset(self):
        """Reseta todas as velocidades e pontos"""
        self.pontos.clear()
        self.velocidade_atual = 0.0
        self.velocidade_media = 0.0
        self.velocidade_maxima = 0.0
        
    def eh_parado(self, threshold=0.5):
        """
        Determina se o veículo está parado
        
        Args:
            threshold: Velocidade mínima em km/h para considerar movimento
            
        Returns:
            bool: True se estiver parado
        """
        return self.velocidade_atual < threshold
    
    def obter_estatisticas(self):
        """
        Retorna estatísticas detalhadas
        
        Returns:
            dict: Estatísticas completas
        """
        return {
            'velocidade_atual': self.velocidade_atual,
            'velocidade_media': self.velocidade_media,
            'velocidade_maxima': self.velocidade_maxima,
            'total_pontos': len(self.pontos),
            'parado': self.eh_parado(),
            'tempo_janela': self.janela_tempo
        } 