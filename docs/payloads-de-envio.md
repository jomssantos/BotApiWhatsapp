# Mensagens que o bot pode enviar

Juntei aqui os corpos JSON de cada tipo de mensagem da Cloud API da Meta. Hoje o bot só envia texto, o resto é referência para quem quiser estender o `senders.py`.

```
POST https://graph.facebook.com/v23.0/{PHONE_NUMBER_ID}/messages
Authorization: Bearer {META_PERMANENT_TOKEN}
```

Os números, links e IDs são de exemplo. Mensagens livres só chegam dentro de 24h depois da última mensagem da pessoa; fora disso, só template aprovado.

## Texto

```json
{
  "messaging_product": "whatsapp",
  "recipient_type": "individual",
  "to": "5511999999999",
  "type": "text",
  "text": {
    "preview_url": false,
    "body": "Olá!"
  }
}
```

## Imagem por URL

```json
{
  "messaging_product": "whatsapp",
  "to": "5511999999999",
  "type": "image",
  "image": {
    "link": "https://meusite.com/imagem.jpg",
    "caption": "Legenda da imagem"
  }
}
```

## Imagem já enviada para a Meta (Media ID)

```json
{
  "messaging_product": "whatsapp",
  "to": "5511999999999",
  "type": "image",
  "image": {
    "id": "123456789012345"
  }
}
```

## Vídeo

```json
{
  "messaging_product": "whatsapp",
  "to": "5511999999999",
  "type": "video",
  "video": {
    "link": "https://meusite.com/video.mp4",
    "caption": "Confira este vídeo"
  }
}
```

## Vídeo por Media ID

```json
{
  "messaging_product": "whatsapp",
  "to": "5511999999999",
  "type": "video",
  "video": {
    "id": "123456789"
  }
}
```

## Áudio

```json
{
  "messaging_product": "whatsapp",
  "to": "5511999999999",
  "type": "audio",
  "audio": {
    "link": "https://meusite.com/audio.mp3"
  }
}
```

## Áudio por Media ID

```json
{
  "messaging_product": "whatsapp",
  "to": "5511999999999",
  "type": "audio",
  "audio": {
    "id": "123456789"
  }
}
```

## Documento

```json
{
  "messaging_product": "whatsapp",
  "to": "5511999999999",
  "type": "document",
  "document": {
    "link": "https://meusite.com/arquivo.pdf",
    "filename": "Contrato.pdf",
    "caption": "Segue o contrato"
  }
}
```

## Documento por Media ID

```json
{
  "messaging_product": "whatsapp",
  "to": "5511999999999",
  "type": "document",
  "document": {
    "id": "123456789",
    "filename": "Contrato.pdf"
  }
}
```

## Sticker

```json
{
  "messaging_product": "whatsapp",
  "to": "5511999999999",
  "type": "sticker",
  "sticker": {
    "id": "123456789"
  }
}
```

## Sticker por link

```json
{
  "messaging_product": "whatsapp",
  "to": "5511999999999",
  "type": "sticker",
  "sticker": {
    "link": "https://meusite.com/sticker.webp"
  }
}
```

## Localização

```json
{
  "messaging_product": "whatsapp",
  "to": "5511999999999",
  "type": "location",
  "location": {
    "latitude": -23.5505,
    "longitude": -46.6333,
    "name": "Meu Escritório",
    "address": "Rua Exemplo, 123"
  }
}
```

## Contato

```json
{
  "messaging_product": "whatsapp",
  "to": "5511999999999",
  "type": "contacts",
  "contacts": [
    {
      "name": {
        "formatted_name": "Maria Souza"
      },
      "phones": [
        {
          "phone": "5511999999999",
          "type": "CELL"
        }
      ]
    }
  ]
}
```

## Reação

```json
{
  "messaging_product": "whatsapp",
  "to": "5511999999999",
  "type": "reaction",
  "reaction": {
    "message_id": "wamid.HBg...",
    "emoji": "👍"
  }
}
```

## Template

```json
{
  "messaging_product": "whatsapp",
  "to": "5511999999999",
  "type": "template",
  "template": {
    "name": "boas_vindas",
    "language": {
      "code": "pt_BR"
    }
  }
}
```

## Template com parâmetros

```json
{
  "messaging_product": "whatsapp",
  "to": "5511999999999",
  "type": "template",
  "template": {
    "name": "confirmacao_agendamento",
    "language": {
      "code": "pt_BR"
    },
    "components": [
      {
        "type": "body",
        "parameters": [
          {
            "type": "text",
            "text": "Maria"
          },
          {
            "type": "text",
            "text": "08/07 às 14:00"
          }
        ]
      }
    ]
  }
}
```

## Botões (Interactive)

```json
{
  "messaging_product": "whatsapp",
  "to": "5511999999999",
  "type": "interactive",
  "interactive": {
    "type": "button",
    "body": {
      "text": "Deseja continuar?"
    },
    "action": {
      "buttons": [
        {
          "type": "reply",
          "reply": {
            "id": "sim",
            "title": "Sim"
          }
        },
        {
          "type": "reply",
          "reply": {
            "id": "nao",
            "title": "Não"
          }
        }
      ]
    }
  }
}
```

## Lista

```json
{
  "messaging_product": "whatsapp",
  "to": "5511999999999",
  "type": "interactive",
  "interactive": {
    "type": "list",
    "body": {
      "text": "Escolha uma opção"
    },
    "action": {
      "button": "Abrir lista",
      "sections": [
        {
          "title": "Serviços",
          "rows": [
            {
              "id": "1",
              "title": "Consulta"
            },
            {
              "id": "2",
              "title": "Exames"
            }
          ]
        }
      ]
    }
  }
}
```
