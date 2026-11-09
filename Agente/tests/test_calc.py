import calc


def test_addizione():
    assert calc.calculate("2 + 3") == "2 + 3 = 5"


def test_precedenza():
    assert calc.calculate("2 + 3 * 4") == "2 + 3 * 4 = 14"


def test_parentesi():
    assert calc.calculate("(2 + 3) * 4") == "(2 + 3) * 4 = 20"


def test_divisione_float():
    assert calc.calculate("7 / 2") == "7 / 2 = 3.5"


def test_unario_negativo():
    assert calc.calculate("-5 + 2") == "-5 + 2 = -3"


def test_schema_ben_formato():
    s = calc.CALC_TOOL_SCHEMA
    assert s["function"]["name"] == "calculate"
    assert s["function"]["parameters"]["required"] == ["expression"]


def test_espressione_vuota():
    assert calc.calculate("") == "espressione non valida"


def test_sintassi_invalida():
    assert calc.calculate("2 +") == "espressione non valida"


def test_nome_non_consentito():
    assert calc.calculate("x + 1") == "operazione non consentita"


def test_chiamata_non_consentita():
    assert calc.calculate("__import__('os')") == "operazione non consentita"


def test_confronto_non_consentito():
    assert calc.calculate("2 == 3") == "operazione non consentita"


def test_divisione_per_zero():
    assert calc.calculate("1 / 0") == "divisione per zero"


def test_espressione_troppo_lunga():
    assert calc.calculate("1+" * 300 + "1") == "espressione troppo lunga"


def test_potenza():
    assert calc.calculate("2 ** 10") == "2 ** 10 = 1024"


def test_modulo():
    assert calc.calculate("17 % 5") == "17 % 5 = 2"


def test_divisione_intera():
    assert calc.calculate("17 // 5") == "17 // 5 = 3"


def test_potenza_entro_il_cap():
    # 10**1000 = 1001 cifre: entro il limite, calcolata (verifica che NON venga rifiutata)
    assert calc.calculate("10 ** 1000").startswith("10 ** 1000 = 1")


def test_potenza_oltre_il_cap():
    assert calc.calculate("10 ** 1001") == "risultato troppo grande"


def test_potenza_annidata_oltre_il_cap():
    assert calc.calculate("(10 ** 1000) ** 2") == "risultato troppo grande"


def test_torre_di_potenze_oltre_il_cap():
    assert calc.calculate("10 ** 10 ** 10") == "risultato troppo grande"


def test_base_negativa_esponente_frazionario():
    assert calc.calculate("(-8) ** 0.5") == "risultato non valido"


def test_modulo_per_zero():
    assert calc.calculate("5 % 0") == "divisione per zero"


def test_divisione_intera_per_zero():
    assert calc.calculate("5 // 0") == "divisione per zero"
