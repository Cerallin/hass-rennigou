import aiohttp
import time
import jwt
from json import JSONDecodeError
from datetime import datetime
from dateutil.relativedelta import relativedelta

from .const import API_HOST, REFER_HOST


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
        super().__init__(f"Response of {method} URL {url} " "returned empty response.")


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
            payload, key="OYZJEYvhNbwYG3WOecDzw8Mq8SixjD23", algorithm="HS256"
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

    async def get_packages(self) -> list[dict]:
        data = await self._send_api_request(
            "GET",
            "/order/order/getAllLists",
            params={
                "page": "1",
                "page_last_id": "0",
                "service": "all_query",
                "is_show_page": "1",
            },
        )

        six_months_ago = datetime.today() - relativedelta(months=+6)

        packages = [
            {
                "show_time": (header := package["header"])["show_time"],
                "status_name": header["status_name"],
                "update_time": (body := package["body"][0])["update_time"],
                "product_main_img": body["product_main_img"],
                "product_title": body["product_title"],
                "source_site_name": body["source_site_name"],
            }
            for package in data["result"]
            if datetime.fromtimestamp(package["header"]["show_time"]) >= six_months_ago
        ]

        return packages
