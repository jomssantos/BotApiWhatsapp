# BotApiWhatsapp

Bot de WhatsApp em Python que responde mensagens com IA. Eu fiz para atender conversas sem precisar de ninguém online: a mensagem chega por webhook, o bot pergunta para um modelo da [Groq](https://groq.com) e devolve a resposta no mesmo chat.

Dá para ligar de dois jeitos, trocando só a variável `PROVIDER`:

- `meta`: direto na Cloud API oficial da Meta. É o caminho mais simples.
- `evolution`: passando pela [Evolution API](https://github.com/EvolutionAPI/evolution-api).

## Como funciona

1. A pessoa manda uma mensagem.
2. A Meta (ou a Evolution) chama `POST /webhook` no meu servidor.
3. O servidor responde `200` na hora e trata a mensagem em segundo plano.
4. O bot monta o histórico da conversa, pergunta para a Groq e envia a resposta.

Eu respondo o `200` antes de chamar a IA porque, se demorar, a Meta reenvia o mesmo webhook. Por garantia, também guardo os IDs recentes e ignoro repetidos.

## O que ele faz

- Responde texto com IA e lembra das últimas mensagens de cada contato.
- Valida a assinatura dos webhooks da Meta.
- Ignora mensagens duplicadas, de grupo e as que o próprio bot enviou.
- Avisa quando recebe imagem, áudio ou outro tipo que ainda não trato.
- Quebra respostas longas em várias mensagens.
- Mostra só os 4 últimos dígitos do número nos logs.

## Estrutura

```text
whatsapp_bot/
  main.py       servidor FastAPI e webhook
  config.py     leitura do .env
  parsing.py    entende o JSON da Meta e da Evolution
  llm.py        chamada à Groq
  history.py    memória das conversas e filtro de repetidas
  senders.py    envio pela Meta ou Evolution
  security.py   assinatura dos webhooks
scripts/        teste de envio e criação da instância Evolution
examples/       JSON de exemplo
docs/           formatos de mensagem que a Meta aceita
tests/
```

## Como rodar

Precisa de Python 3.10+, uma chave da [Groq](https://console.groq.com/keys) e um app da Meta com o produto WhatsApp (token e ID do número). Para a Meta alcançar o servidor, use um túnel com HTTPS, como o [ngrok](https://ngrok.com).

```bash
git clone https://github.com/jomssantos/BotApiWhatsapp.git
cd BotApiWhatsapp

python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env           # Windows: copy .env.example .env
python -m whatsapp_bot
```

Abrindo `http://localhost:5000` deve aparecer `{"status":"ok",...}`.

## Configuração

Tudo fica no `.env`. O `.env.example` já tem um comentário por linha.

| Variável | Obrigatória | Para que serve |
| --- | --- | --- |
| `PROVIDER` | sim | `meta` ou `evolution` (padrão `meta`) |
| `GROQ_API_KEY` | sim | chave da Groq |
| `GROQ_MODEL` | não | modelo usado (padrão `llama-3.1-8b-instant`) |
| `SYSTEM_PROMPT` | não | personalidade e regras do bot |
| `MAX_HISTORY_MESSAGES` | não | quantas mensagens lembrar por pessoa (padrão `10`) |
| `VERIFY_TOKEN` | sim | texto inventado por você, igual ao do painel da Meta |
| `META_PERMANENT_TOKEN` | modo meta | token da API do WhatsApp |
| `PHONE_NUMBER_ID` | modo meta | ID do número |
| `META_APP_SECRET` | recomendada | valida a assinatura dos webhooks |
| `EVOLUTION_URL`, `EVOLUTION_API_KEY`, `INSTANCE_NAME` | modo evolution | acesso à Evolution API |

O token temporário do painel da Meta expira em cerca de 24 horas. Para uso de verdade, crie um usuário do sistema no Gerenciador de Negócios e gere um token permanente.

### Webhook na Meta

1. No app, vá em **WhatsApp > Configuração > Webhook**.
2. Em **URL de retorno**, coloque o endereço público terminado em `/webhook`.
3. Em **Verificar token**, o mesmo valor do `VERIFY_TOKEN`.
4. Clique em **Verificar e salvar** e assine o campo **messages**.

Com o número de teste da Meta, só dá para conversar com números cadastrados como destinatários no painel.

### Evolution API

```bash
# no .env: PROVIDER=evolution e as variáveis da Evolution
docker compose up -d
python scripts/create_evolution_instance.py --webhook-url https://seu-dominio.com/webhook
python -m whatsapp_bot
```

Se o bot roda na sua máquina e a Evolution no Docker, o webhook visto de dentro do container é `http://host.docker.internal:5000/webhook`, não `localhost`.

## Testando

```bash
pip install -r requirements-dev.txt
pytest
```

Os testes não usam internet: troquei a Groq e o WhatsApp por versões falsas.

Para checar o token da Meta antes de subir o bot:

```bash
python scripts/send_test_message.py --to 5511999999999
python scripts/send_test_message.py --to 5511999999999 --text "Oi"
```

O número vai com DDI e DDD, só dígitos. Sem `--text`, envia o template `hello_world`, que funciona em qualquer conta nova.

## Personalizando

- **Personalidade:** edite `SYSTEM_PROMPT` no `.env`.
- **Outros tipos de mensagem:** a decisão fica em `handle_message`, no `main.py`. O campo `kind` diz o tipo recebido.
- **Enviar imagem, botões etc.:** os corpos de requisição estão em [`docs/payloads-de-envio.md`](docs/payloads-de-envio.md). É só criar um método novo no `senders.py`.

## Segurança

- Nunca suba o `.env`. O `.gitignore` já ignora, mas confira com `git status`.
- Se um token já apareceu em arquivo público ou print, considere vazado: gere outro e revogue o antigo.
- Configure `META_APP_SECRET` em produção. Sem ele, qualquer um que descobrir a URL consegue mandar mensagens falsas.
- Com `LOG_LEVEL=DEBUG` o conteúdo dos webhooks aparece inteiro. Use só para depurar.

## Problemas comuns

- **A Meta não verifica o webhook:** confira se o `VERIFY_TOKEN` é idêntico (maiúsculas e espaços contam), se o bot está no ar e se a URL termina em `/webhook`.
- **Recebe mas não responde:** olhe o terminal. Erro 190 da Meta é token expirado; "destinatário não permitido" é número não cadastrado no painel.
- **Texto livre não chega, `hello_world` chega:** fora da janela de 24h só template funciona.
- **403 depois de configurar `META_APP_SECRET`:** o segredo difere do que está em Configurações do app > Básico. Copie de novo, sem espaços.
- **Esquece a conversa ao reiniciar:** é esperado, o histórico fica só na memória.
- **Nada acontece no modo Evolution:** rode com `LOG_LEVEL=DEBUG` e compare o JSON com `examples/payloads/recebidos/evolution-texto.json`.

## Limitações

- O histórico some ao reiniciar (dá para trocar por Redis ou banco).
- Só texto: áudio, imagem e documento ainda não são entendidos.
- Não tem limite de mensagens por pessoa.
- O suporte à Evolution API foi escrito com base na documentação da v2 e testado só com os exemplos da pasta `examples/`. Se algo se comportar diferente na sua instância, abra uma issue.

## Licença

MIT. Veja [LICENSE](LICENSE).
