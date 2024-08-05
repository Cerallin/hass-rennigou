import logging
from datetime import timedelta

LOGGER = logging.getLogger(__package__)
DEFAULT_SCAN_INTERVAL = timedelta(hours=1)
REFRESH_TOKEN_INTERVAL = timedelta(hours=12)

DOMAIN = "rennigou"

ATTRIBUTION = "第三方任你购 hass 集成"

# 全部未完成订单
ATTR_UNCOMPLETED_ORDERS = "uncompleted_orders"
# 采购中
ATTR_AWAITING_PURCHASE = "awaiting_purchase"
# 待入库
ATTR_AWAITING_STORAGE = "awaiting_storage"
# 待发货
ATTR_AWAITING_SHIPMENT = "awaiting_shipment"
# 待收货
ATTR_AWAITING_DELIVERY = "awaiting_delivery"
# 已完成
ATTR_COMPLETED = "completed"

PACKAGE_TYPE_OWNER = "自发包裹"
PACKAGE_TYPE_POOL = "参团包裹"

API_HOST = "https://rl.rngmoe.com"
REFER_HOST = "https://www.030buy.net/"
