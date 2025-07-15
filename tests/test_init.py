"""Tests for the Helvar integration initialization."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform

from custom_components.helvar import async_setup_entry, async_unload_entry
from custom_components.helvar.const import DOMAIN as HELVAR_DOMAIN


class TestHelvarInit:
    """Test the Helvar integration initialization."""

    @pytest.mark.asyncio
    async def test_async_setup_entry_success(self, mock_hass, mock_config_entry):
        """Test successful setup of config entry."""
        mock_config_entry.data = {
            "host": "192.168.1.100",
            "port": 50000
        }
        
        # Initialize hass.data with the domain
        mock_hass.data = {HELVAR_DOMAIN: {}}
        
        # Mock the aiohelvar.Router to prevent actual network connections
        with patch('custom_components.helvar.router.aiohelvar.Router') as mock_aio_router:
            mock_router_instance = Mock()
            mock_router_instance.connect = AsyncMock()
            mock_router_instance.initialize = AsyncMock()
            mock_aio_router.return_value = mock_router_instance
            
            # async_forward_entry_setups is already mocked in conftest.py
            
            result = await async_setup_entry(mock_hass, mock_config_entry)
            
            assert result is True
            assert HELVAR_DOMAIN in mock_hass.data
            assert mock_config_entry.entry_id in mock_hass.data[HELVAR_DOMAIN]
            
            # Verify the aiohelvar router was created and connected
            mock_aio_router.assert_called_once_with("192.168.1.100", 50000)
            mock_router_instance.connect.assert_called_once()
            mock_router_instance.initialize.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_unload_entry_success(self, mock_hass, mock_config_entry):
        """Test successful unload of config entry."""
        # Setup initial state
        mock_router = Mock()
        mock_hass.data = {
            HELVAR_DOMAIN: {
                mock_config_entry.entry_id: mock_router
            }
        }
        
        # async_forward_entry_unload is already mocked in conftest.py
        
        result = await async_unload_entry(mock_hass, mock_config_entry)
        
        assert result is True
        
        # Verify that the unload was successful (mock_unload function returns True)
        
        # Verify data was cleaned up
        assert mock_config_entry.entry_id not in mock_hass.data[HELVAR_DOMAIN]

    @pytest.mark.asyncio
    async def test_async_setup_entry_router_start_failure(self, mock_hass, mock_config_entry):
        """Test setup failure when router fails to start."""
        mock_config_entry.data = {
            "host": "192.168.1.100",
            "port": 50000
        }
        
        # Initialize hass.data with the domain
        mock_hass.data = {HELVAR_DOMAIN: {}}
        
        # Mock the aiohelvar.Router to simulate connection failure
        with patch('custom_components.helvar.router.aiohelvar.Router') as mock_aio_router:
            mock_router_instance = Mock()
            mock_router_instance.connect = AsyncMock(side_effect=Exception("Connection failed"))
            mock_aio_router.return_value = mock_router_instance
            
            result = await async_setup_entry(mock_hass, mock_config_entry)
            
            assert result is False
            
            # Verify data was cleaned up on failure
            assert mock_hass.data[HELVAR_DOMAIN][mock_config_entry.entry_id] is None