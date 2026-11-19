import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()

PROVIDERS = ("meta", "evolution")
PROMPT_PADRAO = "Você é um assistente simpático e objetivo. Responda em português do Brasil."


def _env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _env_int(name: str, default: int) -> int:
    raw = _env(name)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        raise RuntimeError(f"{name} precisa ser um número inteiro (valor atual: {raw!r})")


@dataclass(frozen=True)
class Settings:
    provider: str
    port: int
    log_level: str
    groq_api_key: str
    groq_model: str
    system_prompt: str
    max_history_messages: int
    meta_token: str
    phone_number_id: str
    verify_token: str
    meta_app_secret: str
    graph_version: str
    evolution_url: str
    evolution_api_key: str
    instance_name: str

    def validate(self) -> None:
        if self.provider not in PROVIDERS:
            raise RuntimeError(f"PROVIDER inválido: {self.provider!r}. Use meta ou evolution")

        required = {"GROQ_API_KEY": self.groq_api_key, "VERIFY_TOKEN": self.verify_token}
        if self.provider == "meta":
            required["META_PERMANENT_TOKEN"] = self.meta_token
            required["PHONE_NUMBER_ID"] = self.phone_number_id
        else:
            required["EVOLUTION_URL"] = self.evolution_url
            required["EVOLUTION_API_KEY"] = self.evolution_api_key
            required["INSTANCE_NAME"] = self.instance_name

        missing = [name for name, value in required.items() if not value]
        if missing:
            raise RuntimeError("Faltam variáveis no .env: " + ", ".join(missing))


@lru_cache
def get_settings() -> Settings:
    return Settings(
        provider=_env("PROVIDER", "meta").lower(),
        port=_env_int("PORT", 5000),
        log_level=_env("LOG_LEVEL", "INFO").upper(),
        groq_api_key=_env("GROQ_API_KEY"),
        groq_model=_env("GROQ_MODEL", "llama-3.1-8b-instant"),
        system_prompt=_env("SYSTEM_PROMPT", PROMPT_PADRAO),
        max_history_messages=_env_int("MAX_HISTORY_MESSAGES", 10),
        meta_token=_env("META_PERMANENT_TOKEN"),
        phone_number_id=_env("PHONE_NUMBER_ID"),
        verify_token=_env("VERIFY_TOKEN"),
        meta_app_secret=_env("META_APP_SECRET"),
        graph_version=_env("GRAPH_API_VERSION", "v23.0"),
        evolution_url=_env("EVOLUTION_URL", "http://localhost:8080").rstrip("/"),
        evolution_api_key=_env("EVOLUTION_API_KEY"),
        instance_name=_env("INSTANCE_NAME"),
    )
