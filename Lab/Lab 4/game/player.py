import pygame

SPEED = 4

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.vel_y = 0
        self.on_ground = False
        self.color = (60,160,220)
        self.stretch = 0   # frames of "launched" stretch animation left

    def launch(self, velocity):
        """Spring bounce: fire the player upward."""
        self.vel_y = velocity
        self.on_ground = False
        self.stretch = 18

    def update(self, keys, platforms, width):
        if self.stretch > 0:
            self.stretch -= 1
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx = -SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx = SPEED
        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground:
            self.vel_y = -13
            self.on_ground = False

        self.vel_y = min(self.vel_y + 0.55, 12)
        self.rect.x = max(0, min(width - self.rect.width, self.rect.x + dx))

        # Remember where the feet were BEFORE moving vertically this frame.
        prev_bottom = self.rect.bottom
        self.rect.y += int(self.vel_y)

        # One-way platform landing (bug fix):
        # Only land if we are moving down AND the feet were at/above the
        # platform's top edge before this frame's movement (small tolerance),
        # AND the feet have now reached/passed that top edge.
        # Jumping up through the underside, or grazing it, never snaps the
        # player on top any more. Using ">=" instead of colliderect also keeps
        # on_ground stable while standing still (no True/False flicker).
        self.on_ground = False
        landed_on = None
        for p in platforms:
            horizontally_over = self.rect.right > p.left and self.rect.left < p.right
            if (horizontally_over and self.vel_y >= 0
                    and prev_bottom <= p.top + 2
                    and self.rect.bottom >= p.top):
                self.rect.bottom = p.top
                self.vel_y = 0
                self.on_ground = True
                landed_on = p
                break
        return landed_on

    def draw(self, screen, cam_y):
        dr = self.rect.move(0, -int(cam_y))
        if self.stretch > 0:
            # stretched tall & thin while rocketing off a spring
            k = self.stretch / 18
            w = int(self.rect.width * (1 - 0.3 * k))
            h = int(self.rect.height * (1 + 0.45 * k))
            dr = pygame.Rect(0, 0, w, h)
            dr.midbottom = (self.rect.centerx, self.rect.bottom - int(cam_y))
        pygame.draw.rect(screen, self.color, dr, border_radius=6)
        pygame.draw.circle(screen,(255,220,180),(dr.centerx, dr.top+8),7)
