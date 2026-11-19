import uvicorn

from .config import get_settings

uvicorn.run("whatsapp_bot.main:app", host="0.0.0.0", port=get_settings().port)
