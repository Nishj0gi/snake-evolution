import pygame
import random
import json
import os
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 180, 0)
RED = (255, 0, 0)
BLUE = (0, 150, 255)
YELLOW = (255, 255, 0)
PURPLE = (200, 0, 255)
ORANGE = (255, 165, 0)
GRAY = (100, 100, 100)

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class PowerUpType(Enum):
    SPEED_BOOST = "Speed Boost"
    SHIELD = "Shield"
    MULTIPLIER = "Score x2"
    GHOST = "Ghost Mode"

@dataclass
class PowerUp:
    type: PowerUpType
    pos: Tuple[int, int]
    duration: int = 300  # frames
    color: Tuple[int, int, int] = WHITE
    
    def __post_init__(self):
        colors = {
            PowerUpType.SPEED_BOOST: BLUE,
            PowerUpType.SHIELD: YELLOW,
            PowerUpType.MULTIPLIER: PURPLE,
            PowerUpType.GHOST: ORANGE
        }
        self.color = colors[self.type]

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.life = 30
        self.color = color
        self.size = random.randint(2, 5)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size = max(1, self.size - 0.1)
    
    def draw(self, screen):
        if self.life > 0:
            alpha = int(255 * (self.life / 30))
            color = (*self.color, alpha)
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, color, (self.size, self.size), self.size)
            screen.blit(s, (int(self.x), int(self.y)))

class Obstacle:
    def __init__(self, pos):
        self.pos = pos

class Snake:
    def __init__(self):
        self.reset()
    
    def reset(self):
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        self.body = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
        self.direction = Direction.RIGHT
        self.grow_pending = 0
        self.active_powerups = {}
        
    def get_head(self):
        return self.body[0]
    
    def move(self, has_ghost=False):
        head_x, head_y = self.get_head()
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)
        
        # Wall collision with ghost mode
        if not has_ghost:
            if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or 
                new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
                return False
        else:
            # Wrap around in ghost mode
            new_head = (new_head[0] % GRID_WIDTH, new_head[1] % GRID_HEIGHT)
        
        # Self collision
        if new_head in self.body[1:]:
            return False
        
        self.body.insert(0, new_head)
        
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()
        
        return True
    
    def grow(self, amount=1):
        self.grow_pending += amount
    
    def set_direction(self, direction):
        # Prevent 180-degree turns
        dx, dy = direction.value
        head_x, head_y = self.get_head()
        if len(self.body) > 1:
            neck_x, neck_y = self.body[1]
            if (head_x + dx, head_y + dy) != (neck_x, neck_y):
                self.direction = direction
        else:
            self.direction = direction

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Evolution")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.mode = "MENU"  # MENU, CLASSIC, TIME_ATTACK, SURVIVAL, GAME_OVER
        self.reset_game()
        self.high_scores = self.load_high_scores()
        
    def reset_game(self):
        self.snake = Snake()
        self.score = 0
        self.move_counter = 0
        self.base_speed = 8  # moves per second
        self.speed_multiplier = 1.0
        self.powerups = []
        self.particles = []
        self.obstacles = []
        self.time_remaining = 60 * FPS  # 60 seconds for time attack
        self.powerup_spawn_counter = 0
        self.food_pos = self.spawn_food()
        
    def spawn_food(self):
        while True:
            pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos not in self.snake.body and pos not in [o.pos for o in self.obstacles]:
                return pos
    
    def spawn_powerup(self):
        if len(self.powerups) < 2:  # Max 2 powerups on screen
            while True:
                pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
                if (pos not in self.snake.body and pos != self.food_pos and 
                    pos not in [p.pos for p in self.powerups] and
                    pos not in [o.pos for o in self.obstacles]):
                    powerup_type = random.choice(list(PowerUpType))
                    self.powerups.append(PowerUp(powerup_type, pos))
                    break
    
    def spawn_obstacle(self):
        while True:
            pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if (pos not in self.snake.body and pos != self.food_pos and
                pos not in [p.pos for p in self.powerups] and
                pos not in [o.pos for o in self.obstacles]):
                self.obstacles.append(Obstacle(pos))
                break
    
    def create_particles(self, x, y, color, count=10):
        for _ in range(count):
            self.particles.append(Particle(x * GRID_SIZE + GRID_SIZE // 2, 
                                          y * GRID_SIZE + GRID_SIZE // 2, color))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if self.mode == "MENU":
                    if event.key == pygame.K_1:
                        self.mode = "CLASSIC"
                        self.reset_game()
                    elif event.key == pygame.K_2:
                        self.mode = "TIME_ATTACK"
                        self.reset_game()
                    elif event.key == pygame.K_3:
                        self.mode = "SURVIVAL"
                        self.reset_game()
                    elif event.key == pygame.K_q:
                        return False
                
                elif self.mode == "GAME_OVER":
                    if event.key == pygame.K_SPACE:
                        self.mode = "MENU"
                    elif event.key == pygame.K_r:
                        self.reset_game()
                        self.mode = self.last_mode
                
                else:  # In game
                    if event.key == pygame.K_ESCAPE:
                        self.mode = "MENU"
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.snake.set_direction(Direction.UP)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.snake.set_direction(Direction.DOWN)
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.snake.set_direction(Direction.LEFT)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.snake.set_direction(Direction.RIGHT)
        
        return True
    
    def update(self):
        if self.mode not in ["CLASSIC", "TIME_ATTACK", "SURVIVAL"]:
            return
        
        # Update particles
        self.particles = [p for p in self.particles if p.life > 0]
        for particle in self.particles:
            particle.update()
        
        # Update powerup timers
        expired = []
        for powerup_type, remaining in self.snake.active_powerups.items():
            remaining -= 1
            if remaining <= 0:
                expired.append(powerup_type)
            else:
                self.snake.active_powerups[powerup_type] = remaining
        
        for powerup_type in expired:
            del self.snake.active_powerups[powerup_type]
        
        # Calculate current speed
        current_speed = self.base_speed * self.speed_multiplier
        if PowerUpType.SPEED_BOOST in self.snake.active_powerups:
            current_speed *= 1.5
        
        # Progressive difficulty in classic mode
        if self.mode == "CLASSIC":
            current_speed += len(self.snake.body) * 0.05
        
        # Move snake at appropriate speed
        frames_per_move = max(1, int(FPS / current_speed))
        self.move_counter += 1
        
        if self.move_counter >= frames_per_move:
            self.move_counter = 0
            
            # Move snake
            has_ghost = PowerUpType.GHOST in self.snake.active_powerups
            if not self.snake.move(has_ghost):
                if PowerUpType.SHIELD in self.snake.active_powerups:
                    # Shield saves you once
                    del self.snake.active_powerups[PowerUpType.SHIELD]
                    self.create_particles(*self.snake.get_head(), YELLOW, 20)
                else:
                    self.game_over()
                    return
            
            # Check obstacle collision in survival mode
            if self.mode == "SURVIVAL" and not has_ghost:
                if self.snake.get_head() in [o.pos for o in self.obstacles]:
                    if PowerUpType.SHIELD in self.snake.active_powerups:
                        del self.snake.active_powerups[PowerUpType.SHIELD]
                        self.obstacles = [o for o in self.obstacles if o.pos != self.snake.get_head()]
                        self.create_particles(*self.snake.get_head(), YELLOW, 20)
                    else:
                        self.game_over()
                        return
            
            # Check food collision
            if self.snake.get_head() == self.food_pos:
                self.snake.grow(1)
                multiplier = 2 if PowerUpType.MULTIPLIER in self.snake.active_powerups else 1
                self.score += 10 * multiplier
                self.create_particles(*self.food_pos, RED, 15)
                self.food_pos = self.spawn_food()
            
            # Check powerup collision
            for powerup in self.powerups[:]:
                if self.snake.get_head() == powerup.pos:
                    self.snake.active_powerups[powerup.type] = powerup.duration
                    self.create_particles(*powerup.pos, powerup.color, 15)
                    self.powerups.remove(powerup)
        
        # Spawn powerups periodically
        self.powerup_spawn_counter += 1
        if self.powerup_spawn_counter >= FPS * 10:  # Every 10 seconds
            self.powerup_spawn_counter = 0
            self.spawn_powerup()
        
        # Survival mode: spawn obstacles
        if self.mode == "SURVIVAL" and len(self.snake.body) % 5 == 0 and len(self.snake.body) > 3:
            if len(self.obstacles) < len(self.snake.body) // 5:
                self.spawn_obstacle()
        
        # Time attack mode
        if self.mode == "TIME_ATTACK":
            self.time_remaining -= 1
            if self.time_remaining <= 0:
                self.game_over()
    
    def game_over(self):
        self.last_mode = self.mode
        self.mode = "GAME_OVER"
        
        # Update high score
        mode_key = self.last_mode.lower()
        if self.score > self.high_scores.get(mode_key, 0):
            self.high_scores[mode_key] = self.score
            self.save_high_scores()
    
    def draw(self):
        self.screen.fill(BLACK)
        
        if self.mode == "MENU":
            self.draw_menu()
        elif self.mode == "GAME_OVER":
            self.draw_game_over()
        else:
            self.draw_game()
        
        pygame.display.flip()
    
    def draw_menu(self):
        title = self.font.render("SNAKE EVOLUTION", True, GREEN)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        
        options = [
            "1 - CLASSIC MODE",
            "2 - TIME ATTACK (60s)",
            "3 - SURVIVAL MODE (Obstacles)",
            "",
            "Q - QUIT"
        ]
        
        y = 200
        for option in options:
            text = self.small_font.render(option, True, WHITE)
            self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y))
            y += 40
        
        # High scores
        y = 450
        hs_title = self.small_font.render("HIGH SCORES", True, YELLOW)
        self.screen.blit(hs_title, (WIDTH // 2 - hs_title.get_width() // 2, y))
        y += 30
        
        for mode in ["classic", "time_attack", "survival"]:
            score = self.high_scores.get(mode, 0)
            text = self.small_font.render(f"{mode.replace('_', ' ').title()}: {score}", True, WHITE)
            self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y))
            y += 25
    
    def draw_game_over(self):
        game_over_text = self.font.render("GAME OVER", True, RED)
        self.screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, 200))
        
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 260))
        
        mode_key = self.last_mode.lower()
        if self.score == self.high_scores.get(mode_key, 0) and self.score > 0:
            hs_text = self.small_font.render("NEW HIGH SCORE!", True, YELLOW)
            self.screen.blit(hs_text, (WIDTH // 2 - hs_text.get_width() // 2, 310))
        
        options = [
            "R - RESTART",
            "SPACE - MENU"
        ]
        
        y = 380
        for option in options:
            text = self.small_font.render(option, True, WHITE)
            self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, y))
            y += 35
    
    def draw_game(self):
        # Draw grid
        for x in range(0, WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (WIDTH, y))
        
        # Draw obstacles
        for obstacle in self.obstacles:
            rect = pygame.Rect(obstacle.pos[0] * GRID_SIZE, obstacle.pos[1] * GRID_SIZE, 
                             GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(self.screen, GRAY, rect)
        
        # Draw food
        food_rect = pygame.Rect(self.food_pos[0] * GRID_SIZE, self.food_pos[1] * GRID_SIZE,
                               GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(self.screen, RED, food_rect)
        
        # Draw powerups
        for powerup in self.powerups:
            powerup_rect = pygame.Rect(powerup.pos[0] * GRID_SIZE, powerup.pos[1] * GRID_SIZE,
                                      GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(self.screen, powerup.color, powerup_rect)
            pygame.draw.rect(self.screen, WHITE, powerup_rect, 2)
        
        # Draw snake
        for i, segment in enumerate(self.snake.body):
            color = GREEN if i == 0 else DARK_GREEN
            
            # Ghost mode effect
            if PowerUpType.GHOST in self.snake.active_powerups:
                s = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(s, (*color, 150), (0, 0, GRID_SIZE, GRID_SIZE))
                self.screen.blit(s, (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE))
            else:
                segment_rect = pygame.Rect(segment[0] * GRID_SIZE, segment[1] * GRID_SIZE,
                                         GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(self.screen, color, segment_rect)
            
            # Shield effect on head
            if i == 0 and PowerUpType.SHIELD in self.snake.active_powerups:
                pygame.draw.circle(self.screen, YELLOW, 
                                 (segment[0] * GRID_SIZE + GRID_SIZE // 2,
                                  segment[1] * GRID_SIZE + GRID_SIZE // 2),
                                 GRID_SIZE // 2 + 3, 2)
        
        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)
        
        # Draw UI
        score_text = self.small_font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        mode_text = self.small_font.render(f"Mode: {self.mode}", True, WHITE)
        self.screen.blit(mode_text, (10, 40))
        
        if self.mode == "TIME_ATTACK":
            time_left = max(0, self.time_remaining // FPS)
            time_text = self.small_font.render(f"Time: {time_left}s", True, WHITE)
            self.screen.blit(time_text, (10, 70))
        
        # Draw active powerups
        y = HEIGHT - 30
        for powerup_type, remaining in self.snake.active_powerups.items():
            time_left = remaining // FPS
            text = self.small_font.render(f"{powerup_type.value}: {time_left}s", True, WHITE)
            self.screen.blit(text, (WIDTH - text.get_width() - 10, y))
            y -= 25
    
    def load_high_scores(self):
        try:
            if os.path.exists("high_scores.json"):
                with open("high_scores.json", "r") as f:
                    return json.load(f)
        except:
            pass
        return {"classic": 0, "time_attack": 0, "survival": 0}
    
    def save_high_scores(self):
        try:
            with open("high_scores.json", "w") as f:
                json.dump(self.high_scores, f, indent=2)
        except:
            pass
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()