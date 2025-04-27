import pytest
import os
import sys
import pygame
import asyncio
from unittest.mock import MagicMock

# Mock modules that exist only in the web environment
sys.modules['js'] = MagicMock()

# Add emscripten runtime attribute to identify non-browser environment
sys.emscripten_runtime = False

# Set up a headless pygame environment
os.environ['SDL_VIDEODRIVER'] = 'dummy'

# Initialize pygame for all tests
def pytest_configure(config):
    """Initialize pygame once for all tests"""
    pygame.init()

def pytest_unconfigure(config):
    """Quit pygame after all tests are done"""
    pygame.quit()

# Helper for async tests (required for pytest-asyncio)
@pytest.fixture
def event_loop():
    """Create an event loop for each test case"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()