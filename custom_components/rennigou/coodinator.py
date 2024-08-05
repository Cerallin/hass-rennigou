"""Coordinator for Rennigou."""

import asyncio
from dataclasses import dataclass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    LOGGER,
    DEFAULT_SCAN_INTERVAL,
    ATTR_AWAITING_PURCHASE,
    ATTR_AWAITING_STORAGE,
    ATTR_AWAITING_SHIPMENT,
    ATTR_AWAITING_DELIVERY,
    ATTR_COMPLETED,
)
from .rennigou import RennigouClient, RennigouOrder


@dataclass
class RennigouData:
    """Class for handling the data retrieval."""

    currency_rate: float
    orders: dict[str, list[RennigouOrder]]


class RennigouCoordinator(DataUpdateCoordinator[RennigouData]):
    """Class to manage fetching Rennigou data."""

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
        """Fetch data from Rennigou API."""

        try:
            currency_rate = await self.client.get_currency_rate()
            packages_lists = await asyncio.gather(
                self.client.get_awaiting_purchase_orders(),
                self.client.get_awaiting_storage_orders(),
                self.client.get_awaiting_shipment_orders(),
                self.client.get_awaiting_delivery_orders(),
                self.client.get_completed_orders(),
            )
        except Exception as err:
            raise UpdateFailed(err) from err

        packages_keys = [
            ATTR_AWAITING_PURCHASE,
            ATTR_AWAITING_STORAGE,
            ATTR_AWAITING_SHIPMENT,
            ATTR_AWAITING_DELIVERY,
            ATTR_COMPLETED,
        ]

        return RennigouData(
            currency_rate=currency_rate,
            orders=dict(zip(packages_keys, packages_lists)),
        )
