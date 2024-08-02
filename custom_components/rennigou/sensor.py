from __future__ import annotations


from homeassistant.components.sensor import (
    SensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ATTRIBUTION
from .coodinator import RennigouCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: RennigouCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([RennigouCurrencySensor(coordinator)])


class RennigouSensor(CoordinatorEntity[RennigouCoordinator], SensorEntity):
    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(self, coordinator: RennigouCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.client.uid)},
            entry_type=DeviceEntryType.SERVICE,
            name="任你购",
        )


class RennigouCurrencySensor(RennigouSensor):
    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def name(self):
        return "currency rate"

    @property
    def state(self):
        return self.coordinator.data.currency_rate

    @property
    def unique_id(self):
        return f"{DOMAIN}_currency_sensor"

    @property
    def device_state_attributes(self):
        return {}

    async def async_update(self):
        await self._coordinator.async_request_refresh()


# class RennigouPackagesSensor(Entity):
#     def __init__(self, coordinator):
#         self._coordinator = coordinator

#     @property
#     def name(self):
#         return self._coordinator.name

#     @property
#     def state(self):
#         return len(self._coordinator.data)  # State cannot be a large object, so using length

#     @property
#     def unique_id(self):
#         return f"{DOMAIN}_packages_sensor"

#     @property
#     def device_state_attributes(self):
#         return {"packages": self._coordinator.data}

#     async def async_update(self):
#         await self._coordinator.async_request_refresh()
