import pygame
import random
import sys
import math
import os

# Init
pygame.init()
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zombie Shooter 2D - Animated Edition")
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 26, bold=True)

# Inställning/ Kan ändras
PLAYER_SPEED = 4
BULLET_SPEED = 13
ZOMBIE_SPEED = 2
ZOMBIE_SIZE = (60, 60)
PLAYER_SIZE = (60, 60)
BULLET_SIZE = (10, 10)
HIGHSCORE_FILE = "highscore.txt"

# Ladda ssets
def load_animation_frames(folder, prefix, count, size):
    frames = []
    for i in range(count):
        # Vi använder os.path.join för att det ska funka på alla datorer
        path = os.path.join(folder, f"{prefix}_{i}.png")
        try:
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, size)
            frames.append(img)
        except:
            print(f"Kunde inte hitta: {path}")
    return frames

# Laddar in alla 17 frames för mina move animationer från min folder med alla bilder.
ZOMBIE_WALK_FRAMES = load_animation_frames("tds_zombie", "skeleton-move", 17, ZOMBIE_SIZE)

# Fallback om bilder saknas
if not ZOMBIE_WALK_FRAMES:
    dummy = pygame.Surface(ZOMBIE_SIZE)
    dummy.fill((255, 0, 0))
    ZOMBIE_WALK_FRAMES = [dummy]

# Ladda spelare och kula med bilderna jag har
try:
    player_img = pygame.image.load("player.png").convert_alpha()
    player_img = pygame.transform.scale(player_img, PLAYER_SIZE)
    bullet_img = pygame.image.load("bullet.png").convert_alpha()
    bullet_img = pygame.transform.scale(bullet_img, BULLET_SIZE)
except:
    player_img = pygame.Surface(PLAYER_SIZE); player_img.fill((0, 255, 0))
    bullet_img = pygame.Surface(BULLET_SIZE); bullet_img.fill((255, 255, 0))

# Funtkioner
def load_highscore():
    try:
        with open(HIGHSCORE_FILE, "r") as f: return int(f.read())
    except: return 0

def save_highscore(score):
    if score > load_highscore():
        with open(HIGHSCORE_FILE, "w") as f: f.write(str(score))

def spawn_zombie():
    side = random.choice(["top", "bottom", "left", "right"])
    w, h = ZOMBIE_SIZE
    if side == "top":    pos = [random.randint(0, WIDTH-w), -h]
    elif side == "bottom": pos = [random.randint(0, WIDTH-w), HEIGHT+h]
    elif side == "left":  pos = [-w, random.randint(0, HEIGHT-h)]
    else:                pos = [WIDTH+w, random.randint(0, HEIGHT-h)]
    
    # Returnerar en zombie dict
    return {
        "rect": pygame.Rect(pos[0], pos[1], w, h),
        "frame": 0.0,
        "angle": 0
    }

# Spel Loop
def game():
    player_rect = pygame.Rect(WIDTH//2, HEIGHT//2, *PLAYER_SIZE)
    bullets = []
    zombies = []
    score = 0
    high_score = load_highscore()

    while True:
        SCREEN.fill((40, 40, 40)) # Bakgrundsfärg, onödig nu

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullets.append(pygame.Rect(player_rect.centerx-5, player_rect.centery-5, *BULLET_SIZE))

        # Spelare Rörelse
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]: player_rect.x -= PLAYER_SPEED
        if keys[pygame.K_d]: player_rect.x += PLAYER_SPEED
        if keys[pygame.K_w]: player_rect.y -= PLAYER_SPEED
        if keys[pygame.K_s]: player_rect.y += PLAYER_SPEED
        player_rect.clamp_ip(SCREEN.get_rect())

        # Spawna zombies
        if random.randint(1, 50) == 1:
            zombies.append(spawn_zombie())

        # Kulor
        for b in bullets[:]:
            b.y -= BULLET_SPEED
            if b.bottom < 0: bullets.remove(b)

        # Zombie Logik
        for z in zombies[:]:
            # Flytta mot spelaren
            dx, dy = player_rect.x - z["rect"].x, player_rect.y - z["rect"].y
            dist = math.hypot(dx, dy)
            if dist != 0:
                z["rect"].x += (dx / dist) * ZOMBIE_SPEED
                z["rect"].y += (dy / dist) * ZOMBIE_SPEED
            
            # Beräkna vinkel (rotation) så de tittar på spelaren
            z["angle"] = math.degrees(math.atan2(-dy, dx)) - 90

            # Uppdatera animation (0.2 gör att den byter bild var 5:e frame)
            z["frame"] += 0.2
            if z["frame"] >= len(ZOMBIE_WALK_FRAMES):
                z["frame"] = 0

            # Kollision med spelare
            if z["rect"].colliderect(player_rect):
                save_highscore(score)
                return 

            # Kollision med kulor
            for b in bullets[:]:
                if z["rect"].colliderect(b):
                    if z in zombies: zombies.remove(z)
                    if b in bullets: bullets.remove(b)
                    score += 1
                    break

        
        # Rita kulor
        for b in bullets:
            SCREEN.blit(bullet_img, b)

        # Rita spelare
        SCREEN.blit(player_img, player_rect)

        # Rita animerade zombies
        for z in zombies:
            current_frame = ZOMBIE_WALK_FRAMES[int(z["frame"])]
            # Rotera bilden
            rotated_zombie = pygame.transform.rotate(current_frame, z["angle"])
            # Centrera den roterade bilden på recten
            new_rect = rotated_zombie.get_rect(center=z["rect"].center)
            SCREEN.blit(rotated_zombie, new_rect)

        # UI
        SCREEN.blit(FONT.render(f"Poäng: {score}", True, (255,255,255)), (20, 20))
        
        pygame.display.flip()
        CLOCK.tick(60)

# ---------------- START ----------------
def menu():
    while True:
        SCREEN.fill((20, 20, 20))
        SCREEN.blit(FONT.render("ZOMBIE SHOOTER: ANIMATED", True, (200, 0, 0)), (WIDTH//2-150, 200))
        SCREEN.blit(FONT.render("TRYCK [ENTER] FÖR ATT STARTA", True, (255, 255, 255)), (WIDTH//2-160, 280))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: game()
        
        pygame.display.flip()
        CLOCK.tick(15)

menu()