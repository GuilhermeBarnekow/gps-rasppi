import pygame
import time
from ui.components import Panel, Button, ToggleButton, MetricDisplay, Colors

class HUD:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        
        # Painel lateral direito
        self.painel_lateral = Panel((600, 20, 180, 440), Colors.BG_LIGHT, 
                                   title="Métricas")
        
        # Métricas
        self.metric_pontos = MetricDisplay((610, 60, 160, 40), "Pontos", "0")
        self.metric_largura = MetricDisplay((610, 110, 160, 40), "Largura", "--", "m")
        self.metric_area = MetricDisplay((610, 160, 160, 40), "Área", "0.00", "ha")
        self.metric_velocidade = MetricDisplay((610, 210, 160, 40), "Velocidade", "0.0", "km/h")
        self.metric_tempo = MetricDisplay((610, 260, 160, 40), "Tempo", "00:00")
        
        # Botões de controle
        self.btn_iniciar = ToggleButton((610, 320, 160, 40), "Iniciar Rota", 
                                      Colors.SECONDARY, Colors.TEXT_DISABLED)
        self.btn_exportar = Button((610, 370, 75, 40), "Export", Colors.PRIMARY)
        self.btn_limpar = Button((695, 370, 75, 40), "Limpar", Colors.DANGER)
        
        # Controle de tempo
        self.tempo_inicio = None
        self.tempo_pausado = 0
        
    def handle_event(self, event):
        """Manipula eventos dos botões"""
        resultados = {}
        
        if self.btn_iniciar.handle_event(event):
            self.btn_iniciar.toggle()
            resultados['iniciar_rota'] = self.btn_iniciar.active
            
            # Controle de tempo
            if self.btn_iniciar.active:
                if self.tempo_inicio is None:
                    self.tempo_inicio = time.time()
                else:
                    self.tempo_inicio = time.time() - self.tempo_pausado
            else:
                if self.tempo_inicio:
                    self.tempo_pausado = time.time() - self.tempo_inicio
                    
        if self.btn_exportar.handle_event(event):
            resultados['exportar'] = True
            
        if self.btn_limpar.handle_event(event):
            resultados['limpar'] = True
            self.tempo_inicio = None
            self.tempo_pausado = 0
            
        return resultados
    
    def update(self, count, largura, area, ativo, velocidade=None):
        """Atualiza as métricas do HUD"""
        self.metric_pontos.update(str(count))
        self.metric_largura.update(f"{largura:.1f}" if largura else "--")
        self.metric_area.update(f"{area:.2f}")
        
        if velocidade:
            self.metric_velocidade.update(f"{velocidade['atual']:.1f}")
        
        # Atualizar tempo
        if self.tempo_inicio and ativo:
            tempo_decorrido = time.time() - self.tempo_inicio
            minutos = int(tempo_decorrido // 60)
            segundos = int(tempo_decorrido % 60)
            self.metric_tempo.update(f"{minutos:02d}:{segundos:02d}")
        
        # Sincronizar estado do botão
        self.btn_iniciar.set_active(ativo)
        
    def draw(self):
        """Desenha o HUD"""
        # Desenhar painel lateral com sombra e transparência
        shadow_rect = self.painel_lateral.rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 100), shadow_surf.get_rect(), border_radius=self.painel_lateral.border_radius)
        self.screen.blit(shadow_surf, shadow_rect.topleft)
        
        # Painel com leve transparência
        panel_surf = pygame.Surface((self.painel_lateral.rect.width, self.painel_lateral.rect.height), pygame.SRCALPHA)
        panel_color = (*self.painel_lateral.bg_color, 220) if len(self.painel_lateral.bg_color) == 3 else self.painel_lateral.bg_color
        pygame.draw.rect(panel_surf, panel_color, panel_surf.get_rect(), border_radius=self.painel_lateral.border_radius)
        self.screen.blit(panel_surf, self.painel_lateral.rect.topleft)
        
        # Desenhar título
        if self.painel_lateral.title:
            title_surface = self.painel_lateral.title_font.render(self.painel_lateral.title, True, self.painel_lateral.title_color)
            title_rect = title_surface.get_rect(centerx=self.painel_lateral.rect.centerx, y=self.painel_lateral.rect.y + self.painel_lateral.padding)
            self.screen.blit(title_surface, title_rect)
        
        # Desenhar métricas
        self.metric_pontos.draw(self.screen)
        self.metric_largura.draw(self.screen)
        self.metric_area.draw(self.screen)
        self.metric_velocidade.draw(self.screen)
        self.metric_tempo.draw(self.screen)
        
        # Desenhar botões com efeitos de hover e pressed
        for btn in [self.btn_iniciar, self.btn_exportar, self.btn_limpar]:
            # Ajustar cor para hover e pressed
            if not btn.enabled:
                btn.color = btn.disabled_color
            elif btn.pressed:
                btn.color = btn.pressed_color
            elif btn.hover:
                btn.color = btn.hover_color
            else:
                btn.color = btn.base_color
            btn.draw(self.screen)
        
    def pode_iniciar_rota(self, largura):
        """Verifica se pode iniciar a rota"""
        return largura is not None and largura > 0
        
    def set_largura_disponivel(self, largura):
        """Habilita/desabilita botão baseado na largura"""
        self.btn_iniciar.enabled = self.pode_iniciar_rota(largura)
