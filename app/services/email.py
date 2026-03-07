from typing import Protocol

import httpx


# Interface
class EmailService(Protocol):
    async def send_activation_code(self, to: str, code: str) -> None: ...

# dev/test service
class ConsoleEmailService:
    async def send_activation_code(self, to: str, code: str) -> None:
        print(f"[EMAIL] Activation code for {to}: {code}")

# prod-like http service
class HTTPEmailService:
    def __init__(self, api_url: str, api_key: str):
        self._api_url = api_url
        self._api_key = api_key

    async def send_activation_code(self, to: str, code: str) -> None:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                self._api_url,
                headers={"Authorization": f"Bearer {self._api_key}"},
                json={
                    "to": to,
                    "subject": "Your activation code",
                    "body": f"Your activation code is: {code}",
                },
            )
            response.raise_for_status()
