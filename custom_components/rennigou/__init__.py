import logging
import asyncio
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    Platform,
)

from .const import DOMAIN, REFRESH_TOKEN_INTERVAL
from .rennigou import RennigouClient, RennigouLoginFail
from .coodinator import RennigouCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup(hass: HomeAssistant, config: ConfigType):
    """Set up the Rennigou component."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    _LOGGER.warning("Ciallo Rennigou")

    # Login first
    try:
        client = RennigouClient(entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD])
        await client.login()
    except RennigouLoginFail as err:
        raise ConfigEntryNotReady(err) from err

    # TODO How to register packages?

    rennigou_coordinator = RennigouCoordinator(hass, client)

    # re-login every REFRESH_TOKEN_INTERVAL
    async def refgresh_rennigou_token(coordinator: RennigouCoordinator):
        _LOGGER.info("Refreshed rennigou auth token")
        await coordinator.client.login()
        await asyncio.sleep(REFRESH_TOKEN_INTERVAL.total_seconds())

    hass.loop.create_task(refgresh_rennigou_token(rennigou_coordinator))

    await rennigou_coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = rennigou_coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True
