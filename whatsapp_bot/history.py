from collections import OrderedDict, deque


class ConversationHistory:
    # memória por contato, some ao reiniciar
    def __init__(self, system_prompt: str, max_messages: int = 10) -> None:
        self._system = {"role": "system", "content": system_prompt}
        self._max = max(2, max_messages)
        self._chats: dict[str, deque] = {}

    def build_prompt(self, user: str, new_message: str) -> list[dict]:
        past = list(self._chats.get(user, ()))
        return [self._system, *past, {"role": "user", "content": new_message}]

    def remember(self, user: str, user_message: str, reply: str) -> None:
        chat = self._chats.setdefault(user, deque(maxlen=self._max))
        chat.append({"role": "user", "content": user_message})
        chat.append({"role": "assistant", "content": reply})


class RecentIds:
    # evita responder o mesmo webhook duas vezes
    def __init__(self, capacity: int = 1000) -> None:
        self._capacity = capacity
        self._ids: OrderedDict[str, None] = OrderedDict()

    def seen_before(self, message_id: str | None) -> bool:
        if not message_id:
            return False
        if message_id in self._ids:
            return True
        self._ids[message_id] = None
        if len(self._ids) > self._capacity:
            self._ids.popitem(last=False)
        return False
