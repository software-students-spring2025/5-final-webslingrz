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

def test_draw_error_messages(monkeypatch):
    screen = pygame.Surface((800, 600))
    font = pygame.font.SysFont("Arial", 18)

    game_main.error_messages.clear()
    game_main.error_messages.append("Test error")

    monkeypatch.setattr(pygame.display, "flip", lambda: None)

    game_main.draw_error_messages(screen, font)

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
async def test_show_birdiary_scroll(monkeypatch):
    screen = pygame.Surface((800, 600))
    collected_set = {"TestBird"}
    bird_types = [game_main.Bird(name="TestBird", image=screen, gold_per_minute=10, spawn_chance=0.1, rarity="common")]

    scroll_event = pygame.event.Event(pygame.MOUSEWHEEL, {"y": -1})
    back_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (790, 30)})

    monkeypatch.setattr(pygame, "event", mock.Mock(get=mock.Mock(side_effect=[[scroll_event], [back_event], []])))
    monkeypatch.setattr(pygame.display, "flip", lambda: None)

    result = await game_main.show_birdiary(screen, collected_set, bird_types)
    assert result

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

@pytest.mark.asyncio
async def test_show_store_not_enough_gold(monkeypatch):
    screen = pygame.Surface((800, 600))
    purchased_set = set()
    gold = 50
    deco_assets = {"Lamp": pygame.Surface((50, 50))}
    deco_prices = {"Lamp": 100}
    deco_spawn_points = {"Lamp": (100, 100)}
    deco_click_sound = mock.Mock()

    fake_buy_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (50, 100)})
    fake_back_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (790, 30)})

    monkeypatch.setattr(pygame, "event", mock.Mock(get=mock.Mock(side_effect=[[fake_buy_event], [fake_back_event], []])))
    monkeypatch.setattr(pygame.display, "flip", lambda: None)

    result, updated_gold = await game_main.show_store(screen, purchased_set, gold, deco_assets, deco_prices, deco_spawn_points, deco_click_sound)

    assert "Lamp" not in purchased_set

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
async def test_main_fatal_error(monkeypatch):
    monkeypatch.setattr(pygame.display, "set_mode", mock.Mock(side_effect=Exception("Forced fatal error")))
    monkeypatch.setattr(pygame.font, "Font", lambda *args, **kwargs: mock.Mock(render=lambda text, antialias, color: pygame.Surface((100, 30))))
    monkeypatch.setattr(pygame.display, "flip", lambda: None)
    monkeypatch.setattr(pygame, "display", mock.Mock(flip=lambda: None))
    monkeypatch.setattr(pygame, "quit", lambda: None)
    monkeypatch.setattr(asyncio, "sleep", mock.AsyncMock())

    await game_main.main()

@pytest.mark.asyncio
async def test_main_open_birdiary(monkeypatch):
    monkeypatch.setattr(pygame.display, "set_mode", lambda size: pygame.Surface(size))
    monkeypatch.setattr(pygame.display, "set_caption", lambda title: None)
    monkeypatch.setattr(pygame.display, "flip", lambda: None)
    monkeypatch.setattr(game_main.time, "time", lambda: 100000)
    monkeypatch.setattr(game_main.random, "random", lambda: 0.5)
    monkeypatch.setattr(game_main.random, "shuffle", lambda x: None)
    mock_clock = mock.Mock()
    mock_clock.get_time.return_value = 1000
    monkeypatch.setattr(pygame.time, "Clock", lambda: mock_clock)

    monkeypatch.setattr(game_main, "load_scaled_image", lambda path, width: pygame.Surface((width, width)))

    birdiary_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (650, 20)})
    quit_event = pygame.event.Event(pygame.QUIT)

    monkeypatch.setattr(pygame, "event", mock.Mock(get=mock.Mock(side_effect=[[birdiary_click], [quit_event]])))
    monkeypatch.setattr(pygame.mixer, "init", lambda: None)
    monkeypatch.setattr(game_main, "show_birdiary", mock.AsyncMock(return_value=True))

    await game_main.main()

@pytest.mark.asyncio
async def test_main_open_store(monkeypatch):
    monkeypatch.setattr(pygame.display, "set_mode", lambda size: pygame.Surface(size))
    monkeypatch.setattr(pygame.display, "set_caption", lambda title: None)
    monkeypatch.setattr(pygame.display, "flip", lambda: None)
    monkeypatch.setattr(game_main.time, "time", lambda: 100000)
    monkeypatch.setattr(game_main.random, "random", lambda: 0.5)
    monkeypatch.setattr(game_main.random, "shuffle", lambda x: None)
    mock_clock = mock.Mock()
    mock_clock.get_time.return_value = 1000
    monkeypatch.setattr(pygame.time, "Clock", lambda: mock_clock)

    monkeypatch.setattr(game_main, "load_scaled_image", lambda path, width: pygame.Surface((width, width)))

    store_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (650, 70)})  # Store button is around y=60
    quit_event = pygame.event.Event(pygame.QUIT)

    monkeypatch.setattr(pygame, "event", mock.Mock(get=mock.Mock(side_effect=[[store_click], [quit_event]])))
    monkeypatch.setattr(pygame.mixer, "init", lambda: None)
    monkeypatch.setattr(game_main, "show_store", mock.AsyncMock(return_value=(True, 100)))

    await game_main.main()

@pytest.mark.asyncio
async def test_main_purchase_all_decor(monkeypatch):
    monkeypatch.setattr(pygame.display, "set_mode", lambda size: pygame.Surface(size))
    monkeypatch.setattr(pygame.display, "set_caption", lambda title: None)
    monkeypatch.setattr(pygame.display, "flip", lambda: None)
    monkeypatch.setattr(game_main, "load_scaled_image", lambda path, width: pygame.Surface((width, width)))
    monkeypatch.setattr(game_main.time, "time", lambda: 100000)
    monkeypatch.setattr(game_main.random, "random", lambda: 1)  # prevent random spawns
    monkeypatch.setattr(game_main.random, "shuffle", lambda x: None)

    mock_clock = mock.Mock()
    mock_clock.get_time.return_value = 1000
    monkeypatch.setattr(pygame.time, "Clock", lambda: mock_clock)

    monkeypatch.setattr(pygame.mixer, "init", lambda: None)
    monkeypatch.setattr(pygame.mixer, "Sound", lambda *args, **kwargs: mock.Mock(play=lambda: None))

    # Sequence of deco purchases
    decorations_to_buy = ["Lamp", "Bath", "Clock", "Froggy Fountain", "Sofa"]
    purchase_index = {"index": 0}

    async def fake_show_store(screen, purchased_set, gold, deco_assets, deco_prices, deco_spawn_points, deco_click_sound):
        if purchase_index["index"] < len(decorations_to_buy):
            purchased_set.add(decorations_to_buy[purchase_index["index"]])
            purchase_index["index"] += 1
        return True, gold

    monkeypatch.setattr(game_main, "show_store", fake_show_store)
    monkeypatch.setattr(game_main, "show_birdiary", mock.AsyncMock(return_value=True))

    # simulate clicking "store" 5 times to buy everything, then quit
    store_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": (650, 70)})
    quit_event = pygame.event.Event(pygame.QUIT)

    monkeypatch.setattr(pygame, "event", mock.Mock(get=mock.Mock(side_effect=[
        [store_click], [store_click], [store_click], [store_click], [store_click], [quit_event]
    ])))

    await game_main.main()


