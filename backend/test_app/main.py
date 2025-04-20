import pygame
import asyncio

async def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    font = pygame.font.SysFont("Arial", 36)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.fill((0, 64, 128))
        text = font.render("Hello, Pygbag!", True, (255, 255, 255))
        screen.blit(text, (400 - text.get_width() // 2, 300 - text.get_height() // 2))
        pygame.display.flip()
        
        await asyncio.sleep(0)
    
    pygame.quit()

asyncio.run(main())