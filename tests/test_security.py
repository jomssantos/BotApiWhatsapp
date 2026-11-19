import hashlib
import hmac

from whatsapp_bot.security import signature_is_valid
from whatsapp_bot.senders import split_text


def _sig(secret: str, body: bytes) -> str:
    return "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def test_assinatura_valida():
    body = b'{"ok": true}'
    assert signature_is_valid("segredo", body, _sig("segredo", body))


def test_assinatura_errada_ou_ausente():
    body = b'{"ok": true}'
    assert not signature_is_valid("segredo", body, _sig("outro", body))
    assert not signature_is_valid("segredo", body, None)
    assert not signature_is_valid("segredo", body, "sha256=")


def test_sem_segredo_configurado_nao_valida():
    assert signature_is_valid("", b"qualquer", None)


def test_split_text_respeita_limite():
    texto = ("palavra " * 1500).strip()
    partes = split_text(texto, limit=1000)
    assert all(len(p) <= 1000 for p in partes)
    assert " ".join(partes).split() == texto.split()


def test_split_text_curto_e_vazio():
    assert split_text("oi") == ["oi"]
    assert split_text("   ") == []
