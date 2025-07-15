import math
from utils.haversine import haversine

class SistemaCoordenadasGPS:
    def __init__(self, largura_tela=800, altura_tela=480):
        """
        Inicializa o sistema de coordenadas GPS
        
        Args:
            largura_tela: Largura da tela em pixels
            altura_tela: Altura da tela em pixels
        """
        self.largura_tela = largura_tela
        self.altura_tela = altura_tela
        
        # Coordenadas de referência (centro do mapa)
        self.lat_centro = None
        self.lon_centro = None
        
        # Zoom e escala
        self.zoom = 1.0
        self.metros_por_pixel = 1.0  # Escala inicial
        
        # Limites do mapa
        self.lat_min = None
        self.lat_max = None
        self.lon_min = None
        self.lon_max = None
        
        # Offset para pan/movimentação
        self.offset_x = 0
        self.offset_y = 0
        
    def definir_centro(self, latitude, longitude):
        """
        Define o centro do mapa
        
        Args:
            latitude: Latitude central em graus decimais
            longitude: Longitude central em graus decimais
        """
        self.lat_centro = latitude
        self.lon_centro = longitude
        
    def auto_ajustar_para_pontos(self, pontos, margem_percentual=0.1):
        """
        Ajusta automaticamente o zoom e centro para mostrar todos os pontos
        
        Args:
            pontos: Lista de tuplas (latitude, longitude)
            margem_percentual: Margem extra ao redor dos pontos (0.1 = 10%)
        """
        if not pontos:
            return
            
        # Encontrar limites dos pontos
        lats = [p[0] for p in pontos]
        lons = [p[1] for p in pontos]
        
        self.lat_min = min(lats)
        self.lat_max = max(lats)
        self.lon_min = min(lons)
        self.lon_max = max(lons)
        
        # Calcular centro
        self.lat_centro = (self.lat_min + self.lat_max) / 2
        self.lon_centro = (self.lon_min + self.lon_max) / 2
        
        # Calcular dimensões em metros
        altura_metros = haversine(self.lat_min, self.lon_centro, 
                                 self.lat_max, self.lon_centro)
        largura_metros = haversine(self.lat_centro, self.lon_min, 
                                  self.lat_centro, self.lon_max)
        
        # Adicionar margem
        altura_metros *= (1 + margem_percentual * 2)
        largura_metros *= (1 + margem_percentual * 2)
        
        # Calcular escala baseada na dimensão maior
        escala_altura = altura_metros / self.altura_tela
        escala_largura = largura_metros / self.largura_tela
        
        self.metros_por_pixel = max(escala_altura, escala_largura)
        
    def gps_para_pixel(self, latitude, longitude):
        """
        Converte coordenadas GPS para posição em pixels na tela
        
        Args:
            latitude: Latitude em graus decimais
            longitude: Longitude em graus decimais
            
        Returns:
            tuple: (x, y) em pixels
        """
        if self.lat_centro is None or self.lon_centro is None:
            return (self.largura_tela // 2, self.altura_tela // 2)
        
        # Calcular distância em metros do centro
        # Distância vertical (Norte-Sul)
        if latitude > self.lat_centro:
            dist_y = -haversine(self.lat_centro, self.lon_centro, 
                               latitude, self.lon_centro)
        else:
            dist_y = haversine(self.lat_centro, self.lon_centro, 
                              latitude, self.lon_centro)
        
        # Distância horizontal (Leste-Oeste)
        if longitude > self.lon_centro:
            dist_x = haversine(self.lat_centro, self.lon_centro, 
                              self.lat_centro, longitude)
        else:
            dist_x = -haversine(self.lat_centro, self.lon_centro, 
                               self.lat_centro, longitude)
        
        # Converter para pixels
        pixel_x = (self.largura_tela // 2) + (dist_x / self.metros_por_pixel) + self.offset_x
        pixel_y = (self.altura_tela // 2) + (dist_y / self.metros_por_pixel) + self.offset_y
        
        return (int(pixel_x), int(pixel_y))
    
    def pixel_para_gps(self, x, y):
        """
        Converte posição em pixels para coordenadas GPS
        
        Args:
            x: Posição X em pixels
            y: Posição Y em pixels
            
        Returns:
            tuple: (latitude, longitude)
        """
        if self.lat_centro is None or self.lon_centro is None:
            return (0, 0)
        
        # Calcular distância em metros do centro
        dist_x = (x - self.largura_tela // 2 - self.offset_x) * self.metros_por_pixel
        dist_y = (y - self.altura_tela // 2 - self.offset_y) * self.metros_por_pixel
        
        # Aproximação simples para pequenas distâncias
        # Para precisão maior, seria necessário usar projeção cartográfica
        
        # 1 grau de latitude ≈ 111.320 metros
        # 1 grau de longitude ≈ 111.320 * cos(latitude) metros
        
        delta_lat = -dist_y / 111320.0
        delta_lon = dist_x / (111320.0 * math.cos(math.radians(self.lat_centro)))
        
        latitude = self.lat_centro + delta_lat
        longitude = self.lon_centro + delta_lon
        
        return (latitude, longitude)
    
    def aplicar_zoom(self, fator_zoom, centro_x=None, centro_y=None):
        """
        Aplica zoom no mapa
        
        Args:
            fator_zoom: Fator de zoom (>1 para zoom in, <1 para zoom out)
            centro_x: X do centro do zoom (default: centro da tela)
            centro_y: Y do centro do zoom (default: centro da tela)
        """
        if centro_x is None:
            centro_x = self.largura_tela // 2
        if centro_y is None:
            centro_y = self.altura_tela // 2
            
        # Aplicar zoom
        self.zoom *= fator_zoom
        self.metros_por_pixel /= fator_zoom
        
        # Ajustar offset para manter o ponto central
        self.offset_x = (self.offset_x - centro_x) * fator_zoom + centro_x
        self.offset_y = (self.offset_y - centro_y) * fator_zoom + centro_y
        
    def mover_offset(self, delta_x, delta_y):
        """
        Move o offset do mapa (pan)
        
        Args:
            delta_x: Movimento em X (pixels)
            delta_y: Movimento em Y (pixels)
        """
        self.offset_x += delta_x
        self.offset_y += delta_y
        
    def resetar_offset(self):
        """Reset o offset para zero"""
        self.offset_x = 0
        self.offset_y = 0
        
    def obter_escala_metros(self):
        """
        Retorna a escala atual em metros por pixel
        
        Returns:
            float: Metros por pixel
        """
        return self.metros_por_pixel
        
    def obter_dimensao_tela_metros(self):
        """
        Retorna as dimensões da tela em metros
        
        Returns:
            tuple: (largura_metros, altura_metros)
        """
        largura_metros = self.largura_tela * self.metros_por_pixel
        altura_metros = self.altura_tela * self.metros_por_pixel
        return (largura_metros, altura_metros)
        
    def ponto_visivel(self, latitude, longitude, margem=50):
        """
        Verifica se um ponto GPS está visível na tela
        
        Args:
            latitude: Latitude do ponto
            longitude: Longitude do ponto
            margem: Margem em pixels ao redor da tela
            
        Returns:
            bool: True se o ponto está visível
        """
        x, y = self.gps_para_pixel(latitude, longitude)
        
        return (-margem <= x <= self.largura_tela + margem and 
                -margem <= y <= self.altura_tela + margem)
    
    def obter_limites_visiveis(self):
        """
        Retorna os limites GPS da área visível na tela
        
        Returns:
            dict: {'lat_min', 'lat_max', 'lon_min', 'lon_max'}
        """
        # Cantos da tela
        top_left = self.pixel_para_gps(0, 0)
        top_right = self.pixel_para_gps(self.largura_tela, 0)
        bottom_left = self.pixel_para_gps(0, self.altura_tela)
        bottom_right = self.pixel_para_gps(self.largura_tela, self.altura_tela)
        
        lats = [top_left[0], top_right[0], bottom_left[0], bottom_right[0]]
        lons = [top_left[1], top_right[1], bottom_left[1], bottom_right[1]]
        
        return {
            'lat_min': min(lats),
            'lat_max': max(lats),
            'lon_min': min(lons),
            'lon_max': max(lons)
        } 