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

Note: Phrase generation and dialogue are handled by llm_generator.py (Gemini API).
This module is retained solely for the corpus frequency chart — real linguistic data
that the LLM cannot replicate.
"""

# ── Per-scenario word frequencies (per 100k words) ─────────────────────────
# Source: OpenSubtitles v2024 Spanish corpus (opus.nlpl.eu)
# Pipeline: process_corpus.py — 4,664,874 lines processed,
#           487,963 lines matched to scenarios (10.5%)

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
