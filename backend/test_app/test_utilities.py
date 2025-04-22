import pytest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bird_game import greyscale_surface, load_scaled_image
import pygame

@pytest.fixture(scope="module", autouse=True)
def init_pygame():
    pygame.init()
    yield
    pygame.quit()

def test_load_scaled_image_success():
    # Use a known image that should exist in assets for the test
    test_path = os.path.join("assets", "birds", "duckling.png")
    image = load_scaled_image(test_path, 50)
    assert isinstance(image, pygame.Surface)

def test_load_scaled_image_failure(monkeypatch):
    def fake_load(path):
        raise FileNotFoundError("fail")

    monkeypatch.setattr(pygame.image, "load", fake_load)
    surface = load_scaled_image("fake.png", 50)
    assert isinstance(surface, pygame.Surface)

def test_greyscale_surface():
    surface = pygame.Surface((10, 10))
    surface.fill((255, 0, 0))
    grey_surface = greyscale_surface(surface)
    assert isinstance(grey_surface, pygame.Surface)
