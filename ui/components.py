import pygame
import math

# Paleta de cores moderna
class Colors:
    PRIMARY = (52, 152, 219)      # Azul moderno
    SECONDARY = (46, 204, 113)    # Verde
    ACCENT = (241, 196, 15)       # Amarelo/dourado
    DANGER = (231, 76, 60)        # Vermelho
    WARNING = (230, 126, 34)      # Laranja
    
    BG_DARK = (33, 37, 41)        # Fundo escuro
    BG_LIGHT = (52, 58, 64)       # Fundo claro
    
    TEXT_PRIMARY = (255, 255, 255)
    TEXT_SECONDARY = (174, 182, 191)
    TEXT_DISABLED = (108, 117, 125)
    
    SHADOW = (0, 0, 0, 100)

class Button:
    def __init__(self, rect, text, color=Colors.PRIMARY, text_color=Colors.TEXT_PRIMARY, 
                 font_size=24, border_radius=8, icon=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.Font(None, font_size)
        self.border_radius = border_radius
        self.icon = icon
        self.pressed = False
        self.hover = False
        self.enabled = True
        
        # Estados visuais
        self.base_color = color
        self.hover_color = tuple(min(255, c + 30) for c in color)
        self.pressed_color = tuple(max(0, c - 30) for c in color)
        self.disabled_color = Colors.TEXT_DISABLED
        
    def handle_event(self, event):
        if not self.enabled:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                # Do not return True here to avoid double toggle
                return False
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed and self.rect.collidepoint(event.pos):
                self.pressed = False
                return True
            self.pressed = False
        elif event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
            
        return False
    
    def draw(self, screen):
        # Determinar cor baseada no estado
        if not self.enabled:
            color = self.disabled_color
        elif self.pressed:
            color = self.pressed_color
        elif self.hover:
            color = self.hover_color
        else:
            color = self.base_color
            
        # Desenhar sombra
        shadow_rect = self.rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        pygame.draw.rect(screen, (0, 0, 0, 50), shadow_rect, border_radius=self.border_radius)
        
        # Desenhar botão
        pygame.draw.rect(screen, color, self.rect, border_radius=self.border_radius)
        
        # Desenhar texto
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class Panel:
    def __init__(self, rect, bg_color=Colors.BG_LIGHT, border_radius=12, 
                 title=None, title_color=Colors.TEXT_PRIMARY):
        self.rect = pygame.Rect(rect)
        self.bg_color = bg_color
        self.border_radius = border_radius
        self.title = title
        self.title_color = title_color
        self.title_font = pygame.font.Font(None, 28)
        self.padding = 10
        
    def draw(self, screen):
        # Desenhar sombra
        shadow_rect = self.rect.copy()
        shadow_rect.x += 3
        shadow_rect.y += 3
        pygame.draw.rect(screen, (0, 0, 0, 80), shadow_rect, border_radius=self.border_radius)
        
        # Desenhar painel
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=self.border_radius)
        
        # Desenhar título se existir
        if self.title:
            title_surface = self.title_font.render(self.title, True, self.title_color)
            title_rect = title_surface.get_rect(centerx=self.rect.centerx, 
                                              y=self.rect.y + self.padding)
            screen.blit(title_surface, title_rect)
    
    def get_content_rect(self):
        """Retorna retângulo disponível para conteúdo"""
        title_height = 35 if self.title else 0
        return pygame.Rect(
            self.rect.x + self.padding,
            self.rect.y + self.padding + title_height,
            self.rect.width - 2 * self.padding,
            self.rect.height - 2 * self.padding - title_height
        )

class ToggleButton(Button):
    def __init__(self, rect, text, active_color=Colors.SECONDARY, 
                 inactive_color=Colors.TEXT_DISABLED, **kwargs):
        super().__init__(rect, text, **kwargs)
        self.active_color = active_color
        self.inactive_color = inactive_color
        self.active = False
        
    def toggle(self):
        self.active = not self.active
        self.color = self.active_color if self.active else self.inactive_color
        self.base_color = self.color
        
    def set_active(self, active):
        self.active = active
        self.color = self.active_color if self.active else self.inactive_color
        self.base_color = self.color

class ProgressBar:
    def __init__(self, rect, max_value=100, color=Colors.PRIMARY, 
                 bg_color=Colors.BG_DARK, border_radius=4):
        self.rect = pygame.Rect(rect)
        self.max_value = max_value
        self.value = 0
        self.color = color
        self.bg_color = bg_color
        self.border_radius = border_radius
        
    def set_value(self, value):
        self.value = max(0, min(self.max_value, value))
        
    def draw(self, screen):
        # Desenhar background
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=self.border_radius)
        
        # Desenhar progresso
        if self.value > 0:
            progress_width = int((self.value / self.max_value) * self.rect.width)
            progress_rect = pygame.Rect(self.rect.x, self.rect.y, 
                                      progress_width, self.rect.height)
            pygame.draw.rect(screen, self.color, progress_rect, border_radius=self.border_radius)

class IconButton(Button):
    def __init__(self, rect, icon_path, color=Colors.PRIMARY, **kwargs):
        super().__init__(rect, "", color, **kwargs)
        self.icon_path = icon_path
        self.icon_surface = None
        self.load_icon()
        
    def load_icon(self):
        try:
            # Carregar ícone SVG seria ideal, mas para simplificar usando círculos coloridos
            self.icon_surface = pygame.Surface((24, 24), pygame.SRCALPHA)
            pygame.draw.circle(self.icon_surface, Colors.TEXT_PRIMARY, (12, 12), 10)
        except:
            self.icon_surface = None
            
    def draw(self, screen):
        super().draw(screen)
        if self.icon_surface:
            icon_rect = self.icon_surface.get_rect(center=self.rect.center)
            screen.blit(self.icon_surface, icon_rect)

class MetricDisplay:
    def __init__(self, rect, title, value="--", unit="", font_size=20):
        self.rect = pygame.Rect(rect)
        self.title = title
        self.value = value
        self.unit = unit
        self.title_font = pygame.font.Font(None, font_size)
        self.value_font = pygame.font.Font(None, font_size + 8)
        
    def update(self, value, unit=None):
        self.value = value
        if unit:
            self.unit = unit
            
    def draw(self, screen):
        # Desenhar título
        title_surface = self.title_font.render(self.title, True, Colors.TEXT_SECONDARY)
        title_rect = title_surface.get_rect(centerx=self.rect.centerx, y=self.rect.y)
        screen.blit(title_surface, title_rect)
        
        # Desenhar valor
        value_text = f"{self.value} {self.unit}".strip()
        value_surface = self.value_font.render(value_text, True, Colors.TEXT_PRIMARY)
        value_rect = value_surface.get_rect(centerx=self.rect.centerx, 
                                          y=self.rect.y + title_rect.height + 5)
        screen.blit(value_surface, value_rect)

def draw_rounded_rect(surface, color, rect, radius):
    """Desenha retângulo com cantos arredondados"""
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    
def lerp(start, end, t):
    """Interpolação linear para animações"""
    return start + t * (end - start)

class Animation:
    def __init__(self, duration, start_value, end_value, easing=None):
        self.duration = duration
        self.start_value = start_value
        self.end_value = end_value
        self.current_time = 0
        self.current_value = start_value
        self.finished = False
        self.easing = easing or self.linear
        
    def update(self, dt):
        if self.finished:
            return self.current_value
            
        self.current_time += dt
        if self.current_time >= self.duration:
            self.current_time = self.duration
            self.finished = True
            
        t = self.current_time / self.duration
        t = self.easing(t)
        
        if isinstance(self.start_value, (int, float)):
            self.current_value = lerp(self.start_value, self.end_value, t)
        else:
            # Para tuplas (cores, posições)
            self.current_value = tuple(lerp(s, e, t) for s, e in zip(self.start_value, self.end_value))
            
        return self.current_value
    
    @staticmethod
    def linear(t):
        return t
    
    @staticmethod
    def ease_in_out(t):
        return t * t * (3 - 2 * t)
    
    @staticmethod
    def ease_out_bounce(t):
        if t < 1/2.75:
            return 7.5625 * t * t
        elif t < 2/2.75:
            return 7.5625 * (t - 1.5/2.75) * (t - 1.5/2.75) + 0.75
        elif t < 2.5/2.75:
            return 7.5625 * (t - 2.25/2.75) * (t - 2.25/2.75) + 0.9375
        else:
            return 7.5625 * (t - 2.625/2.75) * (t - 2.625/2.75) + 0.984375 