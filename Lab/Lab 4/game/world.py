import pygame
import random
import math

PLATFORM_COLOR = (100,80,50)
CRUMBLE_COLOR = (150,95,70)
SPRING_COLOR = (240,210,40)
LAVA_COLOR = (220,60,20)

CRUMBLE_CHANCE = 0.22      # chance that a generated platform is unstable
CRUMBLE_FRAMES = 60        # 1 second at 60 FPS before it breaks
SPRING_CHANCE = 0.14       # chance that a generated platform is a spring
SPRING_VELOCITY = -22      # launch speed (normal jump is -13)
SPRING_ANIM_FRAMES = 24    # length of the recoil animation


class Platform(pygame.Rect):
    """A pygame.Rect with a platform type, so all existing Rect-based
    collision code keeps working unchanged."""
    def __init__(self, x, y, w, h, kind="normal"):
        super().__init__(x, y, w, h)
        self.kind = kind            # "normal" | "crumble" | "spring"
        self.crumble_timer = None   # frames left before breaking (None = not triggered)
        self.spring_anim = 0        # frames left in the spring recoil animation

    def trigger_spring(self):
        if self.kind == "spring":
            self.spring_anim = SPRING_ANIM_FRAMES

    def trigger_crumble(self):
        if self.kind == "crumble" and self.crumble_timer is None:
            self.crumble_timer = CRUMBLE_FRAMES


def generate_platforms(width, base_y, count=30):
    plats = [Platform(0, base_y, width, 20)]  # ground (always solid)
    y = base_y - 110
    for i in range(count):
        w = random.randint(80,200)
        x = random.randint(0, width-w)
        kind = "normal"
        # keep the first jump and the final (goal) platform solid
        if 0 < i < count-1:
            roll = random.random()
            if roll < CRUMBLE_CHANCE:
                kind = "crumble"
            elif roll < CRUMBLE_CHANCE + SPRING_CHANCE:
                kind = "spring"
        plats.append(Platform(x, y, w, 16, kind))
        y -= random.randint(80,130)
    return plats


def update_platforms(platforms):
    """Tick crumbling/spring timers and remove platforms that have broken."""
    for p in platforms[:]:
        if p.spring_anim > 0:
            p.spring_anim -= 1
        if p.crumble_timer is not None:
            p.crumble_timer -= 1
            if p.crumble_timer <= 0:
                platforms.remove(p)


def draw_platform(screen, p, cam_y, frame):
    dr = pygame.Rect(p).move(0, -int(cam_y))
    if p.kind == "crumble":
        color = CRUMBLE_COLOR
        if p.crumble_timer is not None:
            # shake harder and glow redder as the platform is about to break
            progress = 1 - p.crumble_timer / CRUMBLE_FRAMES
            amp = 1 + progress * 4
            dr.x += int(math.sin(frame * 1.7) * amp)
            dr.y += int(math.cos(frame * 2.3) * amp * 0.5)
            color = (min(255, 150 + int(progress * 100)), max(30, 95 - int(progress * 60)), 50)
        pygame.draw.rect(screen, color, dr, border_radius=4)
        # crack lines so unstable platforms are recognisable
        crack = (60,35,25)
        for cx in range(dr.left + 14, dr.right - 8, 26):
            pygame.draw.line(screen, crack, (cx, dr.top + 2), (cx + 5, dr.centery), 2)
            pygame.draw.line(screen, crack, (cx + 5, dr.centery), (cx - 2, dr.bottom - 2), 2)
    elif p.kind == "spring":
        # coil height: rest = 10px; on bounce it first squashes, then
        # overshoots and wobbles back (damped oscillation) = recoil animation
        coil_h = 10
        if p.spring_anim > 0:
            t = SPRING_ANIM_FRAMES - p.spring_anim
            coil_h = int(10 - 8 * math.cos(t * 0.55) * math.exp(-t * 0.12))
            coil_h = max(2, coil_h)
        # base
        pygame.draw.rect(screen, SPRING_COLOR, dr, border_radius=4)
        pygame.draw.rect(screen, (170,140,20), dr, 2, border_radius=4)
        # zig-zag coil + top pad drawn above the platform surface
        pad_w = min(60, dr.width - 10)
        left = dr.centerx - pad_w // 2
        steps = 8
        pts = [(left + k * pad_w / steps, dr.top - coil_h * (k % 2))
               for k in range(steps + 1)]
        pygame.draw.lines(screen, (200,200,210), False, pts, 2)
        pad = pygame.Rect(left - 4, dr.top - coil_h - 4, pad_w + 8, 4)
        glow = (255,255,140) if p.spring_anim > 0 else (255,235,90)
        pygame.draw.rect(screen, glow, pad, border_radius=2)
    else:
        pygame.draw.rect(screen, PLATFORM_COLOR, dr, border_radius=4)


def draw_lava(screen, lava_y, cam_y, width, height, frame):
    ly = int(lava_y - cam_y)
    if ly < height:
        # lava surface wave
        pts=[(0,ly)]
        for x in range(0,width+20,20):
            pts.append((x, ly + int(math.sin(x*0.08+frame*0.1)*8)))
        pts.append((width,height)); pts.append((0,height))
        pygame.draw.polygon(screen,LAVA_COLOR,pts)
        # glow
        s=pygame.Surface((width,30),pygame.SRCALPHA)
        for i in range(15):
            pygame.draw.line(s,(255,100,0,max(0,60-i*4)),(0,i),(width,i),1)
        screen.blit(s,(0,ly-15))
