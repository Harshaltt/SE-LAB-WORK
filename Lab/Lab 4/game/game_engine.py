import pygame
from game.player import Player
from game.world import generate_platforms, update_platforms, draw_platform, draw_lava, SPRING_VELOCITY

WIDTH,HEIGHT=500,640
FPS=60
BG=(20,15,30)
GROUND_Y=HEIGHT+200

# Lava settings
LAVA_RISE_START=0.4
LAVA_RISE_MAX=1.2
LAVA_RISE_ACCEL=0.0003
BURST_INTERVAL=15*FPS     # a Lava Burst every 15 seconds
BURST_DURATION=3*FPS      # each burst lasts 3 seconds
BURST_WARNING=1*FPS       # "incoming" warning shown 1 second before
BURST_MULT=2.2            # lava rises 2.2x faster during a burst
HUD_H=52

class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen=pygame.display.set_mode((WIDTH,HEIGHT))
        pygame.display.set_caption("Lava Escape")
        self.clock=pygame.time.Clock()
        self.font=pygame.font.SysFont("monospace",24,bold=True)
        self.big_font=pygame.font.SysFont("monospace",42,bold=True)
        self.small_font=pygame.font.SysFont("monospace",15,bold=True)
        self.reset()

    def reset(self):
        self.platforms=generate_platforms(WIDTH,GROUND_Y)
        self.player=Player(WIDTH//2-16,GROUND_Y-50)
        # Start the camera centred on the player (previously cam_y=0 left the
        # player and ground below the visible screen at the start of a run)
        self.cam_y=self.player.rect.centery-HEIGHT//2
        self.lava_y=GROUND_Y+60
        self.lava_rise=LAVA_RISE_START
        self.next_burst=BURST_INTERVAL   # frames until the next Lava Burst
        self.burst_timer=0               # frames left in the current burst
        self.score=0
        self.game_over=False
        self.won=False
        self.top_y=self.platforms[-1].y
        self.frame=0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type==pygame.QUIT: return False
            if event.type==pygame.KEYDOWN and event.key==pygame.K_r: self.reset()
        return True

    def update(self):
        if self.game_over or self.won: return
        keys=pygame.key.get_pressed()
        landed=self.player.update(keys,self.platforms,WIDTH)
        if landed is not None and landed.kind=="crumble":
            landed.trigger_crumble()
        if landed is not None and landed.kind=="spring":
            landed.trigger_spring()
            self.player.launch(SPRING_VELOCITY)
        update_platforms(self.platforms)
        target=self.player.rect.centery-HEIGHT//2
        if target<self.cam_y: self.cam_y=target
        # Lava Burst: every 15s the lava speeds up for 3s, then returns to normal
        self.next_burst-=1
        if self.next_burst<=0:
            self.burst_timer=BURST_DURATION
            self.next_burst=BURST_INTERVAL
        self.lava_y-=self.current_lava_speed()
        if self.burst_timer>0:
            self.burst_timer-=1
        self.lava_rise=min(LAVA_RISE_MAX,self.lava_rise+LAVA_RISE_ACCEL)
        self.score=max(0,(GROUND_Y-self.player.rect.y)//10)
        self.frame+=1
        if self.player.rect.bottom>=self.lava_y:
            self.game_over=True
        if self.player.rect.top<=self.top_y-20:
            self.won=True

    def current_lava_speed(self):
        return self.lava_rise*(BURST_MULT if self.burst_timer>0 else 1)

    def draw(self):
        self.screen.fill(BG)
        for p in self.platforms:
            draw_platform(self.screen,p,self.cam_y,self.frame)
        self.player.draw(self.screen,self.cam_y)
        draw_lava(self.screen,self.lava_y,self.cam_y,WIDTH,HEIGHT,self.frame)
        self._draw_hud()
        if not (self.game_over or self.won):
            self._draw_burst_warning()
        if self.game_over:
            self._msg("LAVA GOT YOU!",(220,80,40))
        if self.won:
            self._msg("ESCAPED!",(80,220,100))
        pygame.display.flip()

    def _draw_hud(self):
        # translucent panel so the HUD never overlaps platforms unreadably
        panel=pygame.Surface((WIDTH,HUD_H),pygame.SRCALPHA)
        panel.fill((0,0,0,140))
        self.screen.blit(panel,(0,0))
        sc=self.font.render(f"Height: {self.score}m",True,(220,200,180))
        self.screen.blit(sc,(8,4))
        secs=(self.next_burst+FPS-1)//FPS
        info=self.small_font.render(f"R=Restart  Burst in {secs:>2}s",True,(170,160,150))
        self.screen.blit(info,(8,32))

        # Danger meter: fills as self.lava_rise increases
        bw,bh=150,14
        bx,by=WIDTH-bw-10,30
        fill=(self.lava_rise-LAVA_RISE_START)/(LAVA_RISE_MAX-LAVA_RISE_START)
        fill=max(0.0,min(1.0,fill))
        bursting=self.burst_timer>0
        # colour goes green -> yellow -> red as danger grows
        if fill<0.5:
            col=(int(80+350*fill),200,60)
        else:
            col=(255,int(200-300*(fill-0.5)),40)
        border=(200,180,160)
        if bursting and (self.frame//6)%2==0:
            border=(255,60,20)   # meter border flashes during a Lava Burst
        pygame.draw.rect(self.screen,(50,40,40),(bx,by,bw,bh),border_radius=4)
        pygame.draw.rect(self.screen,col,(bx,by,int(bw*fill),bh),border_radius=4)
        pygame.draw.rect(self.screen,border,(bx,by,bw,bh),2,border_radius=4)
        # speed readout relative to the starting lava speed
        speed=self.current_lava_speed()/LAVA_RISE_START
        label="BURST!" if bursting else "DANGER"
        lt=self.small_font.render(f"{label}  LAVA x{speed:.1f}",True,
                                  (255,120,60) if bursting else (220,200,180))
        self.screen.blit(lt,(bx+bw-lt.get_width(),by-20))

    def _draw_burst_warning(self):
        bursting=self.burst_timer>0
        incoming=self.next_burst<=BURST_WARNING and not bursting
        if not (bursting or incoming):
            return
        blink=(self.frame//8)%2==0
        if bursting:
            # pulsing red edges while the lava surges
            a=90 if blink else 40
            edge=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
            pygame.draw.rect(edge,(255,40,0,a),(0,0,WIDTH,HEIGHT),14)
            self.screen.blit(edge,(0,0))
            secs=(self.burst_timer+FPS-1)//FPS
            t=self.big_font.render("LAVA BURST!",True,(255,90,30) if blink else (255,200,60))
            sub=self.small_font.render(f"Lava rising {BURST_MULT}x faster for {secs}s",True,(255,210,170))
            self.screen.blit(t,(WIDTH//2-t.get_width()//2,HUD_H+16))
            self.screen.blit(sub,(WIDTH//2-sub.get_width()//2,HUD_H+64))
        elif blink:
            t=self.font.render("! LAVA BURST INCOMING !",True,(255,170,60))
            self.screen.blit(t,(WIDTH//2-t.get_width()//2,HUD_H+16))

    def _msg(self,text,color):
        ov=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        ov.fill((0,0,0,150))
        self.screen.blit(ov,(0,0))
        m=self.big_font.render(text,True,color)
        s=self.font.render("Press R to Play Again",True,(200,200,200))
        self.screen.blit(m,(WIDTH//2-m.get_width()//2,HEIGHT//2-40))
        self.screen.blit(s,(WIDTH//2-s.get_width()//2,HEIGHT//2+20))

    def run(self):
        running=True
        while running:
            running=self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
