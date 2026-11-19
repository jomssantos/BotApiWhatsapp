from whatsapp_bot.parsing import mask_number, parse_payload


def test_meta_texto(load_payload):
    [msg] = parse_payload(load_payload("text.json"))
    assert msg.kind == "text"
    assert msg.text == "Oi, tudo bem?"
    assert msg.sender == "5511999999999"
    assert msg.message_id.startswith("wamid.")


def test_meta_midias_viram_mensagem_sem_texto(load_payload):
    for nome, tipo in [("image.json", "image"), ("audio.json", "audio"),
                       ("video.json", "video"), ("document.json", "document")]:
        [msg] = parse_payload(load_payload(nome))
        assert msg.kind == tipo
        assert msg.text is None


def test_meta_status_sem_mensagens_e_ignorado():
    payload = {"entry": [{"changes": [{"value": {"statuses": [{"status": "delivered"}]}}]}]}
    assert parse_payload(payload) == []


def test_evolution_texto(load_payload):
    [msg] = parse_payload(load_payload("evolution-texto.json"))
    assert msg.text == "Oi, tudo bem?"
    assert msg.sender == "5511999999999"


def test_evolution_ignora_mensagem_do_proprio_bot(load_payload):
    payload = load_payload("evolution-texto.json")
    payload["data"]["key"]["fromMe"] = True
    assert parse_payload(payload) == []


def test_evolution_ignora_grupos(load_payload):
    payload = load_payload("evolution-texto.json")
    payload["data"]["key"]["remoteJid"] = "120363000000000000@g.us"
    assert parse_payload(payload) == []


def test_evolution_ignora_outros_eventos(load_payload):
    payload = load_payload("evolution-texto.json")
    payload["event"] = "SEND_MESSAGE"
    assert parse_payload(payload) == []


def test_payload_desconhecido():
    assert parse_payload({"qualquer": "coisa"}) == []


def test_mask_number():
    assert mask_number("5511999999999") == "***9999"
