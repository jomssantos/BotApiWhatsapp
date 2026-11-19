from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class IncomingMessage:
    sender: str  # só dígitos
    message_id: str | None
    kind: str  # text, image, audio...
    text: str | None


def parse_payload(payload: dict[str, Any]) -> list[IncomingMessage]:
    if "entry" in payload:
        return parse_meta(payload)
    if "event" in payload:
        return parse_evolution(payload)
    return []


def parse_meta(payload: dict[str, Any]) -> list[IncomingMessage]:
    found = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            for msg in change.get("value", {}).get("messages", []):
                sender = msg.get("from")
                if not sender:
                    continue
                kind = msg.get("type", "unknown")
                text = msg.get("text", {}).get("body") if kind == "text" else None
                found.append(IncomingMessage(sender, msg.get("id"), kind, text))
    return found


def parse_evolution(payload: dict[str, Any]) -> list[IncomingMessage]:
    if str(payload.get("event", "")).lower().replace("_", ".") != "messages.upsert":
        return []

    data = payload.get("data")
    items = data if isinstance(data, list) else [data]
    found = []

    for item in items:
        if not isinstance(item, dict):
            continue
        key = item.get("key", {})
        jid = str(key.get("remoteJid", ""))

        # ignora mensagens próprias e de grupo
        if key.get("fromMe") or jid.endswith("@g.us") or not jid:
            continue

        sender = jid.split("@")[0]
        message = item.get("message") or {}
        text = message.get("conversation") or message.get("extendedTextMessage", {}).get("text")

        if text:
            found.append(IncomingMessage(sender, key.get("id"), "text", text))
        else:
            kind = str(item.get("messageType", "unknown")).removesuffix("Message")
            found.append(IncomingMessage(sender, key.get("id"), kind, None))
    return found


def mask_number(number: str) -> str:
    return f"***{number[-4:]}" if len(number) > 4 else "***"
