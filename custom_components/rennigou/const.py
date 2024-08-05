import logging
from datetime import timedelta

LOGGER = logging.getLogger(__package__)
DEFAULT_SCAN_INTERVAL = timedelta(hours=1)
REFRESH_TOKEN_INTERVAL = timedelta(hours=12)

DOMAIN = "rennigou"

ATTRIBUTION = "第三方任你购 hass 集成"

ATTR_AWAITING_PURCHASE = "awaiting_purchase"
ATTR_AWAITING_STORAGE = "awaiting_storage"
ATTR_AWAITING_SHIPMENT = "awaiting_shipment"
ATTR_AWAITING_DELIVERY = "awaiting_delivery"
ATTR_COMPLETED = "completed"

API_HOST = "https://rl.rngmoe.com"
REFER_HOST = "https://www.030buy.net/"
