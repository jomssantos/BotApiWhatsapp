import json
from pathlib import Path

import pytest

PAYLOADS = Path(__file__).resolve().parent.parent / "examples" / "payloads" / "recebidos"


@pytest.fixture
def load_payload():
    def _load(name: str) -> dict:
        return json.loads((PAYLOADS / name).read_text(encoding="utf-8"))

    return _load
