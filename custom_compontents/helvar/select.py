"""Support for Helvar Groups and Scenes."""
import logging

import aiohelvar

# Import the device class from the component that you want to support
from homeassistant.components.select import SelectEntity

from .const import (  # DEFAULT_OFF_GROUP_BLOCK,; DEFAULT_OFF_GROUP_SCENE,; DEFAULT_ON_GROUP_BLOCK,; DEFAULT_ON_GROUP_SCENE,; VALID_OFF_GROUP_SCENES,
    DOMAIN as HELVAR_DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def asynnc_setup_platform(hass, config, add_entities, discovery_info=None):
    """Not currently used."""


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Helvar groups from a config entry."""

    router = hass.data[HELVAR_DOMAIN][config_entry.entry_id]

    groups = [HelvarGroup(group, router) for group in router.api.groups.groups.values()]

    _LOGGER.info("Adding %s groups", len(groups))

    async_add_entities(groups)


class HelvarGroup(SelectEntity):
    """Representation of a Helvar Light."""

    def __init__(self, group: aiohelvar.groups.Group, router):
        """Initialize an HelvarLight."""
        self.router = router
        self.group = group
        self._attr_current_option = None
        self.register_subscription()

    @property
    def current_option(self):
        """Get current selected option."""
        current_scene_address = self.group.get_last_scene_address()
        current_scene = self.router.api.scenes.get_scene(current_scene_address)

        return _render_scene_name(current_scene)

    @property
    def unique_id(self):
        """Get unique id."""
        return f"{self.group.group_id}-select"

    @property
    def options(self):
        """Get the options."""
        scenes = self.router.api.groups.get_scenes_for_group(
            self.group.group_id, only_named=False
        )

        return [_render_scene_name(scene) for scene in scenes]

    def register_subscription(self):
        """Register subscription."""

        async def async_router_callback_group(group_id):
            _LOGGER.info("Group %s update callback has been received", group_id)
            self.async_write_ha_state()

        result = self.router.api.groups.register_subscription(
            self.group.group_id, async_router_callback_group
        )

        if result is not True:
            _LOGGER.error(
                "Could not register for a callback for group %s", self.group.group_id
            )

    @property
    def name(self):
        """Return the display name of this group."""
        return f"Group: {self.group.name}"

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""

        # translate UI string back to address. (Hass should really be using key:value pairs...)
        scene_address = _scene_string_to_address(option)

        # call scene change for group
        await self.router.api.groups.set_scene(scene_address)

    # async def async_update(self):
    #     """Fetch new state data for this light.

    #     This is the only method that should fetch new data for Home Assistant.
    #     """
    #     # the underlying objects are automatically updated, and all properties read directly from
    #     # those objects. Nothing to do here.
    #     return True


def _render_scene_name(scene):
    """Render scene name for hass."""
    if scene is None:
        return None
    if scene.name:
        return f"{scene.name} - {scene.address}"
    return f"Unnamed - {scene.address}"


def _scene_string_to_address(scene_string):
    """Convert hass name for scene to a SceneAddress."""

    scene_address = scene_string.rsplit(" - ", maxsplit=1)[1].strip(" ")
    return aiohelvar.SceneAddress.fromString(scene_address)
