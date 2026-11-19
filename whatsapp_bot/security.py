import hashlib
import hmac


def signature_is_valid(app_secret: str, body: bytes, header: str | None) -> bool:
    # sem segredo, pula a checagem (só para testes locais)
    if not app_secret:
        return True
    if not header or not header.startswith("sha256="):
        return False
    expected = hmac.new(app_secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header.removeprefix("sha256="))
