import streamlit as st
import plotly.graph_objects as go
import re
import sys
import os

# ── Import corpus data and user model (same directory) ─────────────────────
sys.path.insert(0, os.path.dirname(__file__))
from corpus_data import get_corpus_frequencies
from user_model import (
    record_session,
    get_strengths_and_weaknesses,
    get_recommended_focus,
    get_predicted_readiness,
    get_session_count,
    get_scenario_history,
    clear_profile,
)
from llm_generator import (
    generate_phrases,
    generate_dialogue,
    generate_smart_recommendation,
)

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ConvoReady",
    page_icon="🇪🇸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
#  CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Single font: Nunito (Duolingo-style rounded, friendly) ── */
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');

html, body, [class*="css"], .stTextArea textarea, .stSelectbox, button {
    font-family: 'Nunito', sans-serif !important;
}

/* ── Duolingo dark theme colours ── */
/* Background: #111827 (dark blue-black like Duo dark mode)   */
/* Cards:      #1f2937                                         */
/* Accent:     #58CC02 (Duolingo green)                       */
/* Secondary:  #1CB0F6 (Duolingo blue)                        */
/* Border:     #374151                                         */

/* Hide the ugly white Streamlit header bar */
header[data-testid="stHeader"] { display: none !important; }
#MainMenu { display: none !important; }
footer { display: none !important; }
.stDeployButton { display: none !important; }

.stApp { background-color: #111827; color: #f9fafb; }

[data-testid="stSidebar"] { background-color: #1f2937; border-right: 1px solid #374151; }
[data-testid="stSidebar"] * { color: #f9fafb !important; }

/* Sidebar selectbox — dark text so it's readable in white box */
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] div {
    color: #111827 !important;
    font-weight: 700 !important;
}
[data-testid="stSidebar"] input { color: #111827 !important; }

/* ── Hero ── */
.hero-title { font-size: 3.2rem; font-weight: 900; color: #f9fafb; line-height: 1.1; margin-bottom: 0.3rem; }
.hero-accent { color: #58CC02; }
.hero-subtitle { font-size: 1.05rem; color: #9ca3af; font-weight: 400; margin-bottom: 1.5rem; }

/* ── Stat cards ── */
.stat-card { background: #1f2937; border: 2px solid #374151; border-radius: 16px; padding: 1.2rem 1.5rem; text-align: center; }
.stat-number { font-size: 2.2rem; color: #58CC02; font-weight: 900; }
.stat-label { font-size: 0.78rem; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600; }

/* ── Phrase cards ── */
.phrase-card { background: #1f2937; border: 2px solid #374151; border-radius: 16px; padding: 1rem 1.4rem; margin-bottom: 0.8rem; transition: border-color 0.2s; }
.phrase-card:hover { border-color: #58CC0255; }
.phrase-spanish { font-size: 1.1rem; font-weight: 800; color: #f9fafb; margin-bottom: 0.2rem; }
.phrase-english { font-size: 0.88rem; color: #9ca3af; margin-bottom: 0.25rem; font-weight: 400; }
.phrase-tip { font-size: 0.82rem; color: #58CC02; font-weight: 600; }
.phrase-meta { font-size: 0.72rem; color: #4b5563; margin-top: 0.3rem; }

/* ── Level pills ── */
.level-pill {
    display: inline-block;
    border-radius: 20px;
    padding: 0.1rem 0.55rem;
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.05em;
    margin-right: 0.3rem;
}
.level-A1 { background: #58CC0222; color: #58CC02; border: 1px solid #58CC0244; }
.level-A2 { background: #1CB0F622; color: #1CB0F6; border: 1px solid #1CB0F644; }
.level-B1 { background: #FF9F1C22; color: #FF9F1C; border: 1px solid #FF9F1C44; }

/* ── Dialogue ── */
.dialogue-line { background: #1f2937; border-left: 3px solid #374151; border-radius: 0 12px 12px 0; padding: 0.9rem 1.2rem; margin-bottom: 0.6rem; }
.dialogue-speaker { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: #58CC02; margin-bottom: 0.2rem; font-weight: 800; }
.dialogue-spanish { font-size: 1.05rem; font-weight: 700; color: #f9fafb; }
.dialogue-english { font-size: 0.85rem; color: #9ca3af; margin-top: 0.2rem; font-weight: 400; }

/* ── Section headers ── */
.section-header { font-size: 1.6rem; font-weight: 800; color: #f9fafb; margin-bottom: 0.3rem; }
.section-sub { font-size: 0.9rem; color: #9ca3af; margin-bottom: 1.5rem; font-weight: 400; }

/* ── Readiness ── */
.readiness-container { background: #1f2937; border: 2px solid #374151; border-radius: 16px; padding: 2rem; text-align: center; margin-bottom: 1.5rem; }
.readiness-score { font-size: 4rem; color: #58CC02; font-weight: 900; }
.readiness-label { font-size: 0.9rem; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.1em; font-weight: 700; }

/* ── Kit cards ── */
.kit-card { background: linear-gradient(135deg, #1a2e1a 0%, #1f2937 100%); border: 2px solid #58CC0233; border-radius: 16px; padding: 1rem 1.4rem; margin-bottom: 0.7rem; }
.kit-spanish { font-size: 1.1rem; font-weight: 800; color: #f9fafb; }
.kit-english { font-size: 0.88rem; color: #9ca3af; margin-top: 0.15rem; }
.kit-tip { font-size: 0.82rem; color: #58CC02; margin-top: 0.2rem; font-weight: 600; }

/* ── Badges & tags ── */
.badge { display: inline-block; background: #58CC0222; color: #58CC02; border: 1px solid #58CC0244; border-radius: 20px; padding: 0.2rem 0.8rem; font-size: 0.78rem; margin: 0.15rem; font-weight: 700; }
.tag-detected { display: inline-block; background: #1CB0F622; color: #1CB0F6; border: 1px solid #1CB0F644; border-radius: 20px; padding: 0.15rem 0.6rem; font-size: 0.75rem; margin: 0.15rem; font-weight: 600; }

/* ── Scenario box ── */
.scenario-box { background: #1f2937; border: 2px solid #58CC0244; border-radius: 16px; padding: 1rem 1.4rem; margin-bottom: 1.2rem; }
.scenario-box-label { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.1em; color: #58CC02; margin-bottom: 0.4rem; font-weight: 800; }

/* ── Corpus badge ── */
.corpus-badge { background: #1a2e1a; border: 1px solid #1CB0F644; border-radius: 8px; padding: 0.4rem 0.8rem; font-size: 0.75rem; color: #1CB0F6; display: inline-block; margin-bottom: 0.8rem; font-weight: 600; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { gap: 0.5rem; background: transparent; border-bottom: 1px solid #374151; }
.stTabs [data-baseweb="tab"] { background: transparent; color: #9ca3af; border-radius: 8px 8px 0 0; font-size: 0.9rem; font-weight: 700; }
.stTabs [aria-selected="true"] { background: #1f2937 !important; color: #f9fafb !important; border-bottom: 3px solid #58CC02 !important; }
.stProgress > div > div { background: #58CC02 !important; }
hr { border-color: #374151; }

/* ── Text area ── */
.stTextArea textarea { background: #1f2937 !important; border: 2px solid #374151 !important; color: #f9fafb !important; border-radius: 12px !important; font-weight: 600 !important; }
.stTextArea textarea:focus { border-color: #58CC02 !important; }
.stTextArea textarea::placeholder { color: #6b7280 !important; }

/* ── Buttons ── */
.stButton > button {
    font-weight: 800 !important;
    border-radius: 12px !important;
    background-color: #1f2937 !important;
    color: #f9fafb !important;
    border: 2px solid #374151 !important;
    font-family: Nunito, sans-serif !important;
}
.stButton > button:hover {
    background-color: #58CC02 !important;
    color: #111827 !important;
    border-color: #58CC02 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Level definitions ────────────────────────────────────────────────────────

LEVEL_INFO = {
    "A1 — Beginner":      {"code": "A1", "desc": "Basic greetings and numbers. Real conversations feel overwhelming.", "vocab": "Est. vocabulary: 300 words",   "known_vocab": 300,   "color": "#58CC02"},
    "A2 — Elementary":    {"code": "A2", "desc": "Can handle simple transactions. Struggles with fast speech.",        "vocab": "Est. vocabulary: 1,000 words", "known_vocab": 1000,  "color": "#1CB0F6"},
    "B1 — Intermediate":  {"code": "B1", "desc": "Can navigate most everyday situations with some effort.",            "vocab": "Est. vocabulary: 2,000 words", "known_vocab": 2000,  "color": "#FF9F1C"},
}

SCENARIO_LABELS = {
    "restaurant": "🍽️ Restaurant", "transport": "🚕 Transport",
    "shopping":   "🛍️ Shopping",   "hotel":     "🏨 Hotel",
    "health":     "🏥 Health",     "work":      "💼 Work",
    "social":     "🎉 Social",     "housing":   "🏠 Housing",
    "general":    "🌍 General",
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

MODEL_PATTERN_LABELS = PATTERN_LABELS

# ── TF-IDF scenario profiles ────────────────────────────────────────────────
# Each scenario profile is a rich bag of words drawn from phrases, dialogues,
# and keywords. The vectoriser learns what language belongs to each scenario
# and matches user input via cosine similarity — no keyword lists needed.

SCENARIO_PROFILES = {
    "restaurant": """
        mesa comer cuenta agua carta vino hambre café comida cena pedido pedir
        desayuno cocina cerveza carne camarero restaurante menú reserva tapas
        mesa para dos por favor trae carta recomienda pedir cuenta bebida
        eat food dinner lunch breakfast cafe bar cook cuisine burger pizza
        milkshake shake coffee sandwich juice ice cream dessert pastry bakery
        snack takeaway fast food soda smoothie chicken fish steak soup salad
        table for two bring the menu what do you recommend i want to order
        could you bring the bill do you accept card is service included
        grab a bite starving somewhere to eat book a table tonight hungry
    """,
    "transport": """
        tren viaje calle dirección taxi avión izquierda derecha estación salida
        equipaje esquina mapa billete vuelo autobús llegada conductor parada
        bus station airport directions lost route ticket ride drive uber tram
        straight ahead turn right how much does it cost stop here how long
        where is the stop keep the change accept card far take me to address
        getting a cab going to airport catching a train taking the bus metro
        subway navigate aeropuerto autobus coach ferry port platform
    """,
    "shopping": """
        dinero ropa vestido pagar comprar cambio tienda caja zapatos precio
        color camisa centro oferta marca talla caro barato probador devolución
        shop store buy purchase clothes size market mall souvenir gift sale
        discount fitting return exchange looking for a gift buying clothes
        how much does this cost do you have my size can i try it on
        i will take it do you accept returns where is the checkout
        need a different size another color gift wrap receipt refund
        salon beauty hair eyebrows nails threading waxing haircut hairdresser
        peluquería cejas uñas depilación hilo corte pelo tinte manicura
        beautician stylist barber blow dry trim highlights treatment spa
        how much is a cut keep the same shape a little shorter same style
        just a trim keep the shape make them neat tidy up clean up
        asking price beauty treatment grooming appointment book a time
    """,
    "hotel": """
        noche habitación cama hotel servicio llave doble piso baño maleta
        recepción pasaporte desayuno toalla ducha wifi equipaje ascensor
        accommodation room stay check in check out booking reservation bed
        breakfast key reception airbnb luggage towel hostel
        i have a reservation what time is breakfast is there wifi
        the key doesnt work can you store my luggage what time is checkout
        need more towels air conditioning doesnt work wake me up
    """,
    "health": """
        seguro doctor cabeza sangre médico enfermo hospital dolor cita
        enfermera fiebre medicina estómago herida farmacia receta alergia
        sick pain hurt appointment ill injury emergency prescription clinic
        pharmacy medicine fever symptom allergy feeling unwell
        i need a doctor my head hurts i have a fever i am allergic
        where is the nearest pharmacy i need a prescription health insurance
        been sick for two days need an appointment ache nausea cough
    """,
    "work": """
        trabajo jefe oficina negocio cargo contrato reunión equipo informe
        experiencia cliente departamento empresa sueldo entrevista candidato
        job interview office colleague meeting boss salary hire career
        profession business company cv resume internship
        my name is i have experience my strengths i would like to work here
        i work well in a team what would my role be training opportunities
        when can i start what are the working hours do you have questions
        apply for a job professional presentation deadline project
    """,
    "social": """
        hablar amigo chica chico fiesta música número teléfono bailar copa
        beber novia club plan conocer contigo salir quedar pareja invitar
        friend date party bar meet conversation introduce chat hang out
        weekend invite relationship dating romance flirt
        hi my name is where are you from what do you do want to grab a drink
        what are your plans nice to meet you can i buy you a drink
        do you have whatsapp shall we exchange numbers how long in spain
        making friends getting to know people first date night out
    """,
    "housing": """
        casa luz ruido salón dormitorio alquiler casero piso contrato reparar
        calefacción ducha fontanero avería fianza vecino grifo tubería
        landlord flat apartment rent lease tenant repair broken deposit
        contract neighbour noise heat heater water electric boiler plumber
        shower filter install pipe leak tap drain bathroom kitchen sink
        electrician fix maintenance wall floor ceiling window door lock
        there is a problem with the heating the tap is broken
        when can you send someone to fix it been without hot water
        is water included in the rent need a copy of the contract
        calling a plumber neighbours making noise return my deposit
    """,
}

# Build TF-IDF matrix at import time (fast — runs once on startup)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

_scenario_names = list(SCENARIO_PROFILES.keys())
_vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)
_scenario_matrix = _vectorizer.fit_transform([SCENARIO_PROFILES[s] for s in _scenario_names])

def detect_scenarios(user_text: str) -> list:
    """
    Match user text against scenario profiles using TF-IDF cosine similarity.
    Returns ranked list of scenario keys. Falls back to [general] if no match.
    """
    user_vec = _vectorizer.transform([user_text.lower()])
    similarities = cosine_similarity(user_vec, _scenario_matrix)[0]
    ranked = [
        (name, score)
        for name, score in zip(_scenario_names, similarities)
        if score > 0.02  # minimum similarity threshold
    ]
    ranked.sort(key=lambda x: x[1], reverse=True)
    return [name for name, _ in ranked] if ranked else ["general"]

def get_match_confidence(user_text: str, matched_keys: list) -> dict:
    """Return 0–100 cosine similarity scores per matched scenario."""
    user_vec = _vectorizer.transform([user_text.lower()])
    similarities = cosine_similarity(user_vec, _scenario_matrix)[0]
    score_map = dict(zip(_scenario_names, similarities))
    return {
        key: min(100, int(score_map.get(key, 0) * 200))
        for key in matched_keys
    }

def build_scenario_data(matched_keys: list, user_level_code: str,
                        user_text: str = "") -> dict:
    primary_key = matched_keys[0] if matched_keys and matched_keys != ["general"] else "general"

    # LLM-generated content — fallbacks are minimal emergency phrases
    fallback_phrases  = [{"es": "Por favor, ¿puede ayudarme?", "en": "Please, can you help me?", "tip": "💡 Universal phrase when all else fails.", "level": "A1", "pattern": "polite_request"}]
    fallback_dialogue = [
        {"speaker": "Local",  "es": "¡Hola! ¿En qué puedo ayudarle?", "en": "Hello! How can I help you?"},
        {"speaker": "You",    "es": "Hola, necesito ayuda, por favor.", "en": "Hello, I need help, please."},
    ]

    with st.spinner("✨ Generating personalised phrases with AI..."):
        phrases = generate_phrases(
            user_scenario      = user_text,
            scenario_category  = primary_key,
            level_code         = user_level_code,
            fallback_phrases   = fallback_phrases,
        )

    with st.spinner("✨ Building your practice dialogue..."):
        dialogue = generate_dialogue(
            user_scenario      = user_text,
            scenario_category  = primary_key,
            level_code         = user_level_code,
            fallback_dialogue  = fallback_dialogue,
        )

    return {"phrases": phrases, "dialogue": dialogue,
            "primary_key": primary_key}

def extract_keywords(user_text: str) -> list:
    stopwords = {"i", "a", "the", "to", "in", "at", "my", "me", "and", "for", "with",
                 "of", "on", "is", "it", "an", "want", "need", "going", "will", "be",
                 "have", "about", "that", "this", "how", "would", "can", "when", "do"}
    words = re.findall(r'\b[a-z]{3,}\b', user_text.lower())
    return [w for w in words if w not in stopwords][:8]

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
if "confidence" not in st.session_state:
    st.session_state.confidence = {}
if "scenario_text" not in st.session_state:
    st.session_state.scenario_text = ""
if "scenario_submitted" not in st.session_state:
    st.session_state.scenario_submitted = False

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:1rem 0 0.8rem 0;'>
        <div style='display:flex;align-items:center;gap:0.6rem;margin-bottom:0.3rem;'>
            <svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="18" cy="18" r="18" fill="#58CC02"/>
                <ellipse cx="14" cy="16" rx="3.5" ry="4" fill="white"/>
                <ellipse cx="22" cy="16" rx="3.5" ry="4" fill="white"/>
                <circle cx="14" cy="16" r="2" fill="#1f2937"/>
                <circle cx="22" cy="16" r="2" fill="#1f2937"/>
                <ellipse cx="18" cy="22" rx="4" ry="2.5" fill="#FF9F1C"/>
                <path d="M16 21.5 Q18 24 20 21.5" stroke="#1f2937" stroke-width="0.5" fill="none"/>
            </svg>
            <div>
                <div style='font-family:Nunito,sans-serif;font-size:1.5rem;font-weight:900;color:#f9fafb;line-height:1;'>ConvoReady</div>
                <div style='font-size:0.7rem;color:#58CC02;font-weight:700;letter-spacing:0.05em;'>POWERED BY DUOLINGO DATA</div>
            </div>
        </div>
        <div style='font-size:0.78rem;color:#9ca3af;font-weight:400;'>Spanish Conversation Trainer</div>
    </div>
    <hr style='border-color:#374151;margin:0.8rem 0;'>
    """, unsafe_allow_html=True)

    st.markdown("<div style='font-size:0.75rem;color:#9ca3af;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.4rem;'>Your Level</div>", unsafe_allow_html=True)
    level = st.selectbox("level", list(LEVEL_INFO.keys()), label_visibility="collapsed")
    level_data      = LEVEL_INFO[level]
    user_level_code = level_data["code"]

    # Detect level change → reset confidence so adaptive content refreshes visibly
    if st.session_state.get("last_level") != user_level_code:
        st.session_state["last_level"] = user_level_code
        st.session_state.confidence = {}
        if st.session_state.get("scenario_submitted"):
            st.rerun()

    st.markdown("<hr style='border-color:#374151;margin:1.2rem 0;'>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background:#111827;border:1px solid #374151;border-radius:10px;padding:1rem;'>
        <div style='font-size:0.75rem;color:#9ca3af;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.5rem;'>Your Profile</div>
        <div style='font-size:0.85rem;color:#f9fafb;margin-bottom:0.5rem;'>{level_data["desc"]}</div>
        <div style='font-size:0.75rem;color:#9ca3af;'>Est. vocabulary: <span style='color:{level_data["color"]};'>{level_data["known_vocab"]:,} words</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#374151;margin:1.2rem 0;'>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.75rem;color:#9ca3af;margin-bottom:0.6rem;'>💡 Example scenarios:</div>", unsafe_allow_html=True)
    examples = [
        "Complain to landlord about broken heater",
        "First date at a tapas bar",
        "Buying clothes, asking about sizes",
        "Feeling sick, need a pharmacy",
        "Taxi from the airport",
        "Job interview at a Spanish company",
    ]
    for ex in examples:
        if st.button(f"→ {ex}", key=f"ex_{ex}", use_container_width=True):
            st.session_state.scenario_text = ex
            st.session_state.scenario_submitted = True
            st.session_state.confidence = {}
            st.rerun()

    st.markdown("<hr style='border-color:#374151;margin:1.2rem 0;'>", unsafe_allow_html=True)
    if st.button("🔄 New Scenario", use_container_width=True):
        st.session_state.confidence = {}
        st.session_state.scenario_text = ""
        st.session_state.scenario_submitted = False
        st.rerun()

    # ── Learning Profile sidebar widget ──────────────────────────────────────
    session_count = get_session_count()
    if session_count > 0:
        st.markdown("<hr style='border-color:#374151;margin:1.2rem 0;'>", unsafe_allow_html=True)
        strengths, weaknesses = get_strengths_and_weaknesses()
        st.markdown(f"""
        <div style='background:#111827;border:1px solid #374151;border-radius:12px;padding:1rem;'>
            <div style='font-size:0.7rem;color:#58CC02;text-transform:uppercase;letter-spacing:0.1em;font-weight:800;margin-bottom:0.6rem;'>
                📊 Your Learning Profile
            </div>
            <div style='font-size:0.75rem;color:#9ca3af;margin-bottom:0.7rem;'>{session_count} session{'s' if session_count != 1 else ''} completed</div>
        """, unsafe_allow_html=True)

        if strengths:
            st.markdown("<div style='font-size:0.72rem;color:#58CC02;font-weight:700;margin-bottom:0.3rem;'>💪 Strengths</div>", unsafe_allow_html=True)
            for s in strengths[:2]:
                st.markdown(f"<div style='font-size:0.72rem;color:#f9fafb;margin-bottom:0.2rem;'>✅ {s['label']} — {int(s['rate']*100)}%</div>", unsafe_allow_html=True)

        if weaknesses:
            st.markdown("<div style='font-size:0.72rem;color:#FF9F1C;font-weight:700;margin:0.5rem 0 0.3rem 0;'>⚠️ Needs work</div>", unsafe_allow_html=True)
            for w in weaknesses[:2]:
                st.markdown(f"<div style='font-size:0.72rem;color:#f9fafb;margin-bottom:0.2rem;'>❌ {w['label']} — {int(w['rate']*100)}%</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("🗑️ Reset Profile", use_container_width=True):
            clear_profile()
            st.rerun()

# ─────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────
st.markdown("""
<div style='margin-bottom:1.5rem;'>
    <div class='hero-title'>Real Spanish.<br><span class='hero-accent'>Real Conversations.</span></div>
    <div class='hero-subtitle'>Describe any situation in your own words — we'll match it to real corpus data and build your personalised kit.</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='section-header' style='font-size:1.3rem;'>What's your situation?</div>", unsafe_allow_html=True)
st.markdown("<div class='section-sub'>Describe what you need to do in Spanish. The more detail, the better the match.</div>", unsafe_allow_html=True)

user_input = st.text_area(
    "scenario_input",
    value=st.session_state.scenario_text,
    placeholder="e.g. 'I need to tell my landlord the heater is broken' or 'First date at a tapas bar tonight'...",
    height=90,
    label_visibility="collapsed"
)

if st.button("✨ Analyse my scenario", use_container_width=True):
    if user_input.strip():
        st.session_state.scenario_text = user_input
        st.session_state.scenario_submitted = True
        st.session_state.confidence = {}
        st.rerun()

# ─────────────────────────────────────────────
#  RESULTS
# ─────────────────────────────────────────────
if st.session_state.scenario_submitted and st.session_state.scenario_text.strip():
    user_text       = st.session_state.scenario_text
    matched_keys    = detect_scenarios(user_text)
    confidences     = get_match_confidence(user_text, matched_keys)
    scenario_data   = build_scenario_data(matched_keys, user_level_code, user_text)
    detected_words  = extract_keywords(user_text)
    primary_key     = scenario_data["primary_key"]

    st.markdown("<hr style='border-color:#374151;margin:1.5rem 0;'>", unsafe_allow_html=True)

    # Scenario detected card with confidence scores
    badges = "".join([
        f'<span class="badge">{SCENARIO_LABELS.get(k,k)} <span style="opacity:0.7;font-size:0.7rem;">{confidences.get(k,0)}% match</span></span>'
        for k in matched_keys[:2]
    ])
    tags = "".join([f'<span class="tag-detected">{w}</span>' for w in detected_words])
    level_pill = f'<span class="level-pill level-{user_level_code}">{user_level_code}</span>'

    st.markdown(f"""
    <div class='scenario-box'>
        <div class='scenario-box-label'>📍 Analysed scenario — adapted for {level_pill}</div>
        <div style='font-style:italic;color:#9ca3af;margin-bottom:0.6rem;'>"{user_text}"</div>
        <div>{badges}</div>
        <div style='margin-top:0.5rem;'>{tags}</div>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    dialogue        = scenario_data["dialogue"]
    total_lines     = len(dialogue)
    you_lines       = [l for l in dialogue if l["speaker"] == "You"]
    reviewed        = len(st.session_state.confidence)
    confident_count = sum(1 for v in st.session_state.confidence.values() if v == "✅")
    readiness       = int((confident_count / len(you_lines)) * 100) if you_lines else 0
    r_color         = "#FF9F1C" if readiness >= 70 else "#58CC02" if readiness >= 40 else "#e87c7c"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{len(scenario_data["phrases"])}</div><div class="stat-label">Phrases for {user_level_code}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{total_lines}</div><div class="stat-label">Dialogue Lines</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{len(you_lines)}</div><div class="stat-label">Your Lines</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="stat-card"><div class="stat-number" style="color:{r_color};">{readiness}%</div><div class="stat-label">Readiness</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📊 Scenario Analysis", "🗣️ Practice Dialogue", "🎯 My Survival Kit"])

    # ── TAB 1 ──────────────────────────────────
    with tab1:
        col_l, col_r = st.columns([1.2, 1], gap="large")

        with col_l:
            st.markdown("<div class='section-header'>Corpus Analysis</div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class='corpus-badge'>
                📚 Data source: OpenSubtitles ES corpus · ~1.2M subtitle lines · frequencies per 100k words
            </div>
            """, unsafe_allow_html=True)

            corpus_freqs = get_corpus_frequencies(primary_key)
            top_words    = dict(list(corpus_freqs.items())[:12])

            fig_corpus = go.Figure(go.Bar(
                x=list(top_words.keys()),
                y=list(top_words.values()),
                marker=dict(
                    color=list(top_words.values()),
                    colorscale=[[0, '#1a2e1a'], [1, '#1CB0F6']],
                    showscale=False,
                    line=dict(color='#374151', width=1)
                ),
                hovertemplate='<b>%{x}</b><br>%{y} per 100k words<extra></extra>',
            ))
            fig_corpus.update_layout(
                title=dict(text=f"Most frequent words in real '{SCENARIO_LABELS.get(primary_key,'').split(' ')[-1]}' conversations", font=dict(color='#9ca3af', size=12)),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#f9fafb', family='DM Sans'),
                xaxis=dict(showgrid=False, tickangle=-35, tickfont=dict(size=11)),
                yaxis=dict(showgrid=True, gridcolor='#374151', showticklabels=True,
                           title=dict(text='freq / 100k words', font=dict(size=10, color='#9ca3af'))),
                margin=dict(l=10, r=10, t=50, b=70), height=280,
            )
            st.plotly_chart(fig_corpus, use_container_width=True)

            # Grammar pattern breakdown for this level
            level_patterns = {
                "A1": {"Present tense": 55, "Basic questions": 30, "Greetings": 15},
                "A2": {"Present tense": 42, "Basic questions": 25, "Polite requests": 20, "Past tense": 13},
                "B1": {"Present tense": 32, "Questions": 18, "Polite requests": 18, "Past tense": 15, "Conditional": 10, "Future": 7},
            }
            gp = level_patterns[user_level_code]
            fig_g = go.Figure(go.Bar(
                x=list(gp.values()), y=list(gp.keys()), orientation='h',
                marker=dict(color=list(gp.values()), colorscale=[[0,'#374151'],[1,'#58CC02']], showscale=False),
                text=[f"{v}%" for v in gp.values()], textposition='outside',
                textfont=dict(color='#f9fafb', size=11),
                hovertemplate='%{y}: %{x}%<extra></extra>',
            ))
            fig_g.update_layout(
                title=dict(text=f"Grammar patterns you'll encounter at {user_level_code}", font=dict(color='#9ca3af', size=12)),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#f9fafb', family='DM Sans'),
                xaxis=dict(showgrid=False, showticklabels=False, range=[0, max(gp.values())*1.35]),
                yaxis=dict(showgrid=False, tickfont=dict(size=11)),
                margin=dict(l=0, r=50, t=50, b=10), height=220,
            )
            st.plotly_chart(fig_g, use_container_width=True)

        with col_r:
            st.markdown("<div class='section-header'>Survival Phrases</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='section-sub'>Filtered and ranked for <strong style='color:#f9fafb;'>{level}</strong></div>", unsafe_allow_html=True)

            for phrase in scenario_data["phrases"]:
                plevel   = phrase.get('level', 'A1')
                ppattern = PATTERN_LABELS.get(phrase.get('pattern', 'present_simple'), 'Present tense')
                st.markdown(f"""
                <div class='phrase-card'>
                    <div class='phrase-spanish'>{phrase["es"]}</div>
                    <div class='phrase-english'>{phrase["en"]}</div>
                    <div class='phrase-tip'>{phrase["tip"]}</div>
                    <div class='phrase-meta'>
                        <span class='level-pill level-{plevel}'>{plevel}</span>
                        <span style='color:#4a5568;font-size:0.7rem;'>{ppattern}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── TAB 2 ──────────────────────────────────
    with tab2:
        st.markdown("<div class='section-header'>Practice Dialogue</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='section-sub'>A real {user_level_code}-level conversation — mark your honest confidence on each line you'd need to say.</div>", unsafe_allow_html=True)

        if reviewed > 0:
            st.progress(reviewed / len(you_lines))
            st.markdown(f"<div style='font-size:0.8rem;color:#9ca3af;margin-bottom:1rem;'>{reviewed} of {len(you_lines)} your lines reviewed — {confident_count} confident</div>", unsafe_allow_html=True)

        col_d, col_c = st.columns([1.6, 1], gap="large")

        with col_d:
            you_idx = 0
            for i, line in enumerate(dialogue):
                is_you = line["speaker"] == "You"
                bc = "#58CC02" if is_you else "#374151"
                st.markdown(f"""
                <div class='dialogue-line' style='border-left-color:{bc};'>
                    <div class='dialogue-speaker'>{"🧑 You" if is_you else "💬 " + line["speaker"]}</div>
                    <div class='dialogue-spanish'>{line["es"]}</div>
                    <div class='dialogue-english'>{line["en"]}</div>
                </div>
                """, unsafe_allow_html=True)
                if is_you:
                    key = f"conf_{i}"
                    current = st.session_state.confidence.get(key)
                    cy, cn = st.columns(2)
                    with cy:
                        if st.button("✅ I know this", key=f"yes_{i}", use_container_width=True):
                            st.session_state.confidence[key] = "✅"
                            st.rerun()
                    with cn:
                        if st.button("❌ I'd struggle", key=f"no_{i}", use_container_width=True):
                            st.session_state.confidence[key] = "❌"
                            st.rerun()
                    if current:
                        cc = "#FF9F1C" if current == "✅" else "#e87c7c"
                        label = "I know this ✅" if current == "✅" else "I'd struggle ❌"
                        st.markdown(f"<div style='font-size:0.78rem;color:{cc};margin-bottom:0.5rem;padding-left:0.5rem;'>{label}</div>", unsafe_allow_html=True)
                    you_idx += 1

        with col_c:
            st.markdown(f"""
            <div style='background:#1f2937;border:1px solid #374151;border-radius:12px;padding:1.2rem;margin-bottom:1rem;'>
                <div style='font-size:0.75rem;color:#9ca3af;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.6rem;'>
                    {user_level_code} Dialogue
                </div>
                <div style='font-size:0.85rem;color:#f9fafb;line-height:1.7;'>
                    This dialogue is tailored to your <span style='color:{level_data["color"]};'>{user_level_code}</span> level —
                    {"shorter and simpler for beginners." if user_level_code == "A1" else
                     "a solid mid-length exchange." if user_level_code == "A2" else
                     "the full, natural-speed conversation."}
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class='readiness-container'>
                <div class='readiness-label'>Conversation Readiness</div>
                <div class='readiness-score' style='color:{r_color};'>{readiness}%</div>
                <div style='font-size:0.85rem;color:#9ca3af;margin-top:0.5rem;'>
                    {"🟢 You're ready!" if readiness >= 80 else "🟡 Getting there..." if readiness >= 50 else "🔴 Keep practicing"}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # TAB 3
    with tab3:
        st.markdown("<div class='section-header'>🎯 My Survival Kit</div>", unsafe_allow_html=True)

        struggled_keys    = [k for k, v in st.session_state.confidence.items() if v == "❌"]
        struggled_indices = [int(k.split("_")[-1]) for k in struggled_keys]
        struggled_lines   = [dialogue[i] for i in struggled_indices if i < len(dialogue)]

        if not st.session_state.confidence:
            predicted     = get_predicted_readiness(primary_key, user_level_code)
            session_count = get_session_count()
            if predicted is not None:
                pred_color = "#58CC02" if predicted >= 70 else "#FF9F1C" if predicted >= 40 else "#e87c7c"
                pred_word  = "straightforward" if predicted >= 70 else "moderately challenging" if predicted >= 40 else "quite challenging"
                st.markdown(f"""
                <div style='background:#1f2937;border:2px solid #374151;border-radius:16px;padding:1.5rem;margin-bottom:1.2rem;'>
                    <div style='font-size:0.72rem;color:#58CC02;text-transform:uppercase;letter-spacing:0.1em;font-weight:800;margin-bottom:0.6rem;'>
                        🤖 AI Prediction — based on {session_count} past sessions
                    </div>
                    <div style='display:flex;align-items:center;gap:1.5rem;'>
                        <div>
                            <div style='font-size:3rem;font-weight:900;color:{pred_color};line-height:1;'>{predicted}%</div>
                            <div style='font-size:0.8rem;color:#9ca3af;'>Predicted readiness</div>
                        </div>
                        <div style='flex:1;font-size:0.85rem;color:#f9fafb;line-height:1.6;'>
                            Based on your grammar history, we predict this scenario will be
                            <span style='color:{pred_color};font-weight:700;'>{pred_word}</span>.
                            Complete the Practice Dialogue to see how accurate this was.
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("""
            <div style='background:#1f2937;border:1px dashed #374151;border-radius:12px;padding:2.5rem;text-align:center;'>
                <div style='font-size:2rem;margin-bottom:0.8rem;'>🗣️</div>
                <div style='font-weight:900;font-size:1.2rem;color:#f9fafb;margin-bottom:0.5rem;'>Complete the Practice Dialogue first</div>
                <div style='font-size:0.9rem;color:#9ca3af;'>Go to the Practice Dialogue tab and mark your confidence on each line.</div>
            </div>
            """, unsafe_allow_html=True)

        else:
            # Record session once per scenario+level combination
            session_key = f"recorded_{hash(user_text)}_{user_level_code}"
            if not st.session_state.get(session_key):
                record_session(
                    scenario          = primary_key,
                    level             = user_level_code,
                    confidence_map    = st.session_state.confidence,
                    dialogue          = dialogue,
                    phrase_pattern_fn = lambda es: next(
                        (l.get("pattern", "present_simple") for l in dialogue if l["es"] == es),
                        "present_simple"
                    ),
                )
                st.session_state[session_key] = True

            strengths,   weaknesses   = get_strengths_and_weaknesses()
            predicted                  = get_predicted_readiness(primary_key, user_level_code)
            session_count              = get_session_count()
            fallback_rec               = get_recommended_focus()
            profile                    = __import__("user_model")._load_profile()
            with st.spinner("🤖 Generating personalised recommendation..."):
                recommendation = generate_smart_recommendation(
                    struggled_phrases = [{"es": l["es"], "en": l["en"]} for l in struggled_lines],
                    pattern_stats     = profile.get("pattern_stats", {}),
                    scenario          = primary_key,
                    level_code        = user_level_code,
                    fallback          = fallback_rec,
                )

            col_score, col_model = st.columns([1, 1], gap="large")

            with col_score:
                st.markdown(f"""
                <div class='readiness-container'>
                    <div class='readiness-label'>This Session</div>
                    <div class='readiness-score' style='color:{r_color};'>{readiness}%</div>
                    <div style='font-size:0.85rem;color:#9ca3af;margin-top:0.5rem;'>
                        {confident_count} confident · {len(struggled_lines)} to work on
                    </div>
                </div>
                """, unsafe_allow_html=True)
                fig_donut = go.Figure(go.Pie(
                    values=[max(readiness, 1), max(100 - readiness, 1)],
                    hole=0.72, marker=dict(colors=["#58CC02", "#1f2937"]),
                    textinfo="none", hoverinfo="skip",
                ))
                fig_donut.add_annotation(text=f"{readiness}%", x=0.5, y=0.5,
                    font=dict(size=28, color="#f9fafb", family="Nunito"), showarrow=False)
                fig_donut.update_layout(paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
                    margin=dict(l=20, r=20, t=20, b=20), height=200)
                st.plotly_chart(fig_donut, use_container_width=True)

            with col_model:
                from user_model import get_pattern_performance
                perf = get_pattern_performance()
                if perf and len(perf) >= 2:
                    labels = [v["label"] for v in perf.values()]
                    rates  = [int(v["rate"] * 100) for v in perf.values()]
                    colors = ["#58CC02" if r >= 70 else "#FF9F1C" if r >= 40 else "#e87c7c" for r in rates]
                    fig_hist = go.Figure(go.Bar(
                        x=rates, y=labels, orientation="h",
                        marker=dict(color=colors),
                        text=[f"{r}%" for r in rates], textposition="outside",
                        textfont=dict(color="#f9fafb", size=11),
                        hovertemplate="%{y}: %{x}%<extra></extra>",
                    ))
                    fig_hist.update_layout(
                        title=dict(text="Grammar Pattern History", font=dict(color="#9ca3af", size=12)),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#f9fafb", family="Nunito"),
                        xaxis=dict(showgrid=False, showticklabels=False, range=[0, 130]),
                        yaxis=dict(showgrid=False, tickfont=dict(size=11)),
                        margin=dict(l=0, r=50, t=40, b=10), height=240,
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)
                else:
                    st.markdown(f"""
                    <div style='background:#1f2937;border:1px solid #374151;border-radius:12px;
                                padding:1.2rem;text-align:center;margin-top:0.5rem;'>
                        <div style='font-size:1.5rem;margin-bottom:0.5rem;'>📊</div>
                        <div style='font-size:0.85rem;color:#9ca3af;'>Complete more sessions to<br>build your grammar profile</div>
                        <div style='font-size:0.75rem;color:#58CC02;margin-top:0.5rem;font-weight:700;'>
                            {session_count} session{"s" if session_count != 1 else ""} recorded so far
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # Personalised recommendation
            if recommendation:
                st.markdown(f"""
                <div style='background:linear-gradient(135deg,#1a2e1a,#1f2937);border:2px solid #58CC0244;
                            border-radius:16px;padding:1.2rem 1.5rem;margin:1rem 0;'>
                    <div style='font-size:0.72rem;color:#58CC02;text-transform:uppercase;
                                letter-spacing:0.1em;font-weight:800;margin-bottom:0.5rem;'>
                        🤖 Personalised Recommendation
                    </div>
                    <div style='font-size:0.9rem;color:#f9fafb;line-height:1.6;'>{recommendation}</div>
                </div>
                """, unsafe_allow_html=True)

            # Struggled phrases
            if struggled_lines:
                st.markdown("<hr style='border-color:#374151;margin:1.2rem 0;'>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-size:1rem;font-weight:800;color:#f9fafb;margin-bottom:0.8rem;'>⚠️ {len(struggled_lines)} phrases to focus on</div>", unsafe_allow_html=True)
                for line in struggled_lines:
                    pattern = PATTERN_LABELS.get(line.get('pattern', 'present_simple'), 'Present tense')
                    level_tag = line.get('level', 'A1')
                    st.markdown(f"""
                    <div class='kit-card' style='border-color:#e87c7c44;'>
                        <div style='display:flex;justify-content:space-between;align-items:flex-start;'>
                            <div>
                                <div class='kit-spanish'>{line["es"]}</div>
                                <div class='kit-english'>{line["en"]}</div>
                            </div>
                            <span class='level-pill level-{level_tag}' style='flex-shrink:0;margin-left:0.5rem;'>{level_tag}</span>
                        </div>
                        <div style='margin-top:0.5rem;font-size:0.75rem;color:#9ca3af;'>
                            Grammar pattern: <span style='color:#FF9F1C;font-weight:700;'>{pattern}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='background:#1a2e1a;border:2px solid #58CC0244;border-radius:12px;
                            padding:1.5rem;text-align:center;margin:1rem 0;'>
                    <div style='font-size:1.5rem;margin-bottom:0.5rem;'>🎉</div>
                    <div style='font-weight:900;color:#58CC02;font-size:1.1rem;'>You knew every line!</div>
                    <div style='font-size:0.85rem;color:#9ca3af;margin-top:0.3rem;'>Recorded in your learning profile.</div>
                </div>
                """, unsafe_allow_html=True)

            # Full phrase kit
            st.markdown("<hr style='border-color:#374151;margin:1.5rem 0;'>", unsafe_allow_html=True)
            st.markdown("<div class='section-header' style='font-size:1.2rem;'>Complete Phrase Kit</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='section-sub'>All {user_level_code}-appropriate phrases for this scenario</div>", unsafe_allow_html=True)

            cols = st.columns(2)
            for i, phrase in enumerate(scenario_data["phrases"]):
                plevel   = phrase.get('level', 'A1')
                ppattern = PATTERN_LABELS.get(phrase.get('pattern', 'present_simple'), 'Present tense')
                with cols[i % 2]:
                    st.markdown(f"""
                    <div class='kit-card'>
                        <div class='kit-spanish'>{phrase["es"]}</div>
                        <div class='kit-english'>{phrase["en"]}</div>
                        <div class='kit-tip'>{phrase["tip"]}</div>
                        <div class='phrase-meta' style='margin-top:0.4rem;'>
                            <span class='level-pill level-{plevel}'>{plevel}</span>
                            <span style='color:#4b5563;font-size:0.7rem;'>{ppattern}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            kit_text = f"ConvoReady — {user_level_code} Survival Kit\nScenario: {user_text}\n" + "="*50 + "\n\n"
            if struggled_lines:
                kit_text += "FOCUS PHRASES (you struggled with these):\n"
                for line in struggled_lines:
                    kit_text += f"  ES: {line['es']}\n  EN: {line['en']}\n  Pattern: {PATTERN_LABELS.get(line.get('pattern', 'present_simple'), 'Present tense')}\n\n"
                kit_text += "\nALL PHRASES:\n"
            for p in scenario_data["phrases"]:
                plevel   = p.get('level', 'A1')
                ppattern = PATTERN_LABELS.get(p.get('pattern', 'present_simple'), 'Present tense')
                kit_text += f"[{plevel} · {ppattern}]\nES: {p['es']}\nEN: {p['en']}\n{p['tip']}\n\n"

            st.download_button(
                label="📥 Download My Survival Kit",
                data=kit_text,
                file_name=f"convoready_{user_level_code}_kit.txt",
                mime="text/plain",
                use_container_width=True,
            )

else:
    st.markdown("""
    <div style='background:#1f2937;border:1px dashed #374151;border-radius:16px;padding:3rem;text-align:center;margin-top:1rem;'>
        <div style='font-size:3rem;margin-bottom:1rem;'>🇪🇸</div>
        <div style='font-family:Nunito,sans-serif;font-weight:900;font-size:1.4rem;color:#f9fafb;margin-bottom:0.8rem;'>Describe your situation above to get started</div>
        <div style='font-size:0.9rem;color:#9ca3af;max-width:420px;margin:0 auto;line-height:1.7;'>
            Tell us what you need to do in Spanish. We'll analyse it against real corpus data and build
            a personalised kit matched to your level.
        </div>
    </div>
    """, unsafe_allow_html=True)
