import pygame

class TecladoVirtual:
    def __init__(self, screen, rect):
        self.screen = screen
        self.rect = pygame.Rect(rect)
        self.font = pygame.font.Font(None, 40)
        labels = [('1',(0,0)),('2',(1,0)),('3',(2,0)),('4',(0,1)),('5',(1,1)),('6',(2,1)),('7',(0,2)),('8',(1,2)),('9',(2,2)),('←',(0,3)),('0',(1,3)),('OK',(2,3))]
        w,h = self.rect.width//3, self.rect.height//4
        self.buttons=[]
        for lab,(c,r) in labels:
            self.buttons.append((lab, pygame.Rect(self.rect.x+c*w, self.rect.y+r*h, w,h)))
        self.value=""
        self.visible=True

    def handle_event(self, event):
        if not self.visible or event.type!=pygame.MOUSEBUTTONDOWN: return False
        for lab,btn in self.buttons:
            if btn.collidepoint(event.pos):
                if lab=='←': self.value=self.value[:-1]
                elif lab=='OK': return True
                else: self.value+=lab
        return False

    def draw(self):
        if not self.visible: return
        pygame.draw.rect(self.screen,(50,50,50),self.rect)
        for lab,btn in self.buttons:
            pygame.draw.rect(self.screen,(200,200,200),btn,border_radius=5)
            t=self.font.render(lab,True,(0,0,0))
            tw,th=t.get_size()
            self.screen.blit(t,(btn.x+(btn.width-tw)//2,btn.y+(btn.height-th)//2))
        v=self.font.render(self.value,True,(255,255,255))
        self.screen.blit(v,(self.rect.x+10,self.rect.y-50))

    def hide(self):
        self.visible=False
