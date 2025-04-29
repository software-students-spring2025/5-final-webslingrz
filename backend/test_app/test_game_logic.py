import pygame
import pytest
import os
from unittest import mock
import bird_game.main as game_main
import asyncio

@pytest.fixture(autouse=True)
def setup_pygame():
    """Ensure pygame is initialized for all tests"""
    pygame.init()
    yield
    pygame.quit()

def test_add_error_message_and_limit():
    game_main.error_messages.clear()

    for i in range(game_main.MAX_ERROR_MESSAGES + 2):
        game_main.add_error_message(f"Error {i}")

    assert len(game_main.error_messages) == game_main.MAX_ERROR_MESSAGES
    assert game_main.error_messages[0] == "Error 2"

def test_remove_error_message():
    game_main.error_messages.clear()
    game_main.add_error_message("Some error")

    game_main.remove_error_message()
    assert len(game_main.error_messages) == 0

def test_greyscale_surface_success():
    surface = pygame.Surface((10, 10))
    surface.fill((255, 0, 0))  # Red
    grey_surface = game_main.greyscale_surface(surface)

    assert isinstance(grey_surface, pygame.Surface)

def test_greyscale_surface_fail():
    """Force failure inside greyscale_surface"""
    with mock.patch('pygame.surfarray.array3d', side_effect=Exception("Mocked error")):
        surface = pygame.Surface((10, 10))
        result = game_main.greyscale_surface(surface)
        assert result == surface  # Should return the original

def test_load_scaled_image_success(tmp_path):
    """Test loading and scaling an image"""
    test_img_path = tmp_path / "test_image.png"

    surface = pygame.Surface((100, 100))
    pygame.image.save(surface, str(test_img_path))

    loaded = game_main.load_scaled_image(str(test_img_path), 50)
    assert isinstance(loaded, pygame.Surface)
    assert loaded.get_width() == 50

def test_load_scaled_image_fail():
    """Test fallback placeholder surface when load fails"""
    # Provide a non-existent path
    loaded = game_main.load_scaled_image("non_existent.png", 50)
    assert isinstance(loaded, pygame.Surface)
    assert loaded.get_width() == 50

def test_bird_init():
    """Simple test for Bird initialization"""
    img = pygame.Surface((10, 10))
    bird = game_main.Bird(name="TestBird", image=img, gold_per_minute=10, spawn_chance=0.1, rarity="common")

    assert bird.name == "TestBird"
    assert bird.image == img
    assert bird.gold_per_minute == 10
    assert bird.spawn_chance == 0.1
    assert bird.rarity == "common"

@pytest.mark.asyncio
async def test_show_birdiary(monkeypatch):
    screen = pygame.Surface((800, 600))
    collected_set = {"TestBird"}
    bird_types = [game_main.Bird(name="TestBird", image=screen, gold_per_minute=10, spawn_chance=0.1, rarity="common")]

    fake_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (790, 30)})
    monkeypatch.setattr(pygame, "event", mock.Mock(get=mock.Mock(side_effect=[[fake_event], []])))
    monkeypatch.setattr(pygame.display, "flip", lambda: None)

    result = await game_main.show_birdiary(screen, collected_set, bird_types)
    assert result is True or result is False

@pytest.mark.asyncio
async def test_show_birdiary_exception(monkeypatch):
    screen = pygame.Surface((800, 600))
    collected_set = {"TestBird"}
    bird_types = [game_main.Bird(name="TestBird", image=screen, gold_per_minute=10, spawn_chance=0.1, rarity="common")]

    monkeypatch.setattr(pygame.display, "flip", mock.Mock(side_effect=Exception("Forced error")))
    monkeypatch.setattr(pygame, "event", mock.Mock(get=mock.Mock(return_value=[])))

    result = await game_main.show_birdiary(screen, collected_set, bird_types)
    assert result is True


@pytest.mark.asyncio
async def test_show_store(monkeypatch):
    screen = pygame.Surface((800, 600))
    purchased_set = set()
    gold = 1000
    deco_assets = {"Lamp": pygame.Surface((50, 50))}
    deco_prices = {"Lamp": 100}
    deco_spawn_points = {"Lamp": (100, 100)}
    deco_click_sound = mock.Mock()

    fake_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (790, 30)})
    monkeypatch.setattr(pygame, "event", mock.Mock(get=mock.Mock(side_effect=[[fake_event], []])))
    monkeypatch.setattr(pygame.display, "flip", lambda: None)

    result, updated_gold = await game_main.show_store(screen, purchased_set, gold, deco_assets, deco_prices, deco_spawn_points, deco_click_sound)
    assert isinstance(updated_gold, (int, float))

@pytest.mark.asyncio
async def test_show_store_exception(monkeypatch):
    screen = pygame.Surface((800, 600))
    purchased_set = set()
    gold = 1000
    deco_assets = {"Lamp": pygame.Surface((50, 50))}
    deco_prices = {"Lamp": 100}
    deco_spawn_points = {"Lamp": (100, 100)}
    deco_click_sound = mock.Mock()

    monkeypatch.setattr(pygame.display, "flip", mock.Mock(side_effect=Exception("Forced error")))
    monkeypatch.setattr(pygame, "event", mock.Mock(get=mock.Mock(return_value=[])))

    result, updated_gold = await game_main.show_store(screen, purchased_set, gold, deco_assets, deco_prices, deco_spawn_points, deco_click_sound)
    assert isinstance(updated_gold, (int, float))

@pytest.mark.asyncio
async def test_show_store_purchase(monkeypatch):
    screen = pygame.Surface((800, 600))
    purchased_set = set()
    gold = 500
    deco_assets = {"Lamp": pygame.Surface((50, 50))}
    deco_prices = {"Lamp": 100}
    deco_spawn_points = {"Lamp": (100, 100)}
    deco_click_sound = mock.Mock()

    fake_buy_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (50, 100)})
    fake_back_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (790, 30)})

    monkeypatch.setattr(pygame, "event", mock.Mock(get=mock.Mock(side_effect=[[fake_buy_event], [fake_back_event], []])))
    monkeypatch.setattr(pygame.display, "flip", lambda: None)

    result, updated_gold = await game_main.show_store(screen, purchased_set, gold, deco_assets, deco_prices, deco_spawn_points, deco_click_sound)
    assert updated_gold < gold
    assert "Lamp" in purchased_set

def test_draw_error_messages(monkeypatch):
    screen = pygame.Surface((800, 600))
    font = pygame.font.SysFont("Arial", 18)

    game_main.error_messages.clear()
    game_main.error_messages.append("Test error")

    monkeypatch.setattr(pygame.display, "flip", lambda: None)

    game_main.draw_error_messages(screen, font)

@pytest.mark.asyncio
async def test_main_startup(monkeypatch):
    monkeypatch.setattr(pygame.display, "set_mode", lambda size: pygame.Surface(size))
    monkeypatch.setattr(pygame.display, "set_caption", lambda title: None)
    monkeypatch.setattr(pygame.display, "flip", lambda: None)

    monkeypatch.setattr(game_main, "load_scaled_image", lambda path, width: pygame.Surface((width, width)))

    monkeypatch.setattr(game_main.time, "time", lambda: 100000)
    monkeypatch.setattr(game_main.random, "random", lambda: 0.5)
    monkeypatch.setattr(game_main.random, "shuffle", lambda x: None)

    mock_clock = mock.Mock()
    mock_clock.get_time.return_value = 1000
    monkeypatch.setattr(pygame.time, "Clock", lambda: mock_clock)

    quit_event = pygame.event.Event(pygame.QUIT)
    monkeypatch.setattr(pygame, "event", mock.Mock(get=mock.Mock(side_effect=[[quit_event], []])))

    monkeypatch.setattr(pygame.mixer, "init", lambda: None)

    await game_main.main()

@pytest.mark.asyncio
async def test_main_loop_exception(monkeypatch):
    monkeypatch.setattr(pygame.display, "set_mode", lambda size: pygame.Surface(size))
    monkeypatch.setattr(pygame.display, "set_caption", lambda title: None)
    monkeypatch.setattr(pygame.display, "flip", lambda: None)

    monkeypatch.setattr(pygame.event, "get", mock.Mock(side_effect=Exception("Forced crash")))

    await game_main.main()

@pytest.mark.asyncio
async def test_main_collect_bird(monkeypatch):
    fake_bird = game_main.Bird("TestBird", pygame.Surface((10, 10)), 10, 1.0, "common")
    monkeypatch.setattr(game_main.random, "random", lambda: 0)  # Always spawn
    monkeypatch.setattr(game_main.random, "shuffle", lambda x: None)

    spawn_point = (50, 135)
    bird_rect = pygame.Rect(spawn_point, (10, 10))
    fake_spawn_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": bird_rect.center})
    quit_event = pygame.event.Event(pygame.QUIT)

    monkeypatch.setattr(pygame, "event", mock.Mock(get=mock.Mock(side_effect=[[fake_spawn_event], [quit_event]])))

    monkeypatch.setattr(game_main.mixer, "Sound", lambda *args, **kwargs: mock.Mock(play=lambda: None))

    # Run main
    await game_main.main()
