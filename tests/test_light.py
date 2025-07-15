"""Tests for the Helvar light platform."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode
from homeassistant.const import STATE_ON, STATE_OFF

from custom_components.helvar.light import HelvarLight, async_setup_entry
from custom_components.helvar.const import DOMAIN as HELVAR_DOMAIN


class TestHelvarLight:
    """Test the HelvarLight class."""

    def test_init(self, mock_device, mock_router):
        """Test HelvarLight initialization."""
        light = HelvarLight(mock_device, mock_router)
        
        assert light.device == mock_device
        assert light.router == mock_router
        mock_router.api.devices.register_subscription.assert_called_once()

    def test_unique_id(self, mock_device, mock_router):
        """Test unique_id property."""
        light = HelvarLight(mock_device, mock_router)
        assert light.unique_id == "1.2.3.4-light"

    def test_name(self, mock_device, mock_router):
        """Test name property."""
        light = HelvarLight(mock_device, mock_router)
        assert light.name == "Test Light"

    def test_brightness(self, mock_device, mock_router):
        """Test brightness property."""
        light = HelvarLight(mock_device, mock_router)
        assert light.brightness == 128

    def test_is_on_when_brightness_greater_than_zero(self, mock_device, mock_router):
        """Test is_on returns True when brightness > 0."""
        mock_device.brightness = 100
        light = HelvarLight(mock_device, mock_router)
        assert light.is_on is True

    def test_is_on_when_brightness_is_zero(self, mock_device, mock_router):
        """Test is_on returns False when brightness is 0."""
        mock_device.brightness = 0
        light = HelvarLight(mock_device, mock_router)
        assert light.is_on is False

    def test_supported_color_modes(self, mock_device, mock_router):
        """Test supported_color_modes property."""
        light = HelvarLight(mock_device, mock_router)
        assert light.supported_color_modes == [ColorMode.BRIGHTNESS]

    def test_color_mode(self, mock_device, mock_router):
        """Test color_mode property."""
        light = HelvarLight(mock_device, mock_router)
        assert light.color_mode == ColorMode.BRIGHTNESS

    @pytest.mark.asyncio
    async def test_async_turn_on_with_brightness(self, mock_device, mock_router):
        """Test turning on the light with brightness."""
        light = HelvarLight(mock_device, mock_router)
        
        await light.async_turn_on(**{ATTR_BRIGHTNESS: 200})
        
        mock_router.api.devices.set_device_brightness.assert_called_once_with(
            mock_device.address, 200
        )

    @pytest.mark.asyncio
    async def test_async_turn_on_without_brightness(self, mock_device, mock_router):
        """Test turning on the light without brightness (defaults to 255)."""
        light = HelvarLight(mock_device, mock_router)
        
        await light.async_turn_on()
        
        mock_router.api.devices.set_device_brightness.assert_called_once_with(
            mock_device.address, 255
        )

    @pytest.mark.asyncio
    async def test_async_turn_off(self, mock_device, mock_router):
        """Test turning off the light."""
        light = HelvarLight(mock_device, mock_router)
        
        await light.async_turn_off()
        
        mock_router.api.devices.set_device_brightness.assert_called_once_with(
            mock_device.address, 0
        )

    @pytest.mark.asyncio
    async def test_subscription_callback(self, mock_device, mock_router):
        """Test that subscription callback triggers state update."""
        light = HelvarLight(mock_device, mock_router)
        
        # Mock the async_write_ha_state method
        light.async_write_ha_state = Mock()
        
        # Get the callback that was registered
        callback = mock_router.api.devices.register_subscription.call_args[0][1]
        
        # Call the callback
        await callback(mock_device)
        
        # Verify state update was triggered
        light.async_write_ha_state.assert_called_once()


class TestAsyncSetupEntry:
    """Test the async_setup_entry function."""

    @pytest.mark.asyncio
    async def test_async_setup_entry(self, mock_hass, mock_config_entry, mock_add_entities, mock_router):
        """Test async_setup_entry sets up devices correctly."""
        # Setup mock devices
        mock_device1 = Mock()
        mock_device1.address = "1.2.3.4"
        mock_device1.name = "Light 1"
        mock_device1.brightness = 100
        
        mock_device2 = Mock()
        mock_device2.address = "1.2.3.5"
        mock_device2.name = "Light 2"
        mock_device2.brightness = 200
        
        mock_router.api.devices.get_light_devices.return_value = [mock_device1, mock_device2]
        
        # Setup hass data
        mock_hass.data = {HELVAR_DOMAIN: {mock_config_entry.entry_id: mock_router}}
        
        # Mock the HelvarLight class
        with patch('custom_components.helvar.light.HelvarLight') as mock_light_class:
            mock_light_instance1 = Mock()
            mock_light_instance2 = Mock()
            mock_light_class.side_effect = [mock_light_instance1, mock_light_instance2]
            
            await async_setup_entry(mock_hass, mock_config_entry, mock_add_entities)
        
        # Verify that HelvarLight was created for each device
        assert mock_light_class.call_count == 2
        mock_light_class.assert_any_call(mock_device1, mock_router)
        mock_light_class.assert_any_call(mock_device2, mock_router)
        
        # Verify that entities were added
        mock_add_entities.assert_called_once_with([mock_light_instance1, mock_light_instance2])

    @pytest.mark.asyncio
    async def test_async_setup_entry_no_devices(self, mock_hass, mock_config_entry, mock_add_entities, mock_router):
        """Test async_setup_entry with no devices."""
        # Setup empty device list
        mock_router.api.devices.get_light_devices.return_value = []
        
        # Setup hass data
        mock_hass.data = {HELVAR_DOMAIN: {mock_config_entry.entry_id: mock_router}}
        
        await async_setup_entry(mock_hass, mock_config_entry, mock_add_entities)
        
        # Verify that no entities were added
        mock_add_entities.assert_called_once_with([])


class TestHelvarLightIntegration:
    """Integration tests for HelvarLight."""

    @pytest.mark.asyncio
    async def test_full_light_lifecycle(self, mock_device, mock_router):
        """Test a complete light lifecycle."""
        # Start with light off
        mock_device.brightness = 0
        light = HelvarLight(mock_device, mock_router)
        
        # Verify initial state
        assert light.is_on is False
        assert light.brightness == 0
        
        # Turn on with brightness
        await light.async_turn_on(**{ATTR_BRIGHTNESS: 150})
        mock_router.api.devices.set_device_brightness.assert_called_with(
            mock_device.address, 150
        )
        
        # Simulate device brightness update
        mock_device.brightness = 150
        assert light.is_on is True
        assert light.brightness == 150
        
        # Turn off
        await light.async_turn_off()
        mock_router.api.devices.set_device_brightness.assert_called_with(
            mock_device.address, 0
        )
        
        # Simulate device brightness update
        mock_device.brightness = 0
        assert light.is_on is False
        assert light.brightness == 0

    def test_light_properties_consistency(self, mock_device, mock_router):
        """Test that light properties are consistent."""
        light = HelvarLight(mock_device, mock_router)
        
        # Test various brightness levels
        test_values = [0, 1, 127, 128, 254, 255]
        
        for brightness in test_values:
            mock_device.brightness = brightness
            assert light.brightness == brightness
            assert light.is_on == (brightness > 0)
            assert light.color_mode == ColorMode.BRIGHTNESS
            assert ColorMode.BRIGHTNESS in light.supported_color_modes