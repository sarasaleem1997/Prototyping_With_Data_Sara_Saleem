"""
process_corpus.py
─────────────────
Run this script LOCALLY on the full OpenSubtitles dataset to generate
real word frequencies for ConvoReady's corpus_data.py.

Usage:
    python process_corpus.py path/to/es.txt

Output:
    Prints a ready-to-paste corpus_frequencies dict for corpus_data.py

Requirements:
    pip install tqdm
"""

import re
import sys
import json
from collections import Counter, defaultdict

# ── Spanish stop words ──────────────────────────────────────────────────────
ES_STOPWORDS = {
    "de","la","que","el","en","y","a","los","del","se","las","un","por",
    "con","no","una","su","para","es","al","lo","como","más","pero","sus",
    "le","ya","o","fue","este","ha","sí","porque","esta","son","entre",
    "cuando","muy","sin","sobre","ser","tiene","también","me","hasta",
    "hay","donde","han","quien","están","estado","desde","todo","nos",
    "durante","uno","ni","contra","ese","eso","ante","ellos","e","esto",
    "mí","antes","algunos","qué","unos","yo","otro","otras","otra","él",
    "tanto","esa","estos","mucho","quién","le","dónde","bien","así",
    "cada","era","ellas","dos","bajo","estos","mi","mis","tú","te","ti",
    "tu","tus","vos","os","mío","mía","tuyo","tuya","suyo","suya",
    "nuestro","vuestra","vuestro","cuál","cuáles","quién","quiénes",
    "cómo","cuándo","cuánto","cuánta","cuántos","cuántas","que","si",
    "porque","pues","aunque","mientras","sino","luego","entonces","así",
    "aquí","allí","allá","acá","ahora","hoy","ayer","mañana","siempre",
    "nunca","jamás","también","tampoco","solo","sólo","tal","vez","han",
    "sido","sido","hay","haber","ser","estar","tener","hacer","poder",
    "deber","querer","saber","ver","dar","ir","venir","salir","llevar",
}

# ── Scenario seed words (used to classify subtitle lines by topic) ──────────
SCENARIO_SEEDS = {
    "restaurant": [
        "mesa","comer","comida","restaurante","carta","menú","camarero","pedido",
        "pedir","cuenta","bebida","vino","agua","plato","hambre","reserva",
        "cocina","cocinero","chef","propina","postre","ensalada","carne","pollo",
        "pescado","verdura","fruta","sopa","desayuno","almuerzo","cena","café",
        "cerveza","zumo","refresco","postre","tarjeta","efectivo","factura",
    ],
    "transport": [
        "taxi","autobús","metro","tren","avión","aeropuerto","estación","parada",
        "billete","ticket","conductor","chofer","ruta","mapa","dirección","calle",
        "derecha","izquierda","recto","semáforo","esquina","kilómetro","viaje",
        "llegada","salida","retraso","andén","terminal","vuelo","equipaje",
    ],
    "shopping": [
        "tienda","comprar","precio","dinero","pagar","caro","barato","oferta",
        "descuento","talla","ropa","color","probador","caja","cambio","recibo",
        "marca","moda","bolso","zapatos","ropa","vestido","pantalón","camisa",
        "devolución","reembolso","tarjeta","efectivo","mercado","centro","mall",
    ],
    "hotel": [
        "hotel","habitación","cama","llave","reserva","recepción","desayuno",
        "maleta","baño","toalla","ducha","wifi","pasaporte","equipaje","ascensor",
        "piso","noche","limpieza","servicio","almohada","manta","minibar",
        "factura","check","suit","habitación","single","doble",
    ],
    "health": [
        "médico","doctor","hospital","dolor","enfermo","medicina","farmacia",
        "fiebre","herida","alergia","receta","cita","cabeza","estómago","pastilla",
        "tratamiento","operación","urgencias","sangre","análisis","síntoma",
        "enfermera","ambulancia","seguro","consulta","radiografía","vendaje",
    ],
    "work": [
        "trabajo","empresa","jefe","reunión","proyecto","sueldo","contrato",
        "oficina","equipo","cliente","entrevista","experiencia","cargo","horario",
        "formación","currículum","candidato","departamento","informe","beneficio",
        "empleado","empresa","negocio","ventas","marketing","reunión","plazo",
    ],
    "social": [
        "amigo","fiesta","conocer","salir","gustar","hablar","quedar","bar",
        "beber","reír","bailar","música","noche","invitar","pareja","plan",
        "copa","número","teléfono","whatsapp","cita","novio","novia","chico",
        "chica","divertir","bailar","club","discoteca","cumpleaños","celebrar",
    ],
    "housing": [
        "piso","casa","alquiler","casero","habitación","contrato","reparar",
        "agua","luz","calefacción","ducha","fontanero","avería","fianza","vecino",
        "ruido","llave","grifo","tubería","electricista","inquilino","propietario",
        "mueble","cocina","baño","dormitorio","salón","terraza","garaje","trastero",
    ],
}

def tokenise(text: str) -> list:
    """Lowercase, strip punctuation, remove stopwords and short words."""
    clean = re.sub(r'[^\w\s]', ' ', text.lower())
    return [
        w for w in clean.split()
        if len(w) > 2
        and w not in ES_STOPWORDS
        and not w.isdigit()
        and w.isalpha()
    ]

def classify_line(tokens: list, seeds: dict) -> str | None:
    """Return the best matching scenario for a line, or None if no match."""
    scores = defaultdict(int)
    for token in tokens:
        for scenario, seed_words in seeds.items():
            if token in seed_words:
                scores[scenario] += 1
    if not scores:
        return None
    return max(scores, key=scores.get)

def process_corpus(filepath: str, max_lines: int = 5_000_000):
    """
    Main processing function.
    Reads the corpus line by line (memory efficient),
    classifies each line, and computes per-scenario word frequencies.
    """
    scenario_counters = {k: Counter() for k in SCENARIO_SEEDS}
    scenario_line_counts = defaultdict(int)
    total_lines = 0
    matched_lines = 0

    print(f"Processing {filepath}...")
    print("(This may take several minutes for the full corpus)\n")

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for i, line in enumerate(f):
            if i >= max_lines:
                break

            # Handle tab-separated bilingual files (take Spanish column)
            if "\t" in line:
                parts = line.strip().split("\t")
                text = parts[-1]  # Last column = Spanish in EN→ES files
            else:
                text = line.strip()

            if not text:
                continue

            tokens = tokenise(text)
            if not tokens:
                continue

            total_lines += 1
            scenario = classify_line(tokens, SCENARIO_SEEDS)

            if scenario:
                matched_lines += 1
                scenario_line_counts[scenario] += 1
                scenario_counters[scenario].update(tokens)

            if (i + 1) % 500_000 == 0:
                print(f"  Processed {i+1:,} lines... ({matched_lines:,} matched)")

    print(f"\n✅ Done!")
    print(f"   Total lines processed : {total_lines:,}")
    print(f"   Lines matched to scenario: {matched_lines:,} ({100*matched_lines/max(total_lines,1):.1f}%)")
    print()

    # Compute per-100k normalised frequencies
    results = {}
    for scenario, counter in scenario_counters.items():
        total_tokens = sum(counter.values())
        if total_tokens == 0:
            continue
        print(f"  {scenario}: {scenario_line_counts[scenario]:,} lines · {total_tokens:,} tokens")
        top20 = counter.most_common(20)
        results[scenario] = {
            word: round((count / total_tokens) * 100_000)
            for word, count in top20
        }

    return results

def print_corpus_data_output(results: dict):
    """Print the results formatted for direct paste into corpus_data.py."""
    print("\n" + "="*60)
    print("PASTE THIS INTO corpus_data.py → CORPUS_FREQUENCIES")
    print("="*60 + "\n")
    print("CORPUS_FREQUENCIES = {")
    for scenario, freqs in results.items():
        print(f'    "{scenario}": {{')
        items = list(freqs.items())
        for j, (word, freq) in enumerate(items):
            comma = "," if j < len(items) - 1 else ""
            print(f'        "{word}": {freq}{comma}')
        print("    },")
    print("}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python process_corpus.py path/to/es.txt")
        print("\nThis script processes the OpenSubtitles Spanish corpus")
        print("and outputs real word frequencies for ConvoReady.\n")
        print("Download the full corpus from:")
        print("  https://opus.nlpl.eu/OpenSubtitles/corpus/version/OpenSubtitles")
        sys.exit(1)

    filepath = sys.argv[1]
    results = process_corpus(filepath)
    print_corpus_data_output(results)
