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
bg = load_scaled_image(os.path.join(BASE_DIR, "assets/backgrounds/forest.png"), screen_width)

# pygame.image.load(os.path.join(BASE_DIR, "assets/backgrounds/forest.png"))

# Bird image scaled to 1/10th of screen width (~80px wide)
target_bird_width = screen_width // 10
duckling_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/duckling.png"), target_bird_width
)
alien_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/alien.png"), target_bird_width
)
cherry_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/cherry.png"), target_bird_width
)
confused_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/confused.png"), target_bird_width
)
crow_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/crow.png"), target_bird_width
)
cyan_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/cyan.png"), target_bird_width
)
dandy_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/dandy.png"), target_bird_width
)
eyelash_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/eyelash.png"), target_bird_width
)
gnome_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/gnome.png"), target_bird_width
)
green_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/green.png"), target_bird_width
)
hamilton_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/hamilton.png"), target_bird_width
)
king_rook_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/king_rook.png"), target_bird_width
)
kiwi_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/kiwi.png"), target_bird_width
)
little_guy_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/little_guy.png"), target_bird_width
)
mafia_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/mafia.png"), target_bird_width
)
onigiri_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/onigiri.png"), target_bird_width
)
owl_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/owl.png"), target_bird_width
)
blue_parakeet_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/parakeet_blue.png"), target_bird_width
)
yellow_parakeet_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/parakeet_yellow.png"), target_bird_width
)
pirate_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/pirate.png"), target_bird_width
)
pitiful_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/pitiful.png"), target_bird_width
)
pleh_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/pleh.png"), target_bird_width
)
purple_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/purple.png"), target_bird_width
)
robin_hood_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/robin_hood.png"), target_bird_width
)
sans_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/sans_undertale.png"), target_bird_width
)
seed_dealer_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/seed_dealer.png"), target_bird_width
)
snowy_owl_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/snowy_owl.png"), target_bird_width
)
sonic_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/sonic.png"), target_bird_width
)
space_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/space.png"), target_bird_width
)
spiderman_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/spiderman.png"), target_bird_width
)
stork_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/stork.png"), target_bird_width
)
tomato_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/tomato.png"), target_bird_width
)
toucan_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/toucan.png"), target_bird_width
)
webslinger_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/webslinger.png"), target_bird_width
)
zelda_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/zelda.png"), target_bird_width
)
money_mogul_img = load_scaled_image(
    os.path.join(BASE_DIR, "assets/birds/money_mogul.png"), target_bird_width
)



FONT = pygame.font.SysFont("Arial", 24)


# Bird data
class Bird:
    def __init__(self, name, image, gold_per_minute, spawn_chance, cooldown=1):
        self.name = name
        self.image = image
        self.gold_per_minute = gold_per_minute
        self.spawn_chance = spawn_chance
        self.cooldown = cooldown  # seconds between spawn checks


duckling = Bird("Duckling", duckling_img, gold_per_minute=1, spawn_chance=0.10)
alien = Bird("Alien", alien_img, gold_per_minute=1, spawn_chance=0.15)
cherry = Bird("Cherry", cherry_img, gold_per_minute=1, spawn_chance=0.15)
confused = Bird("Confused", confused_img, gold_per_minute=1, spawn_chance=0.15)
crow = Bird("Crow", crow_img, gold_per_minute=1, spawn_chance=0.15)
cyan = Bird("Cyan", cyan_img, gold_per_minute=1, spawn_chance=0.15)
dandy = Bird("Dandy", dandy_img, gold_per_minute=1, spawn_chance=0.05)
eyelash = Bird("Eyelash", eyelash_img, gold_per_minute=1, spawn_chance=0.05)
gnome = Bird("Gnome", gnome_img, gold_per_minute=1, spawn_chance=0.15)
green = Bird("Green", green_img, gold_per_minute=1, spawn_chance=0.15)
hamilton = Bird("Hamilton", hamilton_img, gold_per_minute=1, spawn_chance=0.15)
king_rook = Bird("King Rook", king_rook_img, gold_per_minute=1, spawn_chance=0.15)
kiwi = Bird("Kiwi", kiwi_img, gold_per_minute=1, spawn_chance=0.15)
little_guy = Bird("Little Guy", little_guy_img, gold_per_minute=1, spawn_chance=0.05)
mafia = Bird("Mafia", mafia_img, gold_per_minute=1, spawn_chance=0.25)
onigiri = Bird("Onigiri", onigiri_img, gold_per_minute=1, spawn_chance=0.25)
owl = Bird("Owl", owl_img, gold_per_minute=1, spawn_chance=0.25)
blue_parakeet = Bird(
    "Blue Parakeet", blue_parakeet_img, gold_per_minute=1, spawn_chance=0.05
)
yellow_parakeet = Bird(
    "Yellow Parakeet", yellow_parakeet_img, gold_per_minute=1, spawn_chance=0.05
)
pirate = Bird("Pirate", pirate_img, gold_per_minute=1, spawn_chance=0.25)
pitiful = Bird("Pitiful", pitiful_img, gold_per_minute=1, spawn_chance=0.05)
pleh = Bird("Pleh", pleh_img, gold_per_minute=1, spawn_chance=0.25)
purple = Bird("Purple", purple_img, gold_per_minute=1, spawn_chance=0.25)
robin_hood = Bird("Robin Hood", robin_hood_img, gold_per_minute=1, spawn_chance=0.35)
sans = Bird("Sans Undertale", sans_img, gold_per_minute=1, spawn_chance=0.35)
dealer = Bird("Seed Dealer", seed_dealer_img, gold_per_minute=1, spawn_chance=0.35)
snowy_owl = Bird("Snowy Owl", snowy_owl_img, gold_per_minute=1, spawn_chance=0.35)
sonic = Bird("Sonic", sonic_img, gold_per_minute=1, spawn_chance=0.35)
space = Bird("Space", space_img, gold_per_minute=1, spawn_chance=0.15)
spiderman = Bird("Spiderman", spiderman_img, gold_per_minute=1, spawn_chance=0.35)
stork = Bird("Stork", stork_img, gold_per_minute=1, spawn_chance=0.05)
tomato = Bird("Tomato", tomato_img, gold_per_minute=1, spawn_chance=0.05)
toucan = Bird("Toucan", toucan_img, gold_per_minute=1, spawn_chance=0.35)
webslinger = Bird("Webslinger", webslinger_img, gold_per_minute=1, spawn_chance=0.35)
zelda = Bird("Zelda", zelda_img, gold_per_minute=1, spawn_chance=0.35)
money_mogul = Bird("Money Mogul", money_mogul_img, gold_per_minute=100, spawn_chance=0.35)

bird_types = [
    duckling,
    alien,
    cherry,
    confused,
    crow,
    cyan,
    dandy,
    eyelash,
    gnome,
    green,
    hamilton,
    king_rook,
    kiwi,
    little_guy,
    mafia,
    onigiri,
    owl,
    blue_parakeet,
    yellow_parakeet,
    pirate,
    pitiful,
    pleh,
    purple,
    robin_hood,
    sans,
    dealer,
    snowy_owl,
    sonic,
    space,
    spiderman,
    stork,
    tomato,
    toucan,
    webslinger,
    zelda,
]

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
