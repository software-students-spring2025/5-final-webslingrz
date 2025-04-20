import os
import pygame
import random
import time
import numpy as np
from datetime import datetime
import asyncio

# Constants for game screen
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

# Paths need to be relative for web deployment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_scaled_image(path, target_width):
    raw_img = pygame.image.load(path)
    aspect_ratio = raw_img.get_height() / raw_img.get_width()
    target_height = int(target_width * aspect_ratio)
    return pygame.transform.scale(raw_img, (target_width, target_height))

def greyscale_surface(surface):
    arr = pygame.surfarray.array3d(surface).astype(float)
    grey = np.dot(arr[..., :3], [0.3, 0.59, 0.11])
    grey_3ch = np.stack((grey,)*3, axis=-1).astype('uint8')
    grey_surface = pygame.surfarray.make_surface(grey_3ch)
    return pygame.transform.rotate(grey_surface, -0)

class Bird:
    def __init__(self, name, image, gold_per_minute, spawn_chance, rarity):
        self.name = name
        self.image = image
        self.spawn_chance = spawn_chance
        self.gold_per_minute = gold_per_minute
        self.rarity = rarity

async def show_birdiary(screen, collected_set, bird_types):
    birdiary_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    font = pygame.font.SysFont("Arial", 22)
    big_font = pygame.font.SysFont("Arial", 28, bold=True)

    scroll_offset = 0
    scroll_speed = 30
    item_height = 60
    padding_top = 80

    back_button = pygame.Rect(SCREEN_WIDTH - 120, 20, 100, 30)
    max_scroll = max(0, len(bird_types) * item_height + padding_top - SCREEN_HEIGHT + 30)

    running = True
    while running:
        birdiary_surface.fill((245, 245, 220))
        y = 20 - scroll_offset

        title = big_font.render("Birdiary", True, (50, 50, 50))
        birdiary_surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, y))
        y += 60

        for bird in bird_types:
            img = bird.image if bird.name in collected_set else greyscale_surface(bird.image)
            img = pygame.transform.scale(img, (50, 50))
            birdiary_surface.blit(img, (40, y))
            desc = f"{bird.name}  |  {bird.rarity.title()}  |  {bird.gold_per_minute / 60:.2f} gold/sec"
            rendered = font.render(desc, True, (30, 30, 30))
            birdiary_surface.blit(rendered, (100, y + 10))
            y += item_height

        pygame.draw.rect(birdiary_surface, (180, 80, 80), back_button, border_radius=6)
        back_text = font.render("Back", True, (255, 255, 255))
        birdiary_surface.blit(back_text, (back_button.x + 20, back_button.y + 4))

        screen.blit(birdiary_surface, (0, 0))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN and back_button.collidepoint(event.pos):
                running = False
            elif event.type == pygame.MOUSEWHEEL:
                scroll_offset -= event.y * scroll_speed
                scroll_offset = max(0, min(scroll_offset, max_scroll))
                
        await asyncio.sleep(0)
    
    return True

# The main game function needs to be async
async def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Bird Watching")
    
    target_bird_width = SCREEN_WIDTH // 10
    
    bg = load_scaled_image(os.path.join(BASE_DIR, "assets/backgrounds/forest.png"), SCREEN_WIDTH)
    
    bird_images = {
        "Duckling": "duckling.png",
        "Alien": "alien.png",
        "Cherry": "cherry.png",
        "Confused": "confused.png",
        "Crow": "crow.png",
        "Cyan": "cyan.png",
        "Dandy": "dandy.png",
        "Eyelash": "eyelash.png",
        "Gnome": "gnome.png",
        "Green": "green.png",
        "Hamilton": "hamilton.png",
        "King Rook": "king_rook.png",
        "Kiwi": "kiwi.png",
        "Little Guy": "little_guy.png",
        "Mafia": "mafia.png",
        "Onigiri": "onigiri.png",
        "Owl": "owl.png",
        "Blue Parakeet": "parakeet_blue.png",
        "Yellow Parakeet": "parakeet_yellow.png",
        "Pirate": "pirate.png",
        "Pitiful": "pitiful.png",
        "Pleh": "pleh.png",
        "Purple": "purple.png",
        "Robin Hood": "robin_hood.png",
        "Sans Undertale": "sans_undertale.png",
        "Seed Dealer": "seed_dealer.png",
        "Snowy Owl": "snowy_owl.png",
        "Sonic": "sonic.png",
        "Space": "space.png",
        "Spiderman": "spiderman.png",
        "Stork": "stork.png",
        "Tomato": "tomato.png",
        "Toucan": "toucan.png",
        "Webslinger": "webslinger.png",
        "Zelda": "zelda.png",
        "Money Mogul": "money_mogul.png",
    }
    
    bird_assets = {
        name: load_scaled_image(os.path.join(BASE_DIR, f"assets/birds/{file}"), target_bird_width)
        for name, file in bird_images.items()
    }
    
    rarity_tiers = {
        "common":     {"spawn_chance": 0.10,    "gold_per_sec": 0.01},
        "uncommon":   {"spawn_chance": 0.033,   "gold_per_sec": 0.05},
        "rare":       {"spawn_chance": 0.0083,  "gold_per_sec": 0.10},
        "epic":       {"spawn_chance": 0.0017,  "gold_per_sec": 0.20},
        "legendary":  {"spawn_chance": 0.00055, "gold_per_sec": 1.00},
    }
    
    rarity_assignments = {
        "common":     ["Duckling"],
        "uncommon":   ["Alien", "Cherry", "Confused", "Crow", "Cyan", "Green", "Gnome"],
        "rare":       ["Dandy", "Eyelash", "Little Guy", "Hamilton", "Blue Parakeet", "Yellow Parakeet",
                       "Onigiri", "Mafia", "Kiwi", "King Rook", "Pirate", "Pitiful", "Pleh", "Purple"],
        "epic":       ["Robin Hood", "Sans Undertale", "Seed Dealer", "Snowy Owl", "Sonic", "Space",
                       "Spiderman", "Stork", "Tomato", "Toucan", "Webslinger", "Zelda"],
        "legendary":  ["Money Mogul"]
    }
    
    bird_types = []
    for rarity, names in rarity_assignments.items():
        for name in names:
            bird_types.append(Bird(
                name,
                bird_assets[name],
                rarity_tiers[rarity]["gold_per_sec"] * 60,
                rarity_tiers[rarity]["spawn_chance"],
                rarity
            ))
    
    # Game state
    spawned_birds = []
    collected_birds = []
    gold = 0
    last_spawn_check = time.time()
    
    FONT = pygame.font.SysFont("Arial", 24)
    BUTTON_FONT = pygame.font.SysFont("Arial", 20)
    birdiary_button = pygame.Rect(SCREEN_WIDTH - 180, 10, 160, 35)
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        screen.blit(bg, (0, 0))
        now = time.time()
        delta_time = clock.get_time() / 1000
        
        gold += sum(b.gold_per_minute / 60 for b in collected_birds) * delta_time
        
        if now - last_spawn_check >= 1:
            for bird in bird_types:
                if random.random() < bird.spawn_chance:
                    bw, bh = bird.image.get_size()
                    x = random.randint(0, SCREEN_WIDTH - bw)
                    y = random.randint(0, SCREEN_HEIGHT - bh)
                    spawned_birds.append({"bird": bird, "pos": (x, y)})
            last_spawn_check = now
        
        for obj in spawned_birds:
            screen.blit(obj["bird"].image, obj["pos"])
        
        gold_text = FONT.render(f"Gold: {int(gold)}", True, (255, 255, 0))
        screen.blit(gold_text, (10, 10))
        
        pygame.draw.rect(screen, (70, 130, 180), birdiary_button, border_radius=8)
        button_text = BUTTON_FONT.render("Open Birdiary", True, (255, 255, 255))
        screen.blit(button_text, (birdiary_button.x + 10, birdiary_button.y + 6))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if birdiary_button.collidepoint(event.pos):
                    # Call the async birdiary function with await
                    game_status = await show_birdiary(screen, set(b.name for b in collected_birds), bird_types)
                    running = game_status
                else:
                    mx, my = event.pos
                    for obj in spawned_birds[:]:
                        rect = obj["bird"].image.get_rect(topleft=obj["pos"])
                        if rect.collidepoint(mx, my):
                            collected_birds.append(obj["bird"])
                            print(f"Collected: {obj['bird'].name} @ {datetime.now()}")
                            spawned_birds.remove(obj)
                            break
        
        clock.tick(30)
        
        await asyncio.sleep(0)
    
    pygame.quit()

# This is how you should run the game for regular Pygame
if __name__ == "__main__":
    asyncio.run(main())