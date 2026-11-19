from whatsapp_bot.history import ConversationHistory, RecentIds


def test_prompt_comeca_com_instrucao_e_termina_com_mensagem_nova():
    h = ConversationHistory("seja gentil", max_messages=10)
    prompt = h.build_prompt("u1", "oi")
    assert prompt[0] == {"role": "system", "content": "seja gentil"}
    assert prompt[-1] == {"role": "user", "content": "oi"}


def test_historico_respeita_o_limite_por_pessoa():
    h = ConversationHistory("x", max_messages=4)
    for i in range(5):
        h.remember("u1", f"pergunta {i}", f"resposta {i}")
    contents = [m["content"] for m in h.build_prompt("u1", "nova")[1:-1]]
    assert contents == ["pergunta 3", "resposta 3", "pergunta 4", "resposta 4"]


def test_pessoas_diferentes_nao_misturam_conversas():
    h = ConversationHistory("x")
    h.remember("ana", "oi", "olá")
    assert len(h.build_prompt("bia", "oi")) == 2


def test_recent_ids_detecta_repeticao():
    ids = RecentIds(capacity=2)
    assert ids.seen_before("a") is False
    assert ids.seen_before("a") is True
    assert ids.seen_before(None) is False


def test_recent_ids_esquece_os_mais_antigos():
    ids = RecentIds(capacity=2)
    for x in ("a", "b", "c"):
        ids.seen_before(x)
    assert ids.seen_before("a") is False
