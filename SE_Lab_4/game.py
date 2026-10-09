import pygame
import random
import math
import time

WIDTH, HEIGHT = 800, 560
FPS = 60
BG = (30,35,25)



class Zombie:
    TYPES = {
        "normal": {
            "size": 30,
            "speed": 1.5,
            "hp": 3,
            "color": (60, 140, 60),
        },
        "fast": {
            "size": 20,
            "speed": 3.0,
            "hp": 1,
            "color": (80, 220, 100),
        },
        "tank": {
            "size": 44,
            "speed": 0.8,
            "hp": 6,
            "color": (100, 70, 130),
        },
    }

    def __init__(self, x, y, zombie_type="normal"):
        stats = self.TYPES[zombie_type]

        self.zombie_type = zombie_type
        self.size = stats["size"]
        self.SPEED = stats["speed"]
        self.hp = stats["hp"]
        self.color = stats["color"]

        self.rect = pygame.Rect(x, y, self.size, self.size)
        self.wobble = random.uniform(0, 6.28)
        self.frame = 0

    def update(self, player_pos):
        px, py = player_pos
        cx, cy = self.rect.center
        dx, dy = px - cx, py - cy
        dist = (dx**2 + dy**2)**0.5

        if dist:
            self.rect.x += int(dx / dist * self.SPEED)
            self.rect.y += int(dy / dist * self.SPEED)

        self.frame += 1

    def hit(self):
        self.hp -= 1
        return self.hp <= 0

    def draw(self, screen):
        wobble_y = int(math.sin(self.frame * 0.2) * 3)
        draw_rect = self.rect.move(0, wobble_y)

        pygame.draw.rect(
            screen, self.color, draw_rect, border_radius=5
        )

        # Position the eyes proportionally to the zombie's size
        eye_y = draw_rect.y + self.size // 3
        eye_radius = max(2, self.size // 10)

        for eye_x in (
            draw_rect.x + self.size // 4,
            draw_rect.x + 3 * self.size // 4,
        ):
            pygame.draw.circle(
                screen, (200, 40, 40),
                (eye_x, eye_y), eye_radius
            )


def spawn_zombie(width, height, player_rect, margin=120,
                 zombie_type="normal"):
    size = Zombie.TYPES[zombie_type]["size"]

    while True:
        x = random.randint(0, width - size)
        y = random.randint(0, height - size)

        rect = pygame.Rect(x, y, size, size)

        if not rect.colliderect(player_rect.inflate(margin, margin)):
            return Zombie(x, y, zombie_type)

SPEED = 4


class Barrel:
    SIZE = 28
    EXPLOSION_RADIUS = 100

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, self.SIZE, self.SIZE)
        self.exploding = False
        self.explosion_start = 0
        self.explosion_duration = 300  # milliseconds

    def explode(self):
        self.exploding = True
        self.explosion_start = pygame.time.get_ticks()

    def update(self):
        if self.exploding:
            elapsed = pygame.time.get_ticks() - self.explosion_start
            return elapsed < self.explosion_duration
        return True

    def draw(self, screen):
        if self.exploding:
            elapsed = pygame.time.get_ticks() - self.explosion_start
            progress = min(1, elapsed / self.explosion_duration)
            radius = int(self.EXPLOSION_RADIUS * progress)

            pygame.draw.circle(
                screen, (255, 130, 20),
                self.rect.center, radius, 4
            )
            pygame.draw.circle(
                screen, (255, 220, 60),
                self.rect.center, max(2, radius // 3)
            )
        else:
            pygame.draw.rect(
                screen, (160, 65, 35), self.rect,
                border_radius=5
            )
            pygame.draw.rect(
                screen, (90, 45, 25), self.rect,
                width=3, border_radius=5
            )
            pygame.draw.line(
                screen, (220, 160, 70),
                (self.rect.left + 5, self.rect.centery),
                (self.rect.right - 5, self.rect.centery), 3
            )

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.color = (60,160,220)
        self.bullets = []
        self.shoot_cooldown = 0
            # Task 1: Health system
        self.health = 3
        self.max_health = 3
        self.invincible_until = 0
        self.invincibility_duration = 1000  # 1 second, in milliseconds

        
        # Task 2: Ammo system
        self.max_ammo = 12
        self.ammo = 12
        self.is_reloading = False
        self.reload_duration = 2000  # 2 seconds in milliseconds
        self.reload_end_time = 0
        
    def move(self, keys, width, height):
        dx = dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]: dy = -SPEED
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy = SPEED
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx = -SPEED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx = SPEED
        self.rect.x = max(0, min(width-self.rect.width, self.rect.x+dx))
        self.rect.y = max(0, min(height-self.rect.height, self.rect.y+dy))
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        self.update_reload()

    def take_damage(self):
        now = pygame.time.get_ticks()

        # Ignore damage while the player is invincible
        if now < self.invincible_until:
            return False

        # Do not reduce health below zero
        if self.health <= 0:
            return False

        # Apply one hit
        self.health -= 1

        # Start the invincibility period
        self.invincible_until = now + self.invincibility_duration

        return True
    

    def shoot(self, target_pos):
        if self.shoot_cooldown > 0 or self.is_reloading:
            return

        # Cannot shoot with an empty clip
        if self.ammo <= 0:
            self.start_reload()
            return

        cx, cy = self.rect.center
        tx, ty = target_pos
        dx, dy = tx - cx, ty - cy
        dist = (dx**2 + dy**2)**0.5

        if dist == 0:
            return

        vx, vy = dx / dist * 10, dy / dist * 10

        self.bullets.append([cx - 4, cy - 4, vx, vy])

        self.ammo -= 1
        self.shoot_cooldown = 15

        # Automatically reload after the last bullet
        if self.ammo == 0:
            self.start_reload()
            

    def start_reload(self):
        if self.is_reloading or self.ammo == self.max_ammo:
            return

        self.is_reloading = True
        self.reload_end_time = (
            pygame.time.get_ticks() + self.reload_duration
        )

    def update_reload(self):
        if not self.is_reloading:
            return

        now = pygame.time.get_ticks()

        if now >= self.reload_end_time:
            self.ammo = self.max_ammo
            self.is_reloading = False
                        
            
    def update_bullets(self, width, height):
        live = []
        for b in self.bullets:
            b[0] += b[2]; b[1] += b[3]
            if 0 <= b[0] <= width and 0 <= b[1] <= height:
                live.append(b)
        self.bullets = live


    def draw(self, screen):
        now = pygame.time.get_ticks()

        # Blink the player during the invincibility period
        if (
            now >= self.invincible_until
            or (now // 100) % 2 == 0
        ):
            pygame.draw.rect(
                screen, self.color, self.rect, border_radius=6
            )

        # Bullets remain visible while the player blinks
        for b in self.bullets:
            pygame.draw.circle(
                screen, (255,220,60),
                (int(b[0]), int(b[1])), 5
            )

class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Zombie Escape")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 24)
        self.big_font = pygame.font.SysFont("monospace", 44, bold=True)
        self.reset()

    def reset(self):
        self.player = Player(WIDTH//2, HEIGHT//2)
        self.zombies = [spawn_zombie(WIDTH, HEIGHT, self.player.rect) for _ in range(4)]
    
        # Task 3: Spawn four barrels away from the player
        self.barrels = []

        while len(self.barrels) < 4:
            x = random.randint(10, WIDTH - Barrel.SIZE - 10)
            y = random.randint(70, HEIGHT - Barrel.SIZE - 10)

            new_rect = pygame.Rect(x, y, Barrel.SIZE, Barrel.SIZE)

            # Avoid placing barrels too close to the player
            if new_rect.colliderect(self.player.rect.inflate(100, 100)):
                continue

            # Keep barrels separated from one another
            if any(new_rect.colliderect(b.rect.inflate(20, 20))
                   for b in self.barrels):
                continue

            self.barrels.append(Barrel(x, y))
        self.score = 0
        self.wave = 1
        self.kills = 0
        self.kills_to_next = 8
        self.game_over = False
        self.start_time = time.time()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r: self.reset()
            if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                self.player.shoot(event.pos)
        return True

    def update(self):
        if self.game_over: return
        keys = pygame.key.get_pressed()
        self.player.move(keys, WIDTH, HEIGHT)
        self.player.update_bullets(WIDTH, HEIGHT)
        self.score = int(time.time() - self.start_time)

        for z in self.zombies:
            z.update(self.player.rect.center)

            if z.rect.colliderect(self.player.rect):
                self.player.take_damage()

                # End the game only when health reaches zero
                if self.player.health <= 0:
                    self.game_over = True
                    break

        dead = []
        
        # Task 3: Check bullet collisions with barrels
        for barrel in self.barrels[:]:
            if barrel.exploding:
                continue

            for b in self.player.bullets[:]:
                bx, by = int(b[0]), int(b[1])

                if barrel.rect.collidepoint(bx, by):
                    # Consume the bullet
                    if b in self.player.bullets:
                        self.player.bullets.remove(b)

                    # Trigger the explosion
                    barrel.explode()

                    # Damage all zombies inside the explosion radius
                    for z in self.zombies[:]:
                        zx, zy = z.rect.center
                        dx = zx - barrel.rect.centerx
                        dy = zy - barrel.rect.centery
                        distance = math.sqrt(dx * dx + dy * dy)

                        if distance <= Barrel.EXPLOSION_RADIUS:
                            # Explosion instantly kills nearby zombies
                            self.zombies.remove(z)
                            self.kills += 1
                            self.score += 10
                    break
        for z in self.zombies:
            for b in self.player.bullets[:]:
                bx, by = int(b[0]), int(b[1])
                if z.rect.collidepoint(bx, by):
                    if z.hit():
                        dead.append(z)
                    if b in self.player.bullets:
                        self.player.bullets.remove(b)
        for z in dead:
            if z in self.zombies:
                self.zombies.remove(z)
                self.kills += 1
                self.score += 10

        # Remove barrels after their explosion animation finishes
        self.barrels = [
            barrel for barrel in self.barrels
            if barrel.update()
        ]
        

        if self.kills >= self.kills_to_next:
            self.kills = 0
            self.wave += 1
            self.kills_to_next = 8 + self.wave * 2

            for _ in range(self.wave + 3):
                # Mix normal, fast and tank zombies
                zombie_type = random.choices(
                    ["normal", "fast", "tank"],
                    weights=[60, 25, 15],
                    k=1
                )[0]

                self.zombies.append(
                    spawn_zombie(
                        WIDTH,
                        HEIGHT,
                        self.player.rect,
                        zombie_type=zombie_type
                    )
                )
                
    def draw(self):
        self.screen.fill(BG)
        for x in range(0, WIDTH, 60):
            pygame.draw.line(self.screen, (40,45,35), (x,0), (x,HEIGHT), 1)
        for y in range(0, HEIGHT, 60):
            pygame.draw.line(self.screen, (40,45,35), (0,y), (WIDTH,y), 1)
        
        # Draw barrels and their explosion effects
        for barrel in self.barrels:
            barrel.draw(self.screen)
        for z in self.zombies: z.draw(self.screen)
        self.player.draw(self.screen)
        hud_bg = pygame.Rect(0, 0, WIDTH, 60)
        pygame.draw.rect(self.screen, (15,20,15), hud_bg)

        ammo_text = (
            f"RELOADING: {max(0, (self.player.reload_end_time - pygame.time.get_ticks()) / 1000):.1f}s"
            if self.player.is_reloading
            else f"Ammo: {self.player.ammo}/{self.player.max_ammo}"
        )

        hud1 = self.font.render(
            f"Wave: {self.wave}  Score: {self.score}  "
            f"Kills: {self.kills}/{self.kills_to_next}  "
            f"HP: {self.player.health}/{self.player.max_health}  "
            f"{ammo_text}",
            True, (160, 220, 120)
        )
        hud2 = self.font.render(
            "WASD Move, Click Shoot, R Restart",
            True, (160,220,120)
        )

        self.screen.blit(hud1, (8, 2))
        self.screen.blit(hud2, (8, 31))
        
        if self.game_over:
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((0,0,0,160))
            self.screen.blit(ov, (0,0))
            m = self.big_font.render("DEVOURED!", True, (180,40,40))
            s = self.font.render(f"Wave {self.wave} | Score {self.score} | Press R", True, (200,200,200))
            self.screen.blit(m, (WIDTH//2-m.get_width()//2, HEIGHT//2-40))
            self.screen.blit(s, (WIDTH//2-s.get_width()//2, HEIGHT//2+20))
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()


if __name__ == "__main__":
    engine = GameEngine()
    engine.run()
