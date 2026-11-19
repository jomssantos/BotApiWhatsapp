# uso: python scripts/send_test_message.py --to 5511999999999 [--text "oi"]
import argparse
import os
import sys

import httpx
from dotenv import load_dotenv

load_dotenv()


def main() -> int:
    parser = argparse.ArgumentParser(description="Envia uma mensagem de teste pela Meta")
    parser.add_argument("--to", required=True, help="número com DDI, só dígitos")
    parser.add_argument("--text", help="texto livre (sem isso, vai o template hello_world)")
    args = parser.parse_args()

    token = os.getenv("META_PERMANENT_TOKEN")
    phone_id = os.getenv("PHONE_NUMBER_ID")
    version = os.getenv("GRAPH_API_VERSION", "v23.0")
    if not token or not phone_id:
        print("Preencha META_PERMANENT_TOKEN e PHONE_NUMBER_ID no .env")
        return 1

    payload = {"messaging_product": "whatsapp", "to": args.to}
    if args.text:
        payload |= {"type": "text", "text": {"body": args.text}}
    else:
        payload |= {"type": "template", "template": {"name": "hello_world", "language": {"code": "en_US"}}}

    url = f"https://graph.facebook.com/{version}/{phone_id}/messages"
    response = httpx.post(url, headers={"Authorization": f"Bearer {token}"}, json=payload, timeout=30)
    print(response.status_code, response.text)
    return 0 if response.is_success else 1


if __name__ == "__main__":
    sys.exit(main())
