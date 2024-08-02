import asyncio
import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD

from .rennigou import RennigouClient

_LOGGER = logging.getLogger(__name__)

DOMAIN = "rennigou_sensor"

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    """Set up the Rennigou sensors."""

    # Get username and password from configuration
    username = config[CONF_USERNAME]
    password = config[CONF_PASSWORD]

    # Initialize Rennigou client
    client = RennigouClient()

    # Login to Rennigou
    await client.login(username, password)

    # Define the currency rate sensor
    hass.states.async_set(
        f"{DOMAIN}.rennigou_currency_rate",
        0.0,  # Initial value
        {
            "friendly_name": "Rennigou Currency Rate",
            "icon": "mdi:currency-usd",
        },
    )

    # Define the packages sensor
    hass.states.async_set(
        f"{DOMAIN}.rennigou_packages",
        [],  # Initial value is an empty list
        {
            "friendly_name": "Rennigou Packages",
            "icon": "mdi:package",
        },
    )

    # Schedule update tasks
    hass.loop.create_task(update_currency_rate(hass, client))
    hass.loop.create_task(update_packages(hass, client))

    return True


async def update_currency_rate(hass, client):
    """Update currency rate sensor."""
    while True:
        currency_rate = await client.get_currency_rate()
        hass.states.async_set(
            f"{DOMAIN}.rennigou_currency_rate",
            currency_rate,
            {
                "friendly_name": "Rennigou Currency Rate",
                "icon": "mdi:currency-usd",
            },
        )
        await asyncio.sleep(3600)  # Update every hour


async def update_packages(hass, client):
    """Update packages sensor."""
    while True:
        packages = await client.get_packages()
        hass.states.async_set(
            f"{DOMAIN}.rennigou_packages",
            packages,
            {
                "friendly_name": "Rennigou Packages",
                "icon": "mdi:package",
            },
        )
        await asyncio.sleep(86400)  # Update every day
