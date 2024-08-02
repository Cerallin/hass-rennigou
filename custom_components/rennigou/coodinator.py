"""Coordinator for 17Track."""

from dataclasses import dataclass

from .rennigou import RennigouClient

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    LOGGER,
    DEFAULT_SCAN_INTERVAL,
)


@dataclass
class RennigouData:
    """Class for handling the data retrieval."""

    currency_rate: float
    packages: list[dict]


class RennigouCoordinator(DataUpdateCoordinator[RennigouData]):
    """Class to manage fetching 17Track data."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, client: RennigouClient) -> None:
        """Initialize."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )

        self.client = client

    async def update_token(self):
        pass

    async def _async_update_data(self) -> RennigouData:
        """Fetch data from 17Track API."""

        try:
            currency_rate = await self.client.get_currency_rate()
            packages = await self.client.get_packages()
        except Exception as err:
            raise UpdateFailed(err) from err

        return RennigouData(
            currency_rate=currency_rate,
            packages=packages,
        )
