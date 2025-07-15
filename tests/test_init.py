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
        
        # Mock the router creation
        with patch('custom_components.helvar.router.HelvarRouter') as mock_router_class:
            mock_router = Mock()
            mock_router.start = AsyncMock()
            mock_router_class.return_value = mock_router
            
            # Mock platform setup
            with patch.object(mock_hass.config_entries, 'async_forward_entry_setups') as mock_forward:
                mock_forward.return_value = True
                
                result = await async_setup_entry(mock_hass, mock_config_entry)
                
                assert result is True
                assert HELVAR_DOMAIN in mock_hass.data
                assert mock_config_entry.entry_id in mock_hass.data[HELVAR_DOMAIN]
                assert mock_hass.data[HELVAR_DOMAIN][mock_config_entry.entry_id] == mock_router
                
                # Verify router was started
                mock_router.start.assert_called_once()
                
                # Verify platforms were set up
                mock_forward.assert_called_once_with(mock_config_entry, [Platform.LIGHT, Platform.SELECT])

    @pytest.mark.asyncio
    async def test_async_unload_entry_success(self, mock_hass, mock_config_entry):
        """Test successful unload of config entry."""
        # Setup initial state
        mock_router = Mock()
        mock_router.stop = AsyncMock()
        mock_hass.data = {
            HELVAR_DOMAIN: {
                mock_config_entry.entry_id: mock_router
            }
        }
        
        with patch.object(mock_hass.config_entries, 'async_unload_platforms') as mock_unload:
            mock_unload.return_value = True
            
            result = await async_unload_entry(mock_hass, mock_config_entry)
            
            assert result is True
            
            # Verify router was stopped
            mock_router.stop.assert_called_once()
            
            # Verify platforms were unloaded
            mock_unload.assert_called_once_with(mock_config_entry, [Platform.LIGHT, Platform.SELECT])
            
            # Verify data was cleaned up
            assert mock_config_entry.entry_id not in mock_hass.data[HELVAR_DOMAIN]

    @pytest.mark.asyncio
    async def test_async_setup_entry_router_start_failure(self, mock_hass, mock_config_entry):
        """Test setup failure when router fails to start."""
        mock_config_entry.data = {
            "host": "192.168.1.100",
            "port": 50000
        }
        
        with patch('custom_components.helvar.router.HelvarRouter') as mock_router_class:
            mock_router = Mock()
            mock_router.start = AsyncMock(side_effect=Exception("Connection failed"))
            mock_router_class.return_value = mock_router
            
            result = await async_setup_entry(mock_hass, mock_config_entry)
            
            assert result is False
            
            # Verify data was not stored on failure
            if HELVAR_DOMAIN in mock_hass.data:
                assert mock_config_entry.entry_id not in mock_hass.data[HELVAR_DOMAIN]