import pytest
import pygame
import asyncio
import os
import bird_game.main as game_main
from unittest import mock

@pytest.fixture(autouse=True)
def setup_pygame():
    pygame.init()
    yield
    pygame.quit()

@pytest.fixture
def dummy_surface():
    return pygame.Surface((10, 10))

def test_add_error_message_and_limit():
    game_main.error_messages.clear()
    for i in range(game_main.MAX_ERROR_MESSAGES + 2):
        game_main.add_error_message(f"Error {i}")
    assert len(game_main.error_messages) == game_main.MAX_ERROR_MESSAGES
    assert "Error" in game_main.error_messages[0]

def test_remove_error_message():
    game_main.error_messages.clear()
    game_main.add_error_message("Temporary error")
    game_main.remove_error_message()
    assert len(game_main.error_messages) == 0

def test_draw_error_messages(dummy_surface, monkeypatch):
    font = pygame.font.SysFont(None, 24)
    game_main.error_messages.clear()
    game_main.error_messages.append("Example error")
    monkeypatch.setattr(pygame.display, "flip", lambda: None)
    game_main.draw_error_messages(dummy_surface, font)

def test_greyscale_surface_success(dummy_surface):
    grey_surface = game_main.greyscale_surface(dummy_surface)
    assert isinstance(grey_surface, pygame.Surface)

def test_greyscale_surface_failure(monkeypatch):
    monkeypatch.setattr("pygame.surfarray.array3d", mock.Mock(side_effect=Exception()))
    surface = pygame.Surface((10, 10))
    result = game_main.greyscale_surface(surface)
    assert result == surface

def test_load_scaled_image_success(tmp_path):
    img_path = tmp_path / "test_image.png"
    surface = pygame.Surface((100, 100))
    pygame.image.save(surface, str(img_path))
    loaded_img = game_main.load_scaled_image(str(img_path), 50)
    assert isinstance(loaded_img, pygame.Surface)

def test_load_scaled_image_failure():
    result = game_main.load_scaled_image("fake_path/image.png", 50)
    assert isinstance(result, pygame.Surface)

def test_bird_init(dummy_surface):
    bird = game_main.Bird(name="Test", image=dummy_surface, gold_per_minute=10, spawn_chance=0.5, rarity="common")
    assert bird.name == "Test"
    assert bird.gold_per_minute == 10
    assert bird.rarity == "common"

@pytest.mark.asyncio
async def test_show_birdiary_basic(monkeypatch):
    screen = pygame.Surface((800, 600))
    birds = [game_main.Bird(name="Birdy", image=screen, gold_per_minute=5, spawn_chance=0.1, rarity="common")]
    collected = {"Birdy"}
    monkeypatch.setattr(pygame, "event", mock.Mock(get=mock.Mock(side_effect=[[pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (790, 30)})], []])))
    monkeypatch.setattr(pygame.display, "flip", lambda: None)
    monkeypatch.setattr(asyncio, "sleep", mock.AsyncMock())
    result = await game_main.show_birdiary(screen, collected, birds)
    assert result in (True, False)

@pytest.mark.asyncio
async def test_show_birdiary_crash(monkeypatch):
    screen = pygame.Surface((800, 600))
    birds = [game_main.Bird(name="Broken", image=screen, gold_per_minute=5, spawn_chance=0.1, rarity="common")]
    monkeypatch.setattr(pygame.display, "flip", mock.Mock(side_effect=Exception()))
    monkeypatch.setattr(pygame, "event", mock.Mock(get=mock.Mock(return_value=[])))
    monkeypatch.setattr(asyncio, "sleep", mock.AsyncMock())
    result = await game_main.show_birdiary(screen, {"Broken"}, birds)
    assert result is True

@pytest.mark.asyncio
async def test_show_store_basic(monkeypatch):
    screen = pygame.Surface((800, 600))
    purchased = set()
    deco_assets = {"Lamp": pygame.Surface((50, 50))}
    deco_prices = {"Lamp": 100}
    deco_spawn_points = {"Lamp": (100, 100)}
    deco_click_sound = mock.Mock()
    monkeypatch.setattr(pygame.display, "flip", lambda: None)
    monkeypatch.setattr(pygame, "event", mock.Mock(get=mock.Mock(side_effect=[[pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (790, 30)})], []])))
    monkeypatch.setattr(asyncio, "sleep", mock.AsyncMock())
    _, gold = await game_main.show_store(screen, purchased, 500, deco_assets, deco_prices, deco_spawn_points, deco_click_sound)
    assert isinstance(gold, (int, float))

@pytest.mark.asyncio
async def test_show_store_crash(monkeypatch):
    screen = pygame.Surface((800, 600))
    purchased = set()
    deco_assets = {"Lamp": pygame.Surface((50, 50))}
    deco_prices = {"Lamp": 100}
    deco_spawn_points = {"Lamp": (100, 100)}
    deco_click_sound = mock.Mock()
    monkeypatch.setattr(pygame.display, "flip", mock.Mock(side_effect=Exception()))
    monkeypatch.setattr(pygame, "event", mock.Mock(get=mock.Mock(return_value=[])))
    monkeypatch.setattr(asyncio, "sleep", mock.AsyncMock())
    _, gold = await game_main.show_store(screen, purchased, 500, deco_assets, deco_prices, deco_spawn_points, deco_click_sound)
    assert isinstance(gold, (int, float))
