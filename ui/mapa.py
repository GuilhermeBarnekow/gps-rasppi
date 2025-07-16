import pygame
import math
from ui.components import Colors
from utils.coordenadas import SistemaCoordenadasGPS

class Mapa:
    def __init__(self, tela, largura=800, altura=480):
        self.tela = tela
        self.largura = largura
        self.altura = altura
        self.trilha = []  # Lista de pontos (latitude, longitude)
        self.sistema_coords = SistemaCoordenadasGPS(largura, altura)
        self.posicao_atual = None
        self.direcao_atual = 0  # Ângulo em radianos
        
        # Área do mapa (deixa espaço para o painel lateral)
        self.area_mapa = pygame.Rect(0, 0, 580, altura)
        
        # Cores do mapa
        self.cor_fundo = (34, 139, 34)  # Verde floresta
        self.cor_trilha = Colors.ACCENT
        self.cor_trator = Colors.TEXT_PRIMARY
        self.cor_grid = (0, 100, 0)  # Verde escuro para grid
        
    def add_point(self, ponto):
        """Adiciona um ponto GPS à trilha"""
        lat, lon = ponto
        self.trilha.append((lat, lon))
        self.posicao_atual = ponto
        
        # Auto-ajustar o mapa para mostrar todos os pontos
        if len(self.trilha) > 1:
            self.sistema_coords.auto_ajustar_para_pontos(self.trilha)
        else:
            # Primeiro ponto - centralizar
            self.sistema_coords.definir_centro(lat, lon)
            self.sistema_coords.metros_por_pixel = 2.0  # Escala inicial
    
    def calcular_direcao(self):
        """Calcula a direção do trator baseada nos últimos pontos"""
        if len(self.trilha) < 2:
            return
            
        p1 = self.trilha[-2]
        p2 = self.trilha[-1]
        
        # Calcular ângulo entre os dois pontos
        lat1, lon1 = p1
        lat2, lon2 = p2
        
        delta_lat = lat2 - lat1
        delta_lon = lon2 - lon1
        
        self.direcao_atual = math.atan2(delta_lon, delta_lat)

    def handle_event(self, event):
        """Manipula eventos do mapa (zoom, pan)"""
        if event.type == pygame.KEYDOWN:
            v = 20
            if event.key == pygame.K_w:
                self.sistema_coords.mover_offset(0, v)
            if event.key == pygame.K_s:
                self.sistema_coords.mover_offset(0, -v)
            if event.key == pygame.K_a:
                self.sistema_coords.mover_offset(v, 0)
            if event.key == pygame.K_d:
                self.sistema_coords.mover_offset(-v, 0)
            if event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                self.sistema_coords.aplicar_zoom(1.2)
            if event.key == pygame.K_MINUS:
                self.sistema_coords.aplicar_zoom(0.8)
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.area_mapa.collidepoint(event.pos):
                if event.button == 4:  # Scroll up
                    self.sistema_coords.aplicar_zoom(1.1, event.pos[0], event.pos[1])
                elif event.button == 5:  # Scroll down
                    self.sistema_coords.aplicar_zoom(0.9, event.pos[0], event.pos[1])
                    
        elif event.type == pygame.MOUSEMOTION:
            if event.buttons[0] and self.area_mapa.collidepoint(event.pos):  # Arrastar
                self.sistema_coords.mover_offset(event.rel[0], event.rel[1])

    def draw_grid(self):
        """Desenha grid de referência"""
        escala = self.sistema_coords.obter_escala_metros()
        
        # Determinar espaçamento do grid baseado na escala
        if escala < 0.5:
            espacamento = 10  # 10 metros
        elif escala < 2:
            espacamento = 50  # 50 metros
        elif escala < 10:
            espacamento = 100  # 100 metros
        else:
            espacamento = 500  # 500 metros
            
        pixel_espacamento = espacamento / escala
        
        # Desenhar linhas verticais
        for x in range(0, self.area_mapa.width, int(pixel_espacamento)):
            pygame.draw.line(self.tela, self.cor_grid, (x, 0), (x, self.area_mapa.height), 1)
            
        # Desenhar linhas horizontais
        for y in range(0, self.area_mapa.height, int(pixel_espacamento)):
            pygame.draw.line(self.tela, self.cor_grid, (0, y), (self.area_mapa.width, y), 1)

    def draw_trilha(self):
        """Desenha a trilha percorrida"""
        if len(self.trilha) < 2:
            return
            
        pontos_pixel = []
        for lat, lon in self.trilha:
            x, y = self.sistema_coords.gps_para_pixel(lat, lon)
            if self.area_mapa.collidepoint(x, y):
                pontos_pixel.append((x, y))
        
        if len(pontos_pixel) > 1:
            pygame.draw.lines(self.tela, self.cor_trilha, False, pontos_pixel, 3)
            
        # Desenhar pontos individuais
        for x, y in pontos_pixel:
            pygame.draw.circle(self.tela, self.cor_trilha, (x, y), 2)

    def draw_trator(self):
        """Desenha o trator na posição atual"""
        if not self.posicao_atual:
            return
            
        x, y = self.sistema_coords.gps_para_pixel(*self.posicao_atual)
        
        if not self.area_mapa.collidepoint(x, y):
            return
            
        # Calcular direção
        self.calcular_direcao()
        
        # Desenhar trator como triângulo orientado
        tamanho = 8
        pontos = []
        
        # Pontos do triângulo (apontando para cima inicialmente)
        triangulo = [
            (0, -tamanho),    # Ponta
            (-tamanho//2, tamanho//2),  # Esquerda
            (tamanho//2, tamanho//2)    # Direita
        ]
        
        # Rotacionar baseado na direção
        cos_a = math.cos(self.direcao_atual)
        sin_a = math.sin(self.direcao_atual)
        
        for px, py in triangulo:
            nx = px * cos_a - py * sin_a
            ny = px * sin_a + py * cos_a
            pontos.append((x + nx, y + ny))
            
        pygame.draw.polygon(self.tela, self.cor_trator, pontos)
        
        # Desenhar círculo ao redor para melhor visibilidade
        pygame.draw.circle(self.tela, self.cor_trator, (int(x), int(y)), tamanho + 2, 2)

    def draw_trator(self):
        """Desenha o trator na posição atual"""
        if not self.posicao_atual:
            return
            
        x, y = self.sistema_coords.gps_para_pixel(*self.posicao_atual)
        
        if not self.area_mapa.collidepoint(x, y):
            return
            
        # Calcular direção
        self.calcular_direcao()
        
        # Desenhar trator como triângulo orientado com sombra para profundidade
        tamanho = 10
        pontos = []
        
        # Pontos do triângulo (apontando para cima inicialmente)
        triangulo = [
            (0, -tamanho),    # Ponta
            (-tamanho//2, tamanho//2),  # Esquerda
            (tamanho//2, tamanho//2)    # Direita
        ]
        
        # Rotacionar baseado na direção
        cos_a = math.cos(self.direcao_atual)
        sin_a = math.sin(self.direcao_atual)
        
        for px, py in triangulo:
            nx = px * cos_a - py * sin_a
            ny = px * sin_a + py * cos_a
            pontos.append((x + nx, y + ny))
            
        # Desenhar sombra do trator
        sombra_offset = 3
        pontos_sombra = [(px + sombra_offset, py + sombra_offset) for px, py in pontos]
        pygame.draw.polygon(self.tela, (0, 0, 0, 100), pontos_sombra)
        
        # Desenhar trator
        pygame.draw.polygon(self.tela, self.cor_trator, pontos)
        
        # Desenhar círculo ao redor para melhor visibilidade
        pygame.draw.circle(self.tela, self.cor_trator, (int(x), int(y)), tamanho + 3, 3)

    def draw_escala(self):
        """Desenha escala do mapa"""
        escala = self.sistema_coords.obter_escala_metros()
        
        # Determinar comprimento da escala
        if escala < 1:
            comprimento_metros = 10
        elif escala < 5:
            comprimento_metros = 50
        elif escala < 20:
            comprimento_metros = 100
        else:
            comprimento_metros = 500
            
        comprimento_pixels = int(comprimento_metros / escala)
        
        # Posição da escala
        x_escala = 20
        y_escala = self.area_mapa.height - 40
        
        # Desenhar escala
        pygame.draw.line(self.tela, Colors.TEXT_PRIMARY, 
                        (x_escala, y_escala), 
                        (x_escala + comprimento_pixels, y_escala), 3)
        
        # Marcadores nas pontas
        pygame.draw.line(self.tela, Colors.TEXT_PRIMARY, 
                        (x_escala, y_escala - 5), 
                        (x_escala, y_escala + 5), 2)
        pygame.draw.line(self.tela, Colors.TEXT_PRIMARY, 
                        (x_escala + comprimento_pixels, y_escala - 5), 
                        (x_escala + comprimento_pixels, y_escala + 5), 2)
        
        # Texto da escala
        font = pygame.font.Font(None, 24)
        texto = font.render(f"{comprimento_metros}m", True, Colors.TEXT_PRIMARY)
        self.tela.blit(texto, (x_escala, y_escala - 25))

    def draw(self):
        """Desenha o mapa completo"""
        # Limitar área de desenho
        clip_original = self.tela.get_clip()
        self.tela.set_clip(self.area_mapa)
        
        # Fundo com gradiente de verde para simular terreno mais natural
        altura = self.area_mapa.height
        largura = self.area_mapa.width
        for y in range(self.area_mapa.top, self.area_mapa.bottom):
            # Gradiente vertical de verde escuro para verde claro
            r = int(34 + (y - self.area_mapa.top) / altura * 40)
            g = int(100 + (y - self.area_mapa.top) / altura * 80)
            b = int(34 + (y - self.area_mapa.top) / altura * 20)
            pygame.draw.line(self.tela, (r, g, b), (self.area_mapa.left, y), (self.area_mapa.right, y))
        
        # Desenhar padrão de grama com variação de cor e formas mais naturais
        import random
        for _ in range(400):
            x = random.randint(self.area_mapa.left, self.area_mapa.right)
            y = random.randint(self.area_mapa.top, self.area_mapa.bottom)
            comprimento = random.randint(6, 12)
            angulo = random.uniform(-0.7, 0.7)  # Ângulo maior para variação
            x2 = x + comprimento * math.cos(angulo)
            y2 = y + comprimento * math.sin(angulo)
            cor_grama = (
                random.randint(30, 50),
                random.randint(120, 160),
                random.randint(30, 50)
            )
            pygame.draw.line(self.tela, cor_grama, (x, y), (x2, y2), 2)
        
        # Desenhar grid
        self.draw_grid()
        
        # Desenhar trilha
        self.draw_trilha()
        
        # Desenhar trator
        self.draw_trator()
        
        # Restaurar clipping
        self.tela.set_clip(clip_original)
        
        # Desenhar escala (fora do clipping)
        self.draw_escala()
        
    def centralizar_em_posicao_atual(self):
        """Centraliza o mapa na posição atual do trator"""
        if self.posicao_atual:
            self.sistema_coords.definir_centro(*self.posicao_atual)
            self.sistema_coords.resetar_offset()
            
    def ajustar_para_toda_trilha(self):
        """Ajusta o zoom para mostrar toda a trilha"""
        if len(self.trilha) > 1:
            self.sistema_coords.auto_ajustar_para_pontos(self.trilha)
            
    def limpar_trilha(self):
        """Limpa a trilha"""
        self.trilha.clear()
        self.posicao_atual = None
        self.direcao_atual = 0
