import logging
from datetime import timedelta

LOGGER = logging.getLogger(__package__)
DEFAULT_SCAN_INTERVAL = timedelta(hours=1)

DOMAIN = "rennigou"

ATTRIBUTION = "第三方任你购 hass 集成"

API_HOST = "https://rl.rngmoe.com"
REFER_HOST = "https://www.030buy.net/"
