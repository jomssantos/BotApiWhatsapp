

import hashlib
import hmac
import json

import pytest
from fastapi.testclient import TestClient

from whatsapp_bot import main
from whatsapp_bot.config import Settings


def make_settings(**over) -> Settings:
    base = dict(
        provider="meta", port=5000, log_level="WARNING",
        groq_api_key="g", groq_model="m", system_prompt="s", max_history_messages=10,
        meta_token="t", phone_number_id="1", verify_token="meu-token", meta_app_secret="",
        graph_version="v23.0", evolution_url="http://x", evolution_api_key="k", instance_name="i",
    )
    base.update(over)
    return Settings(**base)


class FakeLLM:
    async def reply(self, messages):
        return "resposta da IA: " + messages[-1]["content"]


class FakeSender:
    def __init__(self):
        self.sent = []

    async def send_text(self, to, text):
        self.sent.append((to, text))


@pytest.fixture
def client_and_sender(monkeypatch):
    sender = FakeSender()
    real_build = main.build_services

    def fake_build(settings, http_client):
        services = real_build(settings, http_client)
        services.sender = sender
        services.llm = FakeLLM()
        return services

    monkeypatch.setattr(main, "build_services", fake_build)

    def factory(**over):
        app = main.create_app(make_settings(**over))
        return TestClient(app), sender

    return factory


def test_verificacao_do_webhook(client_and_sender):
    factory = client_and_sender
    client, _ = factory()
    with client:
        ok = client.get("/webhook", params={"hub.mode": "subscribe", "hub.verify_token": "meu-token", "hub.challenge": "123"})
        assert ok.status_code == 200 and ok.text == "123"

        ruim = client.get("/webhook", params={"hub.mode": "subscribe", "hub.verify_token": "errado", "hub.challenge": "123"})
        assert ruim.status_code == 403


def test_mensagem_de_texto_gera_resposta(client_and_sender, load_payload):
    client, sender = client_and_sender()
    with client:
        resp = client.post("/webhook", json=load_payload("text.json"))
        assert resp.status_code == 200
    assert sender.sent == [("5511999999999", "resposta da IA: Oi, tudo bem?")]


def test_webhook_repetido_nao_responde_duas_vezes(client_and_sender, load_payload):
    client, sender = client_and_sender()
    with client:
        client.post("/webhook", json=load_payload("text.json"))
        client.post("/webhook", json=load_payload("text.json"))
    assert len(sender.sent) == 1


def test_midia_recebe_aviso_amigavel(client_and_sender, load_payload):
    client, sender = client_and_sender()
    with client:
        client.post("/webhook", json=load_payload("image.json"))
    assert sender.sent[0][1] == main.UNSUPPORTED_REPLY


def test_assinatura_invalida_e_rejeitada(client_and_sender, load_payload):
    client, sender = client_and_sender(meta_app_secret="segredo")
    body = json.dumps(load_payload("text.json")).encode()
    with client:
        ruim = client.post("/webhook", content=body, headers={"X-Hub-Signature-256": "sha256=zzz"})
        assert ruim.status_code == 403

        assinatura = "sha256=" + hmac.new(b"segredo", body, hashlib.sha256).hexdigest()
        bom = client.post("/webhook", content=body, headers={"X-Hub-Signature-256": assinatura})
        assert bom.status_code == 200
    assert len(sender.sent) == 1


def test_modo_evolution_ignora_o_que_o_bot_enviou(client_and_sender, load_payload):
    client, sender = client_and_sender(provider="evolution")
    payload = load_payload("evolution-texto.json")
    with client:
        client.post("/webhook", json=payload)
        payload["data"]["key"]["fromMe"] = True
        payload["data"]["key"]["id"] = "OUTRO"
        client.post("/webhook", json=payload)
    assert len(sender.sent) == 1


def test_validacao_de_configuracao():
    with pytest.raises(RuntimeError, match="GROQ_API_KEY"):
        make_settings(groq_api_key="").validate()
    with pytest.raises(RuntimeError, match="PROVIDER"):
        make_settings(provider="outro").validate()
