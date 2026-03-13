import pygame
import random
import sys
import math
import os

# ---------------- INIT ----------------
pygame.init()
WIDTH, HEIGHT = 1000, 800
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zombie Shooter - Advanced")
CLOCK = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 32, bold=True)
SMALL_FONT = pygame.font.SysFont("Arial", 20)

# ---------------- SETTINGS ----------------
PLAYER_SPEED = 4
BULLET_SPEED = 15
ZOMBIE_SPEED = 1.8
PLAYER_SIZE = (80, 80)
ZOMBIE_SIZE = (70, 70)
BULLET_SIZE = (15, 7) # Made it slightly rectangular for rotation visibility

# ---------------- LOAD ASSETS ----------------
def load_frames(folder_path, prefix, count, size):
    frames = []
    if not os.path.exists(folder_path):
        surf = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(surf, (200, 0, 0), (0, 0, *size))
        return [surf]
    for i in range(count):
        path = os.path.join(folder_path, f"{prefix}_{i}.png")
        if os.path.isfile(path):
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, size)
            frames.append(img)
    return frames if frames else [pygame.Surface(size)]

# Setup Animation Folders
P_BASE = "Player/rifle"
PLAYER_ANIMS = {
    "idle": load_frames(f"{P_BASE}/idle", "survivor-idle_rifle", 20, PLAYER_SIZE),
    "move": load_frames(f"{P_BASE}/move", "survivor-move_rifle", 20, PLAYER_SIZE),
    "shoot": load_frames(f"{P_BASE}/shoot", "survivor-shoot_rifle", 3, PLAYER_SIZE)
}
ZOMBIE_WALK = load_frames("tds_zombie", "skeleton-move", 17, ZOMBIE_SIZE)

# ---------------- LOAD BACKGROUND ----------------
bg_path = "backgrounds/background.png"  # sätt mappen rätt
if os.path.isfile(bg_path):
    background_img = pygame.image.load(bg_path).convert()
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
else:
    # fallback om filen inte finns
    background_img = pygame.Surface((WIDTH, HEIGHT))
    background_img.fill((30,30,35))

# ---------------- Bullet Setup ----------------
bullet_img_base = pygame.Surface(BULLET_SIZE, pygame.SRCALPHA)
pygame.draw.rect(bullet_img_base, (255, 220, 0), (0, 0, *BULLET_SIZE), border_radius=2)

# ---------------- HELPERS ----------------
def angle_to_target(src, dst):
    return math.atan2(dst[1] - src[1], dst[0] - src[0])

def get_anim_frame(anim_list, frame_index):
    return anim_list[int(frame_index) % len(anim_list)]

# ---------------- GAME LOOP ----------------
def game():
    player_pos = [WIDTH//2, HEIGHT//2]
    player_state = "idle"
    player_frame = 0
    player_rect = pygame.Rect(0, 0, 40, 40) # Smaller hitbox for player

    bullets = []
    zombies = []
    score = 0
    shoot_cooldown = 0
    game_over = False

    while True:
        # --- EVENT HANDLING ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_r:
                    game()
                    return

        if not game_over:
            # --- PLAYER INPUT ---
            mouse_pos = pygame.mouse.get_pos()
            keys = pygame.key.get_pressed()
            moving = False
            
            dx, dy = 0, 0
            if keys[pygame.K_a]: dx -= PLAYER_SPEED
            if keys[pygame.K_d]: dx += PLAYER_SPEED
            if keys[pygame.K_w]: dy -= PLAYER_SPEED
            if keys[pygame.K_s]: dy += PLAYER_SPEED
            
            player_pos[0] = max(0, min(WIDTH, player_pos[0] + dx))
            player_pos[1] = max(0, min(HEIGHT, player_pos[1] + dy))
            player_rect.center = player_pos
            
            if dx != 0 or dy != 0: moving = True

            # --- SHOOTING ---
            mouse_click = pygame.mouse.get_pressed()
            if (mouse_click[0] or keys[pygame.K_SPACE]) and shoot_cooldown == 0:
                player_state = "shoot"
                player_frame = 0
                angle = angle_to_target(player_pos, mouse_pos)
                
                m_off, s_off = 35, 12
                muzzle_x = player_pos[0] + math.cos(angle) * m_off - math.sin(angle) * s_off
                muzzle_y = player_pos[1] + math.sin(angle) * m_off + math.cos(angle) * s_off
                
                bullets.append({
                    "pos": [muzzle_x, muzzle_y],
                    "vel": [math.cos(angle) * BULLET_SPEED, math.sin(angle) * BULLET_SPEED],
                    "angle": -math.degrees(angle),
                    "rect": pygame.Rect(muzzle_x, muzzle_y, 10, 10)
                })
                shoot_cooldown = 12

            # --- ANIMATION LOGIC ---
            if player_state == "shoot":
                player_frame += 0.5
                if player_frame >= len(PLAYER_ANIMS["shoot"]):
                    player_state = "move" if moving else "idle"
                    player_frame = 0
            else:
                player_state = "move" if moving else "idle"
                player_frame += 0.2

            if shoot_cooldown > 0: shoot_cooldown -= 1

            # --- ZOMBIE SPAWNING ---
            if random.randint(1, 45) == 1:
                side = random.choice(["T", "B", "L", "R"])
                spawn_pos = {
                    "T": [random.randint(0, WIDTH), -50],
                    "B": [random.randint(0, WIDTH), HEIGHT+50],
                    "L": [-50, random.randint(0, HEIGHT)],
                    "R": [WIDTH+50, random.randint(0, HEIGHT)]
                }[side]
                zombies.append({
                    "pos": spawn_pos,
                    "frame": 0,
                    "rect": pygame.Rect(spawn_pos[0], spawn_pos[1], 40, 40)
                })

            # --- UPDATE ZOMBIES & BULLETS ---
            for z in zombies:
                z_angle = angle_to_target(z["pos"], player_pos)
                z["pos"][0] += math.cos(z_angle) * ZOMBIE_SPEED
                z["pos"][1] += math.sin(z_angle) * ZOMBIE_SPEED
                z["rect"].center = z["pos"]
                z["frame"] = (z["frame"] + 0.15) % len(ZOMBIE_WALK)
                
                if z["rect"].colliderect(player_rect):
                    game_over = True

            for b in bullets[:]:
                b["pos"][0] += b["vel"][0]
                b["pos"][1] += b["vel"][1]
                b["rect"].center = b["pos"]
                if not SCREEN.get_rect().collidepoint(b["pos"]):
                    bullets.remove(b)

            # --- COLLISIONS ---
            for b in bullets[:]:
                for z in zombies[:]:
                    if b["rect"].colliderect(z["rect"]):
                        if z in zombies: zombies.remove(z)
                        if b in bullets: bullets.remove(b)
                        score += 1
                        break

        # --- DRAWING ---
        SCREEN.blit(background_img, (0,0))  # <-- Draw background first

        # Draw Zombies
        for z in zombies:
            z_angle = -math.degrees(angle_to_target(z["pos"], player_pos))
            img = pygame.transform.rotate(get_anim_frame(ZOMBIE_WALK, z["frame"]), z_angle)
            SCREEN.blit(img, img.get_rect(center=z["pos"]))

        # Draw Bullets
        for b in bullets:
            b_img = pygame.transform.rotate(bullet_img_base, b["angle"])
            SCREEN.blit(b_img, b_img.get_rect(center=b["pos"]))

        # Draw Player
        p_angle = -math.degrees(angle_to_target(player_pos, mouse_pos))
        p_img = pygame.transform.rotate(get_anim_frame(PLAYER_ANIMS[player_state], player_frame), p_angle)
        SCREEN.blit(p_img, p_img.get_rect(center=player_pos))

        # UI
        score_surf = FONT.render(f"SCORE: {score}", True, (255, 255, 255))
        SCREEN.blit(score_surf, (20, 20))

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            SCREEN.blit(overlay, (0,0))
            msg = FONT.render("YOU DIED", True, (255, 0, 0))
            retry = SMALL_FONT.render("Press 'R' to Restart", True, (200, 200, 200))
            SCREEN.blit(msg, (WIDTH//2 - 70, HEIGHT//2 - 20))
            SCREEN.blit(retry, (WIDTH//2 - 85, HEIGHT//2 + 30))

        pygame.display.flip()
        CLOCK.tick(60)

if __name__ == "__main__":
    game()