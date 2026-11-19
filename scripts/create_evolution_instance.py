# uso: python scripts/create_evolution_instance.py [--webhook-url https://meu-dominio.com/webhook]
import argparse
import os
import sys

import httpx
from dotenv import load_dotenv

load_dotenv()

EVENTS = ["MESSAGES_UPSERT", "SEND_MESSAGE", "MESSAGES_UPDATE"]
REQUIRED = ["EVOLUTION_URL", "EVOLUTION_API_KEY", "INSTANCE_NAME", "META_PERMANENT_TOKEN", "PHONE_NUMBER_ID", "BUSINESS_ID"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Cria a instância na Evolution API")
    parser.add_argument("--webhook-url", help="URL pública do bot, terminando em /webhook")
    args = parser.parse_args()

    env = {name: os.getenv(name, "").strip() for name in REQUIRED}
    missing = [name for name, value in env.items() if not value]
    if missing:
        print("Faltam variáveis no .env: " + ", ".join(missing))
        return 1

    base = env["EVOLUTION_URL"].rstrip("/")
    headers = {"apikey": env["EVOLUTION_API_KEY"]}
    instance = {
        "instanceName": env["INSTANCE_NAME"],
        "token": env["META_PERMANENT_TOKEN"],
        "number": env["PHONE_NUMBER_ID"],
        "businessId": env["BUSINESS_ID"],
        "qrcode": False,
        "integration": "WHATSAPP-BUSINESS",
    }

    response = httpx.post(f"{base}/instance/create", headers=headers, json=instance, timeout=30)
    print("criar instância:", response.status_code, response.text)

    if args.webhook_url:
        body = {"webhook": {"enabled": True, "url": args.webhook_url, "events": EVENTS}}
        response = httpx.post(f"{base}/webhook/set/{env['INSTANCE_NAME']}", headers=headers, json=body, timeout=30)
        print("webhook:", response.status_code, response.text)
        return 0 if response.is_success else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
