import os
import pygame
import random
import time
import numpy as np
from datetime import datetime
import asyncio
import traceback
from pygame import mixer 

# Constants for game screen
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

# Paths need to be relative for web deployment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Error handling and display
error_messages = []
MAX_ERROR_MESSAGES = 3

def add_error_message(error_text):
    """Add an error message to be displayed on screen"""
    error_messages.append(error_text)
    if len(error_messages) > MAX_ERROR_MESSAGES:
        error_messages.pop(0)  # Remove oldest message if limit reached
    print(f"ERROR: {error_text}")

def remove_error_message():
    error_messages.clear()

def draw_error_messages(screen, font):
    """Draw error messages on the screen"""
    if not error_messages:
        return
    
    error_surface = pygame.Surface((SCREEN_WIDTH, len(error_messages) * 30 + 20))
    error_surface.set_alpha(200)
    error_surface.fill((50, 0, 0))
    screen.blit(error_surface, (0, 0))
    
    for i, msg in enumerate(error_messages):
        text = font.render(msg, True, (255, 200, 200))
        screen.blit(text, (10, 10 + i * 30))

def load_scaled_image(path, target_width):
    try:
        raw_img = pygame.image.load(path)
        aspect_ratio = raw_img.get_height() / raw_img.get_width()
        target_height = int(target_width * aspect_ratio)
        return pygame.transform.scale(raw_img, (target_width, target_height))
    except Exception as e:
        add_error_message(f"Failed to load image {path}")
        # Return a colored placeholder instead
        surface = pygame.Surface((target_width, target_width))
        surface.fill((255, 0, 255))  # Magenta for missing textures
        return surface

def greyscale_surface(surface):
    try:
        arr = pygame.surfarray.array3d(surface).astype(float)
        grey = np.dot(arr[..., :3], [0.3, 0.59, 0.11])
        grey_3ch = np.stack((grey,)*3, axis=-1).astype('uint8')
        grey_surface = pygame.surfarray.make_surface(grey_3ch)
        return pygame.transform.rotate(grey_surface, -0)
    except Exception as e:
        return surface  # Return original surface if conversion fails

class Bird:
    def __init__(self, name, image, gold_per_minute, spawn_chance, rarity):
        self.name = name
        self.image = image
        self.spawn_chance = spawn_chance
        self.gold_per_minute = gold_per_minute
        self.rarity = rarity

async def show_birdiary(screen, collected_set, bird_types):
    try:
        birdiary_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        font = pygame.font.SysFont("Arial", 22)
        big_font = pygame.font.SysFont("Arial", 28, bold=True)
        error_font = pygame.font.SysFont("Arial", 18)

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
            birdiary_surface.blit(back_text, (back_button.x + 24, back_button.y + 2))

            screen.blit(birdiary_surface, (0, 0))
            
            draw_error_messages(screen, error_font)
            
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.MOUSEBUTTONDOWN and back_button.collidepoint(event.pos):
                    remove_error_message()
                    running = False
                elif event.type == pygame.MOUSEWHEEL:
                    scroll_offset -= event.y * scroll_speed
                    scroll_offset = max(0, min(scroll_offset, max_scroll))
                    
            await asyncio.sleep(0)
        
        return True
    except Exception as e:
        add_error_message(f"Birdiary error: {str(e)}")
        return True  # Continue game despite error

# Deco Store function
async def show_store(screen, purchased_set, gold, deco_assets, deco_prices, deco_spawn_points, deco_click_sound):
    try:
        store_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        font = pygame.font.SysFont("Arial", 22)
        big_font = pygame.font.SysFont("Arial", 28, bold=True)
        error_font = pygame.font.SysFont("Arial", 18)

        scroll_offset = 0
        scroll_speed = 30
        item_height = 60
        padding_top = 80

        back_button = pygame.Rect(SCREEN_WIDTH - 120, 20, 100, 30)
        max_scroll = max(0, len(deco_assets) * item_height + padding_top - SCREEN_HEIGHT + 30)

        running = True
        while running:
            store_surface.fill((245, 245, 220))
            y = 20 - scroll_offset

            title = big_font.render("Deco Store", True, (50, 50, 50))
            store_surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, y))
            y += 60

            clickable_items = []

            for name, image in deco_assets.items():
                img = image if name in purchased_set else greyscale_surface(image)
                img = pygame.transform.scale(img, (50, 50))
                store_surface.blit(img, (40, y))
                
                status = "Purchased" if name in purchased_set else f"{deco_prices[name]} gold"
                desc = f"{name}  |  {status}"
                rendered = font.render(desc, True, (30, 30, 30))
                store_surface.blit(rendered, (100, y + 10))

                clickable_items.append((pygame.Rect(40, y, SCREEN_WIDTH - 80, item_height), name))
                y += item_height

            pygame.draw.rect(store_surface, (180, 80, 80), back_button, border_radius=6)
            back_text = font.render("Back", True, (255, 255, 255))
            store_surface.blit(back_text, (back_button.x + 24, back_button.y + 2))

            gold_text = font.render(f"Gold: {int(gold)}", True, (80, 60, 20))
            store_surface.blit(gold_text, (20, 20))

            screen.blit(store_surface, (0, 0))
            
            draw_error_messages(screen, error_font)
            
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False, gold
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button.collidepoint(event.pos):
                        remove_error_message()
                        running = False
                    else:
                        for rect, name in clickable_items:
                            if rect.collidepoint(event.pos) and name not in purchased_set:
                                price = deco_prices[name]
                                #deco_click_sound.play()
                                if gold >= price:
                                    gold -= price
                                    purchased_set.add(name)
                                else:
                                    add_error_message("Not enough gold!")
                elif event.type == pygame.MOUSEWHEEL:
                    scroll_offset -= event.y * scroll_speed
                    scroll_offset = max(0, min(scroll_offset, max_scroll))
                    
            await asyncio.sleep(0)

        return True, gold
    except Exception as e:
        add_error_message(f"Store error: {str(e)}")
        return True, gold  # Continue game despite error

# The main game function
async def main():
    try:
        pygame.init()
        # mixer.init() 

        # common_click_sound = mixer.Sound("assets/marimba-bloop-3-188151.mp3") 
        # uncommon_click_sound = mixer.Sound("assets/marimba-bloop-1-188150.mp3") 
        # rare_click_sound = mixer.Sound("assets/marimba-bloop-2-188149.mp3") 
        # epic_click_sound = mixer.Sound("assets/marimba-ringtone-2-185153.mp3") 
        # legendary_click_sound = mixer.Sound("assets/marimba-win-h-3-209697.mp3") 
        # button_click_sound = mixer.Sound("assets/107136__bubaproducer__button-18.wav")
        # deco_click_sound = mixer.Sound("assets/infographic-pop-4-197870.mp3")
        
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Bird Watching")
        
        target_bird_width = SCREEN_WIDTH // 10
        target_deco_width = SCREEN_WIDTH // 8
        
        error_font = pygame.font.SysFont("Arial", 18)
        
        bg_path = os.path.join(BASE_DIR, "assets/backgrounds/forest.png")
        bg = load_scaled_image(bg_path, SCREEN_WIDTH)
        bg = pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
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
        
        deco_images = {
            "Bath": "bath.png",
            "Clock": "clock.png",
            "Froggy Fountain": "froggy_fountain.png",
            "Lamp": "lamp.png",
            "Sofa": "sofa.png"
        }
        
        bird_assets = {}
        for name, file in bird_images.items():
            bird_path = os.path.join(BASE_DIR, f"assets/birds/{file}")
            bird_assets[name] = load_scaled_image(bird_path, target_bird_width)
        
        deco_assets = {}
        for name, file in deco_images.items():
            deco_path = os.path.join(BASE_DIR, f"assets/decoration/{file}")
            deco_assets[name] = load_scaled_image(deco_path, target_deco_width)
        
        # deco_prices = {
        #     "Bath": 1000,
        #     "Clock": 200,
        #     "Froggy Fountain": 10000,
        #     "Lamp": 100,
        #     "Sofa": 500
        # }

        deco_prices = {
            "Bath": 0,
            "Clock": 0,
            "Froggy Fountain": 0,
            "Lamp": 0,
            "Sofa": 0
        }
        
        rarity_tiers = {
            "common": {"spawn_chance": 0.10, "gold_per_sec": 0.01},
            "uncommon": {"spawn_chance": 0.033, "gold_per_sec": 0.05},
            "rare": {"spawn_chance": 0.0083, "gold_per_sec": 0.10},
            "epic": {"spawn_chance": 0.0017, "gold_per_sec": 0.20},
            "legendary": {"spawn_chance": 0.00055, "gold_per_sec": 1.00},
        }
        
        rarity_assignments = {
            "common": ["Duckling"],
            "uncommon": ["Alien", "Cherry", "Confused", "Crow", "Cyan", "Green", "Gnome"],
            "rare": ["Dandy", "Eyelash", "Little Guy", "Hamilton", "Blue Parakeet", "Yellow Parakeet",
                    "Onigiri", "Mafia", "Kiwi", "King Rook", "Pirate", "Pitiful", "Pleh", "Purple"],
            "epic": ["Robin Hood", "Sans Undertale", "Seed Dealer", "Snowy Owl", "Sonic", "Space",
                    "Spiderman", "Stork", "Tomato", "Toucan", "Webslinger", "Zelda"],
            "legendary": ["Money Mogul"]
        }
        
        bird_types = []
        for rarity, names in rarity_assignments.items():
            for name in names:
                if name in bird_assets:
                    bird_types.append(Bird(
                        name,
                        bird_assets[name],
                        rarity_tiers[rarity]["gold_per_sec"] * 60,
                        rarity_tiers[rarity]["spawn_chance"],
                        rarity
                    ))
        
        SPAWN_POINTS = [
            (50, 135),  # top left
            (140, 350),  # long left
            (270, 365),  # long right
            (240, 210),  # swing
            (220, 485),  # bottom left
            (600, 125),  # top right
            (630, 385)  # bottom right
        ]
        
        DECO_SPAWN_POINTS = {
            "Lamp": (50, 320),
            "Bath": (320, 360), 
            "Clock": (100, 465),
            "Froggy Fountain": (700, 390),  
            "Sofa": (700, 135)  
        }
        
        spawned_birds = []
        collected_birds = []
        purchased_deco = set()
        gold = 0
        last_spawn_check = time.time()
        occupied_spawn = set()
        lamp = False
        bath = False
        clock = False
        fountain = False
        sofa = False
        
        FONT = pygame.font.SysFont("Arial", 24)
        BUTTON_FONT = pygame.font.SysFont("Arial", 20)
        birdiary_button = pygame.Rect(SCREEN_WIDTH - 180, 10, 160, 35)
        store_button = pygame.Rect(SCREEN_WIDTH - 180, 60, 160, 35)
        
        clock = pygame.time.Clock()
        running = True
        
        while running:
            try:
                screen.blit(bg, (0, 0))
                now = time.time()
                delta_time = clock.get_time() / 1000
                
                gold += sum(b.gold_per_minute for b in collected_birds) * delta_time 
                
                if now - last_spawn_check >= 1:
                    unoccupied_spawn = [spawn for spawn in SPAWN_POINTS if spawn not in occupied_spawn]
                    random.shuffle(unoccupied_spawn)
                    
                    for bird in bird_types:
                        if random.random() < bird.spawn_chance and unoccupied_spawn:
                            spawn_position = unoccupied_spawn.pop()
                            occupied_spawn.add(spawn_position)
                            spawned_birds.append({"bird": bird, "pos": spawn_position})
                    last_spawn_check = now
                
                for obj in spawned_birds:
                    screen.blit(obj["bird"].image, obj["pos"])
                
                for deco in purchased_deco:
                    if deco in deco_assets and deco in DECO_SPAWN_POINTS:
                        if not lamp and deco == "Lamp":
                            rarity_tiers["common"]["spawn_chance"] = 0.05
                            print("altered rarity")
                            bird_types = []
                            for rarity, names in rarity_assignments.items():
                                for name in names:
                                    if name in bird_assets:
                                        bird_types.append(Bird(
                                            name,
                                            bird_assets[name],
                                            rarity_tiers[rarity]["gold_per_sec"] * 60,
                                            rarity_tiers[rarity]["spawn_chance"],
                                            rarity
                                        ))
                            lamp = True
                        elif not bath and deco == "Bath":
                            rarity_tiers["epic"]["spawn_chance"] = 0.005
                            print("altered rarity")
                            bird_types = []
                            for rarity, names in rarity_assignments.items():
                                for name in names:
                                    if name in bird_assets:
                                        bird_types.append(Bird(
                                            name,
                                            bird_assets[name],
                                            rarity_tiers[rarity]["gold_per_sec"] * 60,
                                            rarity_tiers[rarity]["spawn_chance"],
                                            rarity
                                        ))
                            bath = True
                        elif not clock and deco == "Clock":
                            rarity_tiers["uncommon"]["spawn_chance"] = 0.04
                            print("altered rarity")
                            bird_types = []
                            for rarity, names in rarity_assignments.items():
                                for name in names:
                                    if name in bird_assets:
                                        bird_types.append(Bird(
                                            name,
                                            bird_assets[name],
                                            rarity_tiers[rarity]["gold_per_sec"] * 60,
                                            rarity_tiers[rarity]["spawn_chance"],
                                            rarity
                                        ))
                            clock = True
                        elif not fountain and deco == "Froggy Fountain":
                            rarity_tiers["legendary"]["spawn_chance"] =  0.05
                            print("altered rarity")
                            print(rarity_tiers["legendary"]["spawn_chance"])
                            bird_types = []
                            for rarity, names in rarity_assignments.items():
                                for name in names:
                                    if name in bird_assets:
                                        bird_types.append(Bird(
                                            name,
                                            bird_assets[name],
                                            rarity_tiers[rarity]["gold_per_sec"] * 60,
                                            rarity_tiers[rarity]["spawn_chance"],
                                            rarity
                                        ))
                            fountain = True
                        elif not sofa and deco == "Sofa":
                            rarity_tiers["rare"]["spawn_chance"] = 0.033
                            print("altered rarity")
                            bird_types = []
                            for rarity, names in rarity_assignments.items():
                                for name in names:
                                    if name in bird_assets:
                                        bird_types.append(Bird(
                                            name,
                                            bird_assets[name],
                                            rarity_tiers[rarity]["gold_per_sec"] * 60,
                                            rarity_tiers[rarity]["spawn_chance"],
                                            rarity
                                        ))
                            sofa = True

                        # rarity_tiers = {
                        #    "common": {"spawn_chance": 0.10, "gold_per_sec": 0.01},
                        #    "uncommon": {"spawn_chance": 0.033, "gold_per_sec": 0.05},
                        #    "rare": {"spawn_chance": 0.0083, "gold_per_sec": 0.10},
                        #    "epic": {"spawn_chance": 0.0017, "gold_per_sec": 0.20},
                        #    "legendary": {"spawn_chance": 0.00055, "gold_per_sec": 1.00},
                        # }
                        screen.blit(deco_assets[deco], DECO_SPAWN_POINTS[deco])
                
                gold_text = FONT.render(f"Gold: {int(gold)}", True, (255, 255, 0))
                screen.blit(gold_text, (10, 10))
                
                pygame.draw.rect(screen, (70, 130, 180), birdiary_button, border_radius=8)
                pygame.draw.rect(screen, (70, 130, 180), store_button, border_radius=8)
                
                button_text = BUTTON_FONT.render("Open Birdiary", True, (255, 255, 255))
                store_text = BUTTON_FONT.render("Store", True, (255, 255, 255))
                
                screen.blit(button_text, (birdiary_button.x + 10, birdiary_button.y + 6))
                screen.blit(store_text, (store_button.x + 10, store_button.y + 6))
                
                draw_error_messages(screen, error_font)
                
                pygame.display.flip()
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if birdiary_button.collidepoint(event.pos):
                            collected_set = set(b.name for b in collected_birds)
                            #button_click_sound.play()
                            game_status = await show_birdiary(screen, collected_set, bird_types)
                            #button_click_sound.play()
                            running = game_status
                        elif store_button.collidepoint(event.pos):
                            #button_click_sound.play()
                            game_status, gold = await show_store(screen, purchased_deco, gold, deco_assets, deco_prices, DECO_SPAWN_POINTS, deco_click_sound)
                            #button_click_sound.play()
                            running = game_status
                        else:
                            mx, my = event.pos
                            for obj in spawned_birds[:]:
                                rect = obj["bird"].image.get_rect(topleft=obj["pos"])
                                if rect.collidepoint(mx, my):
                                    collected_birds.append(obj["bird"])
                                    print(obj["bird"].rarity)
                                    if obj["bird"].rarity == "common":
                                        print("should play sound!!!!!!!!!!!!!!!!!!!!!!!!!")
                                        #common_click_sound.play() 
                                    elif obj["bird"].rarity == "uncommon":
                                        print("should play sound!!!!!!!!!!!!!!!!!!!!!!!!!")
                                        #uncommon_click_sound.play() 
                                    elif obj["bird"].rarity == "rare":
                                        print("should play sound!!!!!!!!!!!!!!!!!!!!!!!!!")
                                        #rare_click_sound.play()
                                    elif obj["bird"].rarity == "epic":
                                        print("should play sound!!!!!!!!!!!!!!!!!!!!!!!!!")
                                        #epic_click_sound.play()
                                    elif obj["bird"].rarity == "legendary":
                                        print("should play sound!!!!!!!!!!!!!!!!!!!!!!!!!")
                                        #legendary_click_sound.play()
                                    print(f"Collected: {obj['bird'].name} @ {datetime.now()}")
                                    occupied_spawn.discard(obj["pos"])
                                    spawned_birds.remove(obj)
                                    break
            
            except Exception as e:
                # Main game loop error handling
                add_error_message(f"Game loop error: {str(e)}")
            
            try:
                clock.tick(30)
                await asyncio.sleep(0)
            except Exception as e:
                add_error_message(f"Clock error: {str(e)}")
        
        pygame.quit()
    
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        try:
            if 'screen' in locals():
                error_font = pygame.font.Font(None, 24)
                screen.fill((0, 0, 0))
                error_text = error_font.render(f"FATAL ERROR: {str(e)}", True, (255, 0, 0))
                screen.blit(error_text, (10, 10))
                pygame.display.flip()
                await asyncio.sleep(5)  # Show error for 5 seconds
        except:
            pass
        finally:
            try:
                pygame.quit()
            except:
                pass

# Entry point
if __name__ == "__main__":
    asyncio.run(main())