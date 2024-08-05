from __future__ import annotations


from homeassistant.components.sensor import (
    SensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    ATTRIBUTION,
    ATTR_UNCOMPLETED_ORDERS,
    ATTR_AWAITING_PURCHASE,
    ATTR_AWAITING_STORAGE,
    ATTR_AWAITING_SHIPMENT,
    ATTR_AWAITING_DELIVERY,
    ATTR_COMPLETED,
)
from .coodinator import RennigouCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: RennigouCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        [
            RennigouCurrencySensor(coordinator),
            RennigouUncompletedOrdersSensor(coordinator, ATTR_UNCOMPLETED_ORDERS),
            RennigouOrdersSensor(coordinator, ATTR_AWAITING_PURCHASE),
            RennigouOrdersSensor(coordinator, ATTR_AWAITING_STORAGE),
            RennigouOrdersSensor(coordinator, ATTR_AWAITING_SHIPMENT),
            RennigouOrdersSensor(coordinator, ATTR_AWAITING_DELIVERY),
            RennigouOrdersSensor(coordinator, ATTR_COMPLETED),
        ]
    )


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
        await self.coordinator.async_request_refresh()


class RennigouOrdersSensor(RennigouSensor):
    def __init__(self, coordinator: RennigouCoordinator, attr_name: str):
        super().__init__(coordinator)

        self._name = attr_name.replace("_", " ")
        self._entry_name = attr_name

    @property
    def _orders(self):
        return self.coordinator.data.orders[self._entry_name]

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return len(self._orders)

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self.name.replace(" ", "_")}"

    @property
    def extra_state_attributes(self):
        return {"orders": self._orders}

    async def async_update(self):
        await self.coordinator.async_request_refresh()


class RennigouUncompletedOrdersSensor(RennigouOrdersSensor):
    def __init__(self, coordinator: RennigouCoordinator, attr_name: str):
        super().__init__(coordinator, attr_name)

    @property
    def _orders(self):
        data = self.coordinator.data.orders

        orders = []
        orders += data[ATTR_AWAITING_PURCHASE]
        orders += data[ATTR_AWAITING_STORAGE]
        orders += data[ATTR_AWAITING_SHIPMENT]
        orders += data[ATTR_AWAITING_DELIVERY]

        return orders
