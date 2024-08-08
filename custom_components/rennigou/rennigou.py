import aiohttp
import asyncio
import time
import jwt
from dataclasses import dataclass
from json import JSONDecodeError
from datetime import datetime
from dateutil.relativedelta import relativedelta

from .const import (
    API_HOST,
    REFER_HOST,
    PACKAGE_TYPE_OWNER,
    PACKAGE_TYPE_POOL,
)


@dataclass
class RennigouOrder:
    id: int
    timestamp: datetime
    updated_at: datetime
    status: str
    image_link: str
    title: str
    source_site: str
    weight: int  # 只有待发货订单有这个字段

    type: str  # 自发包裹/参团包裹，仅对待收货/已完成的订单有效

    def __init__(self, order_data: dict) -> None:
        header: dict = order_data["header"]
        body: dict = order_data["body"][0]

        self.id = order_data.get("id", 0)

        self.timestamp = datetime.fromtimestamp(header["show_time"])
        self.updated_at = datetime.fromtimestamp(body["update_time"])
        self.status = header["status_name"]

        self.image_link = body["product_main_img"]
        self.title = body["product_title"]

        self.source_site = body["source_site_name"]

        self.weight = body.get("weight", 0)

        self.type = "无"

    def assign_type(self, type: str):
        self.type = type

        return self


class RennigouLoginFail(RuntimeError):
    def __init__(self) -> None:
        super().__init__(
            "Login to rennigou failed. Please check your username and password."
        )


class RennigouHTTPError(RuntimeError):
    def __init__(self, url: str, code: int) -> None:
        super().__init__(f"Response of URL {url} returns {code}.")


class RennigouEmptyResponse(RuntimeError):
    def __init__(self, method: str, url: str) -> None:
        super().__init__(f"Response of {method} URL {url} returned empty response.")


class RennigouAPIRequestError(RuntimeError):
    def __init__(self, code: int, message: str) -> None:
        super().__init__(f"code: {code}, message: {message}")


class RennigouClient:
    def __init__(self, username: str, password: str):
        self.uid = None
        self.username = username
        self.password = password
        self.token = None

    async def _send_request(
        self, method: str, url: str, params=None, data=None
    ) -> aiohttp.ClientResponse:
        headers = {
            "Referer": REFER_HOST,
            "Authorization": f"Bearer {self._generate_jwt_token()}",
        }

        if self.token is not None:
            headers["Token"] = f"{self.token}"
            headers["Uid"] = f"{self.uid}"

        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, url, headers=headers, params=params, data=data
            ) as response:
                # Check if status code == 200
                if status_code := response.status != 200:
                    raise RennigouHTTPError(url, status_code)

                return response

    async def _send_api_request(
        self, method: str, endpoint: str, params=None, data=None
    ) -> dict:
        url = f"{API_HOST}{endpoint}"
        headers = {
            "Referer": REFER_HOST,
            "Authorization": f"Bearer {self._generate_jwt_token()}",
        }

        if self.token is not None:
            headers["Token"] = f"{self.token}"
            headers["Uid"] = f"{self.uid}"

        async with aiohttp.ClientSession() as session:
            async with session.request(
                method, url, headers=headers, params=params, data=data
            ) as response:
                # Check if status code == 200
                if status_code := response.status != 200:
                    raise RennigouHTTPError(url, status_code)

                # Check if response is empty
                try:
                    data = await response.json()
                except JSONDecodeError:
                    raise RennigouEmptyResponse(method, url)

                # Check if data code == 0
                if code := data["code"] != 0:
                    raise RennigouAPIRequestError(code, data["msg"])

                return data["data"]

    def _generate_jwt_token(self) -> str:
        payload = {
            "iss": "FQwcwtrHtmdxQ0aCKlQoxNMy9glEr4Zd",
            "iat": int(time.time()),
            "exp": int(time.time()) + 6000,
        }

        token = jwt.encode(
            payload,
            key="OYZJEYvhNbwYG3WOecDzw8Mq8SixjD23",
            algorithm="HS256",
        )

        return token

    async def login(self) -> None:
        try:
            response = await self._send_api_request(
                "POST",
                "/user/index/login",
                data={
                    "type": 3,  # 也许是网页登录的意思
                    "mail": self.username,
                    "pass": self.password,
                },
            )
            self.token = response["token"]
            self.uid = response["userInfo"]["user_id"]
        except RennigouEmptyResponse:
            raise RennigouLoginFail
        except RennigouAPIRequestError:
            raise RennigouLoginFail

    async def get_currency_rate(self) -> float:
        data = await self._send_api_request("GET", "/supplier/index/getCommonInfo")
        return data["exchange"]

    async def _get_orders(
        self,
        service: str,
        page: int = 1,
        is_show_page: bool = True,
    ) -> list[RennigouOrder]:
        response = await self._send_api_request(
            "GET",
            "/order/order/getLists",
            params={
                "page": f"{page}",
                "page_last_id": "0",
                "service": service,
                "is_show_page": "1" if is_show_page else "0",
            },
        )

        # 有的接口返回null而不是空数组
        order_list = res if (res := response["result"]) else []

        # 用于去重
        orders = {}
        for order_data in order_list:
            orders[order_data["id"]] = RennigouOrder(order_data)
        # 忽略时间截断之前的包裹
        ignore_before = datetime.today() + relativedelta(months=-6)
        return [order for order in orders.values() if order.timestamp >= ignore_before]

    async def get_awaiting_purchase_orders(self) -> list[RennigouOrder]:
        return await self._get_orders("unpaid_purchase")

    async def get_awaiting_storage_orders(self) -> list[RennigouOrder]:
        """待入库订单"""
        return await self._get_orders("unPutIn")

    async def get_awaiting_shipment_orders(self) -> list[RennigouOrder]:
        """待发货订单"""
        return await self._get_orders("unDelivery_unDelivery")

    async def _get_2_type_orders(self, service: str) -> list[RennigouOrder]:
        """待收货订单"""
        orders: list[list[RennigouOrder]] = await asyncio.gather(
            self._get_orders(f"{service}_ownerPackage"),
            self._get_orders(f"{service}_poolPackage"),
        )

        for order in orders[0]:
            order.assign_type(PACKAGE_TYPE_OWNER)
        for order in orders[1]:
            order.assign_type(PACKAGE_TYPE_POOL)

        orders_togather = [*orders[0], *orders[1]]
        # 时间倒序
        orders_togather.sort(key=lambda d: d.timestamp, reverse=True)

        return orders_togather

    async def get_awaiting_delivery_orders(self) -> list[RennigouOrder]:
        """待收货订单"""
        orders = await self._get_2_type_orders("unTakeDelivery")
        # TODO 查询快递单号
        return orders

    async def get_completed_orders(self) -> list[RennigouOrder]:
        """已完成订单"""
        return await self._get_2_type_orders("finish")
