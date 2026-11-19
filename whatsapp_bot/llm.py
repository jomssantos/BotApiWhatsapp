import httpx

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


class GroqChat:
    def __init__(self, client: httpx.AsyncClient, api_key: str, model: str, temperature: float = 0.7) -> None:
        self._client = client
        self._api_key = api_key
        self._model = model
        self._temperature = temperature

    async def reply(self, messages: list[dict]) -> str:
        response = await self._client.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {self._api_key}"},
            json={"model": self._model, "messages": messages, "temperature": self._temperature},
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
