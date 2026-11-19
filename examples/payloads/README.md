# Payloads de exemplo

JSON que chega no webhook, com dados fictícios. Uso nos testes e como referência.

| Arquivo | O que é |
| --- | --- |
| `recebidos/text.json` | texto pela Meta |
| `recebidos/image.json`, `audio.json`, `video.json`, `document.json` | mídias pela Meta |
| `recebidos/evolution-texto.json` | texto pela Evolution API v2 |

O da Evolution eu montei a partir da documentação, então vale comparar com um webhook real (`LOG_LEVEL=DEBUG` mostra tudo que chega).
