"""Test fixtures for Helvar integration."""
import pytest
from unittest.mock import Mock, AsyncMock, MagicMock
import aiohelvar


@pytest.fixture
def mock_device():
    """Create a mock Helvar device."""
    device = Mock(spec=aiohelvar.devices.Device)
    device.address = "1.2.3.4"
    device.name = "Test Light"
    device.brightness = 128
    return device


@pytest.fixture
def mock_router():
    """Create a mock router."""
    router = Mock()
    router.api = Mock()
    router.api.devices = Mock()
    router.api.devices.get_light_devices = Mock(return_value=[])
    router.api.devices.register_subscription = Mock()
    router.api.devices.set_device_brightness = AsyncMock()
    return router


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = Mock()
    hass.data = {}
    return hass


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    config_entry = Mock()
    config_entry.entry_id = "test_entry_id"
    return config_entry


@pytest.fixture
def mock_add_entities():
    """Create a mock add_entities function."""
    return AsyncMock()