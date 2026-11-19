import logging
from typing import Protocol

import httpx

log = logging.getLogger("whatsapp_bot.senders")

MAX_TEXT_LENGTH = 4000  # limite do WhatsApp é 4096


class Sender(Protocol):
    async def send_text(self, to: str, text: str) -> None: ...


def split_text(text: str, limit: int = MAX_TEXT_LENGTH) -> list[str]:
    text = text.strip()
    if len(text) <= limit:
        return [text] if text else []

    parts = []
    while len(text) > limit:
        # corta em quebra de linha, depois espaço
        cut = text.rfind("\n", 0, limit)
        if cut < limit // 2:
            cut = text.rfind(" ", 0, limit)
        if cut < limit // 2:
            cut = limit
        parts.append(text[:cut].strip())
        text = text[cut:].strip()
    if text:
        parts.append(text)
    return parts


def _check(response: httpx.Response, origin: str) -> None:
    if response.is_error:
        log.error("%s respondeu %s: %s", origin, response.status_code, response.text[:500])
    response.raise_for_status()


class MetaSender:
    def __init__(self, client: httpx.AsyncClient, token: str, phone_number_id: str, graph_version: str) -> None:
        self._client = client
        self._headers = {"Authorization": f"Bearer {token}"}
        self._url = f"https://graph.facebook.com/{graph_version}/{phone_number_id}/messages"

    async def send_text(self, to: str, text: str) -> None:
        for part in split_text(text):
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to,
                "type": "text",
                "text": {"preview_url": False, "body": part},
            }
            _check(await self._client.post(self._url, headers=self._headers, json=payload), "Meta")


class EvolutionSender:
    def __init__(self, client: httpx.AsyncClient, base_url: str, api_key: str, instance_name: str) -> None:
        self._client = client
        self._headers = {"apikey": api_key}
        self._url = f"{base_url}/message/sendText/{instance_name}"

    async def send_text(self, to: str, text: str) -> None:
        for part in split_text(text):
            response = await self._client.post(self._url, headers=self._headers, json={"number": to, "text": part})
            _check(response, "Evolution")
