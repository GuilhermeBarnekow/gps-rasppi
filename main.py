import pygame
import sys
from ui.mapa import Mapa
# Removed import of TecladoVirtual
from ui.widgets import HUD
from ui.components import Colors
from gnss import GNSSManager
from utils.area_calc import calcular_area
from utils.haversine import haversine
from utils.velocimetro import Velocimetro
from utils.exportacao import ExportadorDados
import db

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 480), pygame.FULLSCREEN)
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()

    # Setup database
    db.criar_banco()

    # Obter informações da fazenda
    fazenda = db.obter_fazenda()
    largura = None
    nome_fazenda = None

    if fazenda:
        nome_fazenda = fazenda['nome']
        largura = fazenda['largura_implemento']
    else:
        # Solicitar entrada do usuário para nome da fazenda e largura do implemento
        import tkinter as tk
        from tkinter import simpledialog

        root = tk.Tk()
        root.withdraw()  # Ocultar janela principal

        nome_fazenda = simpledialog.askstring("Entrada", "Digite o nome da fazenda:")
        largura_str = simpledialog.askstring("Entrada", "Digite a largura do implemento (m):")

        try:
            largura = float(largura_str)
        except (ValueError, TypeError):
            largura = None

        if nome_fazenda and largura:
            db.salvar_fazenda(nome_fazenda, largura)
        else:
            print("Informações da fazenda inválidas. Encerrando.")
            pygame.quit()
            sys.exit()

    # Sistemas principais
    gnss_manager = GNSSManager(baudrate=115200)
    velocimetro = Velocimetro()
    exportador = ExportadorDados()
    
    # Ativar modo simulação para desenvolvimento (comentar para usar GPS real)
    gnss_manager.ativar_modo_simulacao()

    # UI components
    mapa = Mapa(screen)
    hud = HUD(screen)

    rota_ativa = False
    pontos = []
    area_acumulada = 0.0

    running = True
    while running:
        # Background gradient
        screen.fill(Colors.BG_DARK)
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # ESC para sair
                if event.key == pygame.K_ESCAPE:
                    running = False
                # F1 para alternar modo simulação
                elif event.key == pygame.K_F1:
                    if gnss_manager.modo_simulacao:
                        gnss_manager.desativar_modo_simulacao()
                    else:
                        gnss_manager.ativar_modo_simulacao()

            # Handle map events
            mapa.handle_event(event)
            
            # Handle HUD events
            hud_eventos = hud.handle_event(event)
            
            # Processar eventos do HUD
            if 'iniciar_rota' in hud_eventos:
                if largura is not None:
                    rota_ativa = hud_eventos['iniciar_rota']
                    if rota_ativa:
                        velocimetro.reset()
                        
            if 'exportar' in hud_eventos:
                try:
                    arquivo = exportador.exportar_csv()
                    print(f"Dados exportados para: {arquivo}")
                except Exception as e:
                    print(f"Erro ao exportar: {e}")
                    
            if 'limpar' in hud_eventos:
                try:
                    exportador.limpar_dados()
                    pontos.clear()
                    area_acumulada = 0.0
                    mapa.limpar_trilha()
                    velocimetro.reset()
                    print("Dados limpos")
                except Exception as e:
                    print(f"Erro ao limpar: {e}")

        # Update GNSS when route active
        if rota_ativa and largura is not None:
            dados_gnss = gnss_manager.ler_ponto_gnss()
            if dados_gnss:
                # Extrair coordenadas básicas
                lat, lon = dados_gnss[0], dados_gnss[1]
                ponto_coordenadas = (lat, lon)
                
                # Extrair velocidade e direção se disponíveis
                velocidade_gnss = dados_gnss[2] if len(dados_gnss) > 2 else 0
                direcao_gnss = dados_gnss[3] if len(dados_gnss) > 3 else 0
                
                pontos.append(ponto_coordenadas)
                mapa.add_point(ponto_coordenadas)
                velocimetro.adicionar_ponto(lat, lon)
                
                # Usar velocidade do GNSS se disponível
                if velocidade_gnss > 0:
                    velocimetro.velocidade_atual = velocidade_gnss
                    velocimetro.usando_gnss = True
                else:
                    velocimetro.usando_gnss = False
                
                # Calcular área apenas se temos pontos anteriores
                if len(pontos) > 1:
                    d = haversine(*pontos[-2], *pontos[-1])
                    area = calcular_area(d, largura)
                    area_acumulada += area
                    db.salvar_ponto(lat, lon, area)

        # Draw everything
        mapa.draw()
        
        # Update HUD with velocity data
        velocidade_dados = velocimetro.obter_velocidade()
        hud.update(len(pontos), largura, area_acumulada, rota_ativa, velocidade_dados)
        hud.draw()
        
        # Draw status information
        draw_status_info(screen, gnss_manager, velocimetro)

        pygame.display.flip()
        clock.tick(30)

    # Cleanup
    gnss_manager.desconectar()
    pygame.quit()
    sys.exit()

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
