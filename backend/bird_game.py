import os
import pygame
import random
import time
from datetime import datetime

# Ensure paths are always correct
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

pygame.init()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Bird Watching")

# Load and scale bird image to 1/10th of screen width
def load_scaled_image(path, target_width):
    raw_img = pygame.image.load(path)
    aspect_ratio = raw_img.get_height() / raw_img.get_width()
    target_height = int(target_width * aspect_ratio)
    return pygame.transform.scale(raw_img, (target_width, target_height))

# Background
bg = pygame.image.load(os.path.join(BASE_DIR, "assets/backgrounds/woodlands.jpg"))

# Bird image scaled to 1/10th of screen width (~80px wide)
target_bird_width = screen_width // 10
duckling_img = load_scaled_image(os.path.join(BASE_DIR, "assets/birds/duckling.png"), target_bird_width)

FONT = pygame.font.SysFont("Arial", 24)

# Bird data
class Bird:
    def __init__(self, name, image, gold_per_minute, spawn_chance, cooldown=1):
        self.name = name
        self.image = image
        self.gold_per_minute = gold_per_minute
        self.spawn_chance = spawn_chance
        self.cooldown = cooldown  # seconds between spawn checks

duckling = Bird("Duckling", duckling_img, gold_per_minute=1, spawn_chance=0.05)
bird_types = [duckling]

# Game state
spawned_birds = []
collected_birds = []
gold = 0
last_spawn_check = time.time()
last_gold_tick = time.time()

running = True
clock = pygame.time.Clock()

while running:
    screen.blit(bg, (0, 0))

    now = time.time()

    # Gold accumulation (once per minute)
    if now - last_gold_tick >= 60:
        gold += sum(b.gold_per_minute for b in collected_birds)
        last_gold_tick = now

    # Bird spawn check (every 1 second)
    if now - last_spawn_check >= 1:
        for bird in bird_types:
            if random.random() < bird.spawn_chance:
                bird_width, bird_height = bird.image.get_size()
                max_x = max(0, screen_width - bird_width)
                max_y = max(0, screen_height - bird_height)
                x = random.randint(0, max_x)
                y = random.randint(0, max_y)
                spawned_birds.append({"bird": bird, "pos": (x, y)})
        last_spawn_check = now

    # Draw birds
    for obj in spawned_birds:
        screen.blit(obj["bird"].image, obj["pos"])

    # Draw gold
    gold_text = FONT.render(f"Gold: {gold}", True, (255, 255, 0))
    screen.blit(gold_text, (10, 10))

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            for obj in spawned_birds[:]:
                bx, by = obj["pos"]
                bird_img = obj["bird"].image
                rect = bird_img.get_rect(topleft=(bx, by))
                if rect.collidepoint(mx, my):
                    collected_birds.append(obj["bird"])
                    print(f"Collected: {obj['bird'].name} @ {datetime.now()}")
                    spawned_birds.remove(obj)

    clock.tick(30)

pygame.quit()
