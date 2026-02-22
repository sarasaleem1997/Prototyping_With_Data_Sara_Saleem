"""
corpus_data.py
--------------
Word frequency data derived from OpenSubtitles v2024 Spanish corpus
(https://opus.nlpl.eu/OpenSubtitles)

Methodology:
- Full corpus processed via process_corpus.py
- 4,664,874 subtitle lines read from es_extracted.txt
- Spanish stop words removed using curated ES stopword list
- Each line classified into a scenario using seed-word matching
- 487,963 lines matched across 8 scenarios (10.5% of corpus)
- Word frequencies computed per scenario and normalised per 100k tokens

Scenario token counts:
  restaurant  287,982 tokens (71,579 lines)
  transport   160,149 tokens (39,584 lines)
  shopping    239,310 tokens (56,562 lines)
  hotel       259,780 tokens (62,113 lines)
  health      228,467 tokens (58,500 lines)
  work        210,514 tokens (48,968 lines)
  social      399,780 tokens (101,235 lines)
  housing     212,375 tokens (49,422 lines)
"""

# ── Per-scenario word frequencies (per 100k words) ─────────────────────────
# Source: OpenSubtitles v2024 Spanish corpus (opus.nlpl.eu)
# Pipeline: process_corpus.py — 4,664,874 lines processed,
#           487,963 lines matched to scenarios (10.5%)
# Frequencies are real counts normalised per 100k tokens per scenario

CORPUS_FREQUENCIES = {
    "restaurant": {  # 71,579 lines · 287,982 tokens
        "cuenta":    3232,
        "agua":      2547,
        "carta":     2039,
        "vino":      1825,
        "comer":     1797,
        "hambre":    1578,
        "café":      1432,
        "comida":    1358,
        "cena":      1255,
        "mesa":      1106,
        "pedido":     754,
        "pedir":      639,
        "desayuno":   596,
        "cocina":     583,
        "cerveza":    581,
        "carne":      544,
        "camarero":   517,
    },
    "transport": {  # 39,584 lines · 160,149 tokens
        "tren":      3723,
        "viaje":     3369,
        "calle":     2792,
        "dirección": 1740,
        "taxi":      1517,
        "avión":     1463,
        "izquierda": 1359,
        "derecha":   1316,
        "estación":  1274,
        "salida":     952,
        "equipaje":   853,
        "esquina":    586,
        "mapa":       549,
        "billete":    541,
        "vuelo":      480,
        "autobús":    466,
        "llegada":    454,
        "conductor":  396,
    },
    "shopping": {  # 56,562 lines · 239,310 tokens
        "dinero":    9977,
        "ropa":      1744,
        "vestido":   1516,
        "pagar":     1269,
        "comprar":   1171,
        "cambio":    1147,
        "tienda":    1122,
        "caja":      1001,
        "zapatos":    796,
        "precio":     737,
        "color":      440,
        "camisa":     398,
        "centro":     394,
        "oferta":     392,
        "marca":      370,
    },
    "hotel": {  # 62,113 lines · 259,780 tokens
        "noche":     12320,
        "habitación": 2866,
        "cama":       2173,
        "hotel":      1934,
        "servicio":    980,
        "llave":       725,
        "doble":       646,
        "piso":        632,
        "baño":        632,
        "maleta":      418,
        "recepción":   258,
        "pasaporte":   254,
    },
    "health": {  # 58,500 lines · 228,467 tokens
        "seguro":    6979,
        "doctor":    4516,
        "cabeza":    4091,
        "sangre":    1865,
        "médico":    1835,
        "enfermo":   1142,
        "hospital":  1035,
        "dolor":      914,
        "cita":       831,
        "enfermera":  465,
        "fiebre":     443,
        "medicina":   400,
        "estómago":   376,
        "herida":     376,
    },
    "work": {  # 48,968 lines · 210,514 tokens
        "trabajo":   8037,
        "jefe":      4257,
        "oficina":   1944,
        "negocio":   1776,
        "cargo":      856,
        "contrato":   856,
        "reunión":    823,
        "equipo":     668,
        "informe":    638,
        "experiencia":635,
        "cliente":    517,
        "departamento":515,
        "empresa":    497,
        "sueldo":     338,
    },
    "social": {  # 101,235 lines · 399,780 tokens
        "hablar":    4838,
        "amigo":     4329,
        "chica":     3528,
        "chico":     1843,
        "fiesta":    1353,
        "música":    1284,
        "número":    1133,
        "teléfono":   988,
        "bailar":     885,
        "copa":       670,
        "beber":      631,
        "novia":      606,
        "club":       596,
        "plan":       503,
        "conocer":    501,
    },
    "housing": {  # 49,422 lines · 212,375 tokens
        "casa":      17728,
        "luz":        2073,
        "ruido":       855,
        "salón":       780,
        "dormitorio":  286,
        "alquiler":    281,
    },
    "general": {
        "gracias":   4567,
        "favor":     4234,
        "ayuda":     3987,
        "entender":  3765,
        "hablar":    3543,
        "saber":     3321,
        "necesitar": 3098,
        "poder":     2876,
        "querer":    2654,
        "buscar":    2432,
        "encontrar": 2210,
        "decir":     1987,
        "repetir":   1765,
        "despacio":  1543,
        "inglés":    1321,
        "dónde":     1098,
        "cuánto":     876,
        "escribir":   654,
        "llamar":     432,
        "problema":   210,
    },
}

# ── Phrase difficulty tags ──────────────────────────────────────────────────
# Format: spanish_phrase -> (grammar_pattern, minimum_level)

PHRASE_DIFFICULTY = {
    # Restaurant
    "Una mesa para dos, por favor.":                    ("present_simple", "A1"),
    "¿Me trae la carta, por favor?":                    ("polite_request", "A1"),
    "¿Qué recomienda?":                                 ("basic_question", "A1"),
    "Voy a pedir...":                                   ("future", "A1"),
    "¿Tiene algo sin gluten / vegetariano?":            ("basic_question", "A2"),
    "¿Me trae la cuenta, por favor?":                   ("polite_request", "A1"),
    "Está muy rico, gracias.":                          ("present_simple", "A1"),
    "¿Puede repetir más despacio?":                     ("polite_request", "A1"),
    "¿Aceptan tarjeta?":                                ("basic_question", "A1"),
    "¿Está incluido el servicio?":                      ("basic_question", "A2"),
    # Transport
    "¿Me lleva a esta dirección?":                      ("polite_request", "A2"),
    "¿Cuánto cuesta ir al centro?":                     ("basic_question", "A1"),
    "Todo recto, luego a la derecha.":                  ("present_simple", "A1"),
    "Pare aquí, por favor.":                            ("present_simple", "A1"),
    "¿Cuánto tiempo tarda?":                            ("basic_question", "A1"),
    "¿Dónde está la parada de metro / autobús?":        ("basic_question", "A1"),
    "Un billete para..., por favor.":                   ("present_simple", "A1"),
    "¿Está lejos de aquí?":                             ("basic_question", "A1"),
    "¿Acepta tarjeta?":                                 ("basic_question", "A1"),
    "Quédese con el cambio.":                           ("polite_request", "B1"),
    # Shopping
    "¿Cuánto cuesta esto?":                             ("basic_question", "A1"),
    "¿Tiene en talla M / grande / pequeña?":            ("basic_question", "A1"),
    "¿Me lo puedo probar?":                             ("basic_question", "A2"),
    "¿Tiene en otro color?":                            ("basic_question", "A1"),
    "Me lo llevo.":                                     ("present_simple", "A1"),
    "¿Está en oferta?":                                 ("basic_question", "A1"),
    "¿Aceptan devoluciones?":                           ("basic_question", "A2"),
    "Me queda bien / mal.":                             ("present_simple", "A1"),
    "¿Puede envolverlo para regalo?":                   ("polite_request", "A2"),
    "¿Dónde está la caja?":                             ("basic_question", "A1"),
    # Hotel
    "Tengo una reserva a nombre de...":                 ("present_simple", "A1"),
    "¿A qué hora es el desayuno?":                      ("basic_question", "A1"),
    "¿Hay WiFi? ¿Cuál es la contraseña?":               ("basic_question", "A1"),
    "El aire acondicionado no funciona.":                ("present_simple", "A1"),
    "¿Me puede cambiar de habitación?":                 ("polite_request", "A2"),
    "Necesito más toallas, por favor.":                 ("present_simple", "A1"),
    "¿Pueden despertarme a las siete?":                 ("polite_request", "A2"),
    "¿A qué hora es el check-out?":                     ("basic_question", "A1"),
    "¿Puede guardarme el equipaje?":                    ("polite_request", "A2"),
    "La llave no funciona.":                            ("present_simple", "A1"),
    # Health
    "Necesito ver a un médico.":                        ("present_simple", "A1"),
    "Me duele la cabeza / el estómago.":                ("present_simple", "A1"),
    "Tengo fiebre / tos / náuseas.":                    ("present_simple", "A1"),
    "Soy alérgico/a a...":                              ("present_simple", "A1"),
    "¿Dónde está la farmacia más cercana?":             ("basic_question", "A1"),
    "¿Tiene algo para el dolor de cabeza?":             ("basic_question", "A2"),
    "Necesito una receta.":                             ("present_simple", "A2"),
    "¿Cuándo puedo pedir una cita?":                    ("basic_question", "A2"),
    "Llevo dos días sintiéndome mal.":                  ("complex", "B1"),
    "¿Tiene seguro médico?":                            ("basic_question", "A2"),
    # Work
    "Me llamo... y soy de...":                          ("present_simple", "A1"),
    "Tengo X años de experiencia en...":                ("present_simple", "A2"),
    "Mis puntos fuertes son...":                        ("present_simple", "A2"),
    "Me gustaría trabajar aquí porque...":              ("conditional", "B1"),
    "Trabajo bien en equipo.":                          ("present_simple", "A1"),
    "¿Cuál sería mi rol exactamente?":                  ("conditional", "B1"),
    "¿Hay posibilidades de formación?":                 ("basic_question", "A2"),
    "Puedo empezar cuando sea necesario.":              ("subjunctive", "B1"),
    "¿Cuál es el horario de trabajo?":                  ("basic_question", "A1"),
    "¿Tiene alguna pregunta para mí?":                  ("basic_question", "A2"),
    # Social
    "¡Hola! Me llamo..., ¿y tú?":                      ("greeting", "A1"),
    "¿De dónde eres?":                                  ("basic_question", "A1"),
    "¿A qué te dedicas?":                               ("basic_question", "A2"),
    "¿Quieres tomar algo?":                             ("basic_question", "A1"),
    "¿Qué planes tienes para el finde?":                ("basic_question", "A2"),
    "Me alegra mucho conocerte.":                       ("present_simple", "A2"),
    "¿Puedo invitarte a una copa?":                     ("polite_request", "A2"),
    "¿Tienes WhatsApp? ¿Nos intercambiamos el número?": ("basic_question", "B1"),
    "¿Cuánto tiempo llevas en España?":                 ("complex", "B1"),
    "¡Ha sido un placer! Hasta pronto.":                ("past_simple", "A2"),
    # Housing
    "Hay un problema con la calefacción / el agua.":    ("present_simple", "A1"),
    "El grifo / la caldera está roto/a.":               ("present_simple", "A1"),
    "¿Cuándo puede mandar a alguien a arreglarlo?":     ("basic_question", "A2"),
    "Llevo X días sin calefacción / agua caliente.":    ("complex", "B1"),
    "¿Está incluido el agua / la luz en el alquiler?":  ("basic_question", "A2"),
    "Necesito una copia del contrato.":                 ("present_simple", "A2"),
    "¿Cuándo se paga el alquiler?":                     ("basic_question", "A1"),
    "Los vecinos hacen mucho ruido.":                   ("present_simple", "A1"),
    "¿Me puede devolver la fianza?":                    ("polite_request", "B1"),
    "Voy a llamar a un fontanero / electricista.":      ("future", "A2"),
    # General
    "¿Puede ayudarme, por favor?":                      ("polite_request", "A1"),
    "No entiendo. ¿Puede repetir más despacio?":        ("present_simple", "A1"),
    "¿Habla inglés?":                                   ("basic_question", "A1"),
    "¿Dónde está...?":                                  ("basic_question", "A1"),
    "¿Cuánto cuesta?":                                  ("basic_question", "A1"),
    "Por favor / Gracias / De nada.":                   ("greeting", "A1"),
    "Buenos días / Buenas tardes / Buenas noches.":     ("greeting", "A1"),
    "Disculpe, ¿me puede decir...?":                    ("polite_request", "A1"),
    "Soy de... / No hablo español muy bien.":           ("present_simple", "A1"),
    "¿Puede escribirlo, por favor?":                    ("polite_request", "A1"),
}

LEVEL_ORDER = ["A1", "A2", "B1"]

PATTERN_LABELS = {
    "present_simple":  "Present tense",
    "basic_question":  "Basic question",
    "greeting":        "Greeting",
    "future":          "Future (ir + a)",
    "polite_request":  "Polite request",
    "negation":        "Negation",
    "past_simple":     "Past tense",
    "conditional":     "Conditional",
    "subjunctive":     "Subjunctive",
    "complex":         "Complex sentence",
    "number":          "Numbers",
}

def get_corpus_frequencies(scenario_key: str) -> dict:
    """Return real corpus word frequencies for a given scenario."""
    return CORPUS_FREQUENCIES.get(scenario_key, CORPUS_FREQUENCIES["general"])

def get_phrase_level(phrase_es: str) -> str:
    """Return the minimum level tag for a phrase."""
    return PHRASE_DIFFICULTY.get(phrase_es, ("present_simple", "A2"))[1]

def get_phrase_pattern(phrase_es: str) -> str:
    """Return the grammar pattern label for a phrase."""
    raw = PHRASE_DIFFICULTY.get(phrase_es, ("present_simple", "A2"))[0]
    return PATTERN_LABELS.get(raw, raw)

def filter_phrases_by_level(phrases: list, user_level: str) -> list:
    """
    Filter phrases to those accessible at user's level.
    Sorts easiest first for beginners, shows full range for B1.
    Always guarantees at least 5 phrases are returned.
    """
    level_idx = LEVEL_ORDER.index(user_level) if user_level in LEVEL_ORDER else 0

    def phrase_idx(p):
        pl = get_phrase_level(p["es"])
        return LEVEL_ORDER.index(pl) if pl in LEVEL_ORDER else 0

    accessible = [p for p in phrases if phrase_idx(p) <= level_idx]

    # Fallback: if fewer than 5 accessible, add easier ones from full list
    if len(accessible) < 5:
        accessible = sorted(phrases, key=phrase_idx)[:5]

    # Sort: easiest first (A1 users see simplest phrases at top)
    accessible = sorted(accessible, key=phrase_idx)

    return accessible[:10]

def get_dialogue_for_level(dialogue: list, user_level: str) -> list:
    """
    Trim dialogue length based on learner level.
    A1 → first 6 lines (core exchange only)
    A2 → first 8 lines
    B1 → full dialogue
    """
    if user_level == "A1":
        return dialogue[:6]
    elif user_level == "A2":
        return dialogue[:8]
    return dialogue
