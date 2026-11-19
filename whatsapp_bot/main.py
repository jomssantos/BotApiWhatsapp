import hmac
import json
import logging
from contextlib import asynccontextmanager
from dataclasses import dataclass

import httpx
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse

from .config import Settings, get_settings
from .history import ConversationHistory, RecentIds
from .llm import GroqChat
from .parsing import IncomingMessage, mask_number, parse_payload
from .security import signature_is_valid
from .senders import EvolutionSender, MetaSender, Sender

log = logging.getLogger("whatsapp_bot")

UNSUPPORTED_REPLY = "Por enquanto eu só entendo texto. Pode escrever o que precisa?"
FALLBACK_REPLY = "Tive um problema para responder agora. Tenta de novo em instantes?"


@dataclass
class Services:
    settings: Settings
    sender: Sender
    llm: GroqChat
    history: ConversationHistory
    recent_ids: RecentIds


def build_services(settings: Settings, client: httpx.AsyncClient) -> Services:
    if settings.provider == "meta":
        sender: Sender = MetaSender(client, settings.meta_token, settings.phone_number_id, settings.graph_version)
    else:
        sender = EvolutionSender(client, settings.evolution_url, settings.evolution_api_key, settings.instance_name)

    return Services(
        settings=settings,
        sender=sender,
        llm=GroqChat(client, settings.groq_api_key, settings.groq_model),
        history=ConversationHistory(settings.system_prompt, settings.max_history_messages),
        recent_ids=RecentIds(),
    )


async def handle_message(services: Services, message: IncomingMessage) -> None:
    who = mask_number(message.sender)

    if message.text is None:
        log.info("tipo %r de %s não tratado", message.kind, who)
        reply = UNSUPPORTED_REPLY
    else:
        try:
            prompt = services.history.build_prompt(message.sender, message.text)
            reply = await services.llm.reply(prompt)
            services.history.remember(message.sender, message.text, reply)
        except (httpx.HTTPError, KeyError, IndexError) as exc:
            log.error("erro ao gerar resposta para %s: %s", who, exc)
            reply = FALLBACK_REPLY

    try:
        await services.sender.send_text(message.sender, reply)
    except httpx.HTTPError as exc:
        log.error("erro ao enviar para %s: %s", who, exc)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        settings.validate()
        async with httpx.AsyncClient(timeout=30) as client:
            app.state.services = build_services(settings, client)
            log.info("bot iniciado no modo %r", settings.provider)
            yield

    app = FastAPI(title="Bot de WhatsApp com IA", lifespan=lifespan)

    @app.get("/")
    async def health():
        return {"status": "ok", "provider": settings.provider}

    @app.get("/webhook")
    async def verify_webhook(request: Request):
        # a Meta chama uma vez ao cadastrar o webhook
        params = request.query_params
        token = params.get("hub.verify_token") or ""
        if params.get("hub.mode") == "subscribe" and hmac.compare_digest(token, settings.verify_token):
            return PlainTextResponse(params.get("hub.challenge") or "")
        raise HTTPException(status_code=403, detail="Forbidden")

    @app.post("/webhook")
    async def receive_webhook(request: Request, background: BackgroundTasks):
        body = await request.body()

        if settings.provider == "meta":
            signature = request.headers.get("X-Hub-Signature-256")
            if not signature_is_valid(settings.meta_app_secret, body, signature):
                raise HTTPException(status_code=403, detail="Assinatura inválida")

        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            return JSONResponse({"received": True})

        log.debug("payload: %s", json.dumps(payload, ensure_ascii=False))

        services: Services = request.app.state.services
        for message in parse_payload(payload):
            if services.recent_ids.seen_before(message.message_id):
                continue
            # responde 200 já, processa depois
            background.add_task(handle_message, services, message)

        return JSONResponse({"received": True})

    return app


app = create_app()
