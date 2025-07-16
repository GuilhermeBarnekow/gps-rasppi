import pygame
import sys
import time
# Removed import of Mapa and TecladoVirtual
import time

from ui.widgets import HUD
from ui.components import Colors, Button
from gnss import GNSSManager
from utils.area_calc import calcular_area
from utils.haversine import haversine
from utils.velocimetro import Velocimetro
from utils.exportacao import ExportadorDados
import db
from utils.detect_gps_port import detectar_porta_gps

def mostrar_resumo_fazendas(screen, clock):
    """Mostra a tela de resumo da fazenda registrada antes da interface principal"""
    font_titulo = pygame.font.Font(None, 48)
    font_texto = pygame.font.Font(None, 32)
    largura_tela, altura_tela = screen.get_size()
    
    # Botão para continuar
    btn_continuar = Button((largura_tela//2 - 100, altura_tela - 80, 200, 50), "Continuar", Colors.SECONDARY)
    
    # Obter fazenda e hectares percorridos do banco
    fazenda = db.obter_fazenda()
    hectares_totais = db.obter_hectares_totais()
    
    running = True
    while running:
        screen.fill(Colors.BG_DARK)
        
        # Título
        titulo_surface = font_titulo.render("Fazenda Registrada", True, Colors.TEXT_PRIMARY)
        titulo_rect = titulo_surface.get_rect(center=(largura_tela//2, 50))
        screen.blit(titulo_surface, titulo_rect)
        
        # Mostrar dados da fazenda
        y_offset = 120
        if fazenda:
            nome = fazenda.get('nome', 'Desconhecida')
            texto = f"{nome} - {hectares_totais:.2f} ha percorridos"
        else:
            texto = "Nenhuma fazenda registrada"
        texto_surface = font_texto.render(texto, True, Colors.TEXT_SECONDARY)
        texto_rect = texto_surface.get_rect(center=(largura_tela//2, y_offset))
        screen.blit(texto_surface, texto_rect)
        
        # Desenhar botão continuar
        btn_continuar.draw(screen)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                if btn_continuar.handle_event(event):
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                btn_continuar.handle_event(event)
            elif event.type == pygame.MOUSEMOTION:
                btn_continuar.handle_event(event)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        
        pygame.display.flip()
        clock.tick(30)

from ui.kivy_interface import GPSApp
import sys

def main():
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((840, 480))
    clock = pygame.time.Clock()

    # Show initial farm summary screen
    mostrar_resumo_fazendas(screen, clock)

    # Quit pygame display before launching Kivy app
    pygame.display.quit()

    # Launch the Kivy GPS app
    GPSApp().run()

def draw_status_info(screen, gnss_manager, velocimetro):
    """Desenha informações de status no canto inferior esquerdo"""
    font = pygame.font.Font(None, 20)
    y_offset = 400
    
    # Status GNSS
    status_gnss = gnss_manager.obter_status()
    cor_status = Colors.SECONDARY if status_gnss['conectado'] else Colors.DANGER
    
    if status_gnss['modo_simulacao']:
        texto_gnss = "GPS: SIMULAÇÃO"
        cor_status = Colors.WARNING
    elif status_gnss['conectado']:
        texto_gnss = f"GPS: OK ({status_gnss['taxa_sucesso']:.1f}%)"
    else:
        texto_gnss = "GPS: DESCONECTADO"
    
    surface = font.render(texto_gnss, True, cor_status)
    screen.blit(surface, (10, y_offset))
    
    # Velocidade (mostra se é do GNSS ou calculada)
    velocidade_info = velocimetro.obter_velocidade()
    fonte_vel = "GNSS" if hasattr(velocimetro, 'usando_gnss') and velocimetro.usando_gnss else "Calc"
    texto_vel = f"Vel: {velocidade_info['atual']:.1f} km/h ({fonte_vel})"
    surface = font.render(texto_vel, True, Colors.TEXT_SECONDARY)
    screen.blit(surface, (10, y_offset + 20))
    
    # Controles
    texto_controles = "ESC: Sair | F1: Alternar Simulação"
    surface = font.render(texto_controles, True, Colors.TEXT_DISABLED)
    screen.blit(surface, (10, y_offset + 40))

if __name__ == '__main__':
    main()
