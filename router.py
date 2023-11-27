"""Helvar Router."""
import logging

import aiohelvar

from homeassistant.exceptions import ConfigEntryNotReady

from .const import CONF_HOST, CONF_PORT

_LOGGER = logging.getLogger(__name__)


class HelvarRouter:
    """Manages a Helvar Router."""

    def __init__(self, hass, config_entry):
        """Initialize the system."""
        self.config_entry = config_entry
        self.hass = hass
        self.available = True
        self.api = None

    @property
    def host(self):
        """Return the host of this router."""
        return self.config_entry.data[CONF_HOST]

    @property
    def port(self):
        """Return the host of this router."""
        return self.config_entry.data[CONF_PORT]

    async def async_setup(self, tries=0):
        """Set up a helval router based on host paramete50000r."""
        host = self.host
        port = self.port
        hass = self.hass

        router = aiohelvar.Router(host, port)

        try:
            await router.connect()
            await router.initialize()

        except ConnectionError as err:
            _LOGGER.error("Error connecting to the Helvar router at %s", host)
            raise ConfigEntryNotReady from err

        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unknown error connecting with Helvar router at %s", host)
            return False

        self.api = router
        # self.sensor_manager = SensorManager(self)

        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(self.config_entry, "light"),
        )
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(self.config_entry, "select"),
        )

        return True
