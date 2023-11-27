"""Support for Helvar light devices."""
import logging

import aiohelvar

# Import the device class from the component that you want to support
from homeassistant.components.light import (  # COLOR_MODE_ONOFF,
    ATTR_BRIGHTNESS,
    COLOR_MODE_BRIGHTNESS,
    SUPPORT_BRIGHTNESS,
    LightEntity,
)

from .const import (  # DEFAULT_OFF_GROUP_BLOCK,; DEFAULT_OFF_GROUP_SCENE,; DEFAULT_ON_GROUP_BLOCK,; DEFAULT_ON_GROUP_SCENE,; VALID_OFF_GROUP_SCENES,
    DOMAIN as HELVAR_DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def asynnc_setup_platform(hass, config, add_entities, discovery_info=None):
    """Not currently used."""


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Helvar lights from a config entry."""

    router = hass.data[HELVAR_DOMAIN][config_entry.entry_id]

    # Add devices
    # async_add_entities(
    #     # Add groups
    #     HelvarLight(group, None, router)
    #     for group in router.api.groups.groups.values()
    # )

    devices = [
        HelvarLight(device, router) for device in router.api.devices.get_light_devices()
    ]

    _LOGGER.info("Adding %s helvar devices", len(devices))

    async_add_entities(devices)


class HelvarLight(LightEntity):
    """Representation of a Helvar Light."""

    def __init__(self, device: aiohelvar.devices.Device, router):
        """Initialize an HelvarLight."""
        self.router = router
        self.device = device

        self.register_subscription()

    def register_subscription(self):
        """Register subscription."""

        async def async_router_callback_device(device):

            _LOGGER.debug("Received status update for %s", device)

            self.async_write_ha_state()

        self.router.api.devices.register_subscription(
            self.device.address, async_router_callback_device
        )

    @property
    def unique_id(self):
        """
        Return the unique ID of this Helvar light.

        This isn't truly unique as we do not get a serial number or MAC address from the Helvar APIs.

        We use the device's bus network address which is at least guaranteed to be unique at any point in time.

        """
        return f"{self.device.address}-light"

    @property
    def name(self):
        """Return the display name of this light."""
        return self.device.name

    @property
    def brightness(self):
        """Return the brightness of the light.

        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """

        return self.device.brightness

    @property
    def is_on(self):
        """Return true if light is on."""

        if self.brightness > 0:
            return True
        return False

    @property
    def supported_color_modes(self):
        """Colour modes."""

        return [COLOR_MODE_BRIGHTNESS]

    @property
    def supported_features(self) -> int:
        """Supported Features."""
        return SUPPORT_BRIGHTNESS

    async def async_turn_on(self, **kwargs):
        """We'll just select scene 1 for a group, for now."""

        brightness = kwargs.get(ATTR_BRIGHTNESS, 255)

        # if self.is_group:
        #     await self._router.api.groups.set_scene(
        #         aiohelvar.parser.address.SceneAddress(
        #             self._group.group_id, DEFAULT_ON_GROUP_BLOCK, DEFAULT_ON_GROUP_SCENE
        #         )
        #     )
        # else:
        # For now, set the device level directly. But we may want to set the device scene as we do with
        # groups.

        await self.router.api.devices.set_device_brightness(
            self.device.address, brightness
        )

    async def async_turn_off(self, **kwargs):
        """Instruct the light to turn off."""

        # if self.is_group:
        #     await self._router.api.groups.set_scene(
        #         aiohelvar.parser.address.SceneAddress(
        #             self._group.group_id,
        #             DEFAULT_OFF_GROUP_BLOCK,
        #             DEFAULT_OFF_GROUP_SCENE,
        #         )
        #     )
        # else:
        # For now, set the device level directly. But we may want to set the device scene as we do with
        # groups.
        await self.router.api.devices.set_device_brightness(self.device.address, 0)

    # async def async_update(self):
    #     """Fetch new state data for this light.

    #     This is the only method that should fetch new data for Home Assistant.
    #     """
    #     # the underlying objects are automatically updated, and all properties read directly from
    #     # those objects.
    #     return True
