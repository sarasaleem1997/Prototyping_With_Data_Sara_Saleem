import streamlit as st
import plotly.graph_objects as go
import re
import sys
import os

# ── Import corpus data and user model (same directory) ─────────────────────
sys.path.insert(0, os.path.dirname(__file__))
from corpus_data import (
    get_corpus_frequencies,
    filter_phrases_by_level,
    get_dialogue_for_level,
    get_phrase_level,
    get_phrase_pattern,
    LEVEL_ORDER,
    PATTERN_LABELS,
)
from user_model import (
    record_session,
    get_strengths_and_weaknesses,
    get_recommended_focus,
    get_predicted_readiness,
    get_session_count,
    get_scenario_history,
    clear_profile,
    PATTERN_LABELS as MODEL_PATTERN_LABELS,
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

# ─────────────────────────────────────────────
#  KNOWLEDGE BASE
# ─────────────────────────────────────────────

KNOWLEDGE_BASE = {
    "restaurant": {
        "phrases": [
            {"es": "Una mesa para dos, por favor.", "en": "A table for two, please.", "tip": "💡 Always add 'por favor' — it goes a long way!"},
            {"es": "¿Me trae la carta, por favor?", "en": "Could you bring the menu, please?", "tip": "💡 'Carta' = menu in Spain. In Latin America say 'menú'."},
            {"es": "¿Qué recomienda?", "en": "What do you recommend?", "tip": "💡 Locals love this question — you'll get great tips."},
            {"es": "Voy a pedir...", "en": "I'm going to order...", "tip": "💡 The most natural way to place your order."},
            {"es": "¿Tiene algo sin gluten / vegetariano?", "en": "Do you have anything gluten-free / vegetarian?", "tip": "💡 Swap the last word for your dietary need."},
            {"es": "¿Me trae la cuenta, por favor?", "en": "Could you bring the bill, please?", "tip": "💡 More polite than just saying 'la cuenta'."},
            {"es": "Está muy rico, gracias.", "en": "It's delicious, thank you.", "tip": "💡 Complimenting the food makes you instantly likeable."},
            {"es": "¿Puede repetir más despacio?", "en": "Could you repeat that more slowly?", "tip": "💡 Your most important phrase as a beginner!"},
            {"es": "¿Aceptan tarjeta?", "en": "Do you accept card?", "tip": "💡 Spain is mostly card-friendly but always worth asking."},
            {"es": "¿Está incluido el servicio?", "en": "Is service included?", "tip": "💡 Tipping culture varies — always good to check."},
        ],
        "dialogues": {
            "A1": [
                {"speaker": "Waiter", "es": "¡Buenas tardes! ¿Mesa para cuántos?", "en": "Good afternoon! Table for how many?"},
                {"speaker": "You",   "es": "Para dos, por favor.", "en": "For two, please."},
                {"speaker": "Waiter", "es": "¿Qué quieren beber?", "en": "What would you like to drink?"},
                {"speaker": "You",   "es": "Agua, por favor. ¿Qué recomienda?", "en": "Water, please. What do you recommend?"},
                {"speaker": "Waiter", "es": "El pollo está muy bueno hoy.", "en": "The chicken is very good today."},
                {"speaker": "You",   "es": "Perfecto. Voy a pedir eso.", "en": "Perfect. I'll order that."},
            ],
            "A2": [
                {"speaker": "Waiter", "es": "¡Buenas tardes! ¿Tienen reserva?", "en": "Good afternoon! Do you have a reservation?"},
                {"speaker": "You",   "es": "No, no tenemos. ¿Tienen mesa libre?", "en": "No, we don't. Do you have a free table?"},
                {"speaker": "Waiter", "es": "Sí, claro. ¿Mesa para cuántas personas?", "en": "Yes, of course. Table for how many?"},
                {"speaker": "You",   "es": "Para dos. ¿Me trae la carta, por favor?", "en": "For two. Could you bring the menu, please?"},
                {"speaker": "Waiter", "es": "¿Qué quieren tomar de bebida?", "en": "What would you like to drink?"},
                {"speaker": "You",   "es": "Agua con gas. ¿Qué recomienda hoy?", "en": "Sparkling water. What do you recommend today?"},
                {"speaker": "Waiter", "es": "El pollo al ajillo está muy bueno.", "en": "The garlic chicken is very good."},
                {"speaker": "You",   "es": "Perfecto. Voy a pedir eso. ¿Aceptan tarjeta?", "en": "Perfect. I'll have that. Do you accept card?"},
            ],
            "B1": [
                {"speaker": "Waiter", "es": "¡Buenas tardes! ¿Tienen reserva?", "en": "Good afternoon! Do you have a reservation?"},
                {"speaker": "You",   "es": "No, no tenemos. ¿Tienen mesa libre?", "en": "No, we don't. Do you have a free table?"},
                {"speaker": "Waiter", "es": "Sí, claro. ¿Mesa para cuántas personas?", "en": "Yes, of course. Table for how many?"},
                {"speaker": "You",   "es": "Para dos, por favor.", "en": "For two, please."},
                {"speaker": "Waiter", "es": "¿Qué quieren tomar de bebida?", "en": "What would you like to drink?"},
                {"speaker": "You",   "es": "Agua con gas para mí. ¿Qué recomienda hoy?", "en": "Sparkling water for me. What do you recommend today?"},
                {"speaker": "Waiter", "es": "El pollo al ajillo está muy bueno.", "en": "The garlic chicken is very good."},
                {"speaker": "You",   "es": "Perfecto. Voy a pedir eso, gracias.", "en": "Perfect. I'll order that, thank you."},
                {"speaker": "Waiter", "es": "¿Algo más?", "en": "Anything else?"},
                {"speaker": "You",   "es": "No, gracias. ¿Me trae la cuenta cuando pueda?", "en": "No, thank you. Could you bring the bill when you can?"},
            ],
        },
    },
    "transport": {
        "phrases": [
            {"es": "¿Me lleva a esta dirección?", "en": "Can you take me to this address?", "tip": "💡 Show your phone with the address — works every time."},
            {"es": "¿Cuánto cuesta ir al centro?", "en": "How much does it cost to go to the center?", "tip": "💡 Always ask before getting in an unofficial taxi."},
            {"es": "Todo recto, luego a la derecha.", "en": "Straight ahead, then right.", "tip": "💡 Key words: derecha (right), izquierda (left), recto (straight)."},
            {"es": "Pare aquí, por favor.", "en": "Stop here, please.", "tip": "💡 Essential — say it early enough!"},
            {"es": "¿Cuánto tiempo tarda?", "en": "How long does it take?", "tip": "💡 Great for planning your journey."},
            {"es": "¿Dónde está la parada de metro / autobús?", "en": "Where is the metro / bus stop?", "tip": "💡 Swap 'metro' for 'autobús' or 'tren'."},
            {"es": "Un billete para..., por favor.", "en": "One ticket to..., please.", "tip": "💡 'Billete' = ticket in Spain. Latin America uses 'boleto'."},
            {"es": "¿Está lejos de aquí?", "en": "Is it far from here?", "tip": "💡 'Cerca' = near, 'lejos' = far."},
            {"es": "¿Acepta tarjeta?", "en": "Do you accept card?", "tip": "💡 Many taxis are still cash only in Spain."},
            {"es": "Quédese con el cambio.", "en": "Keep the change.", "tip": "💡 A classy way to tip your driver."},
        ],
        "dialogues": {
            "A1": [
                {"speaker": "You",    "es": "¡Hola! ¿Está libre?", "en": "Hi! Are you free?"},
                {"speaker": "Driver", "es": "Sí, ¿adónde va?", "en": "Yes, where are you going?"},
                {"speaker": "You",    "es": "Al aeropuerto, por favor.", "en": "To the airport, please."},
                {"speaker": "Driver", "es": "De acuerdo.", "en": "Alright."},
                {"speaker": "You",    "es": "¿Cuánto cuesta?", "en": "How much does it cost?"},
                {"speaker": "Driver", "es": "Unos treinta euros.", "en": "About thirty euros."},
            ],
            "A2": [
                {"speaker": "You",    "es": "¡Hola! ¿Está libre?", "en": "Hi! Are you free?"},
                {"speaker": "Driver", "es": "Sí, ¿adónde va?", "en": "Yes, where are you going?"},
                {"speaker": "You",    "es": "Al aeropuerto, por favor. ¿Cuánto cuesta?", "en": "To the airport, please. How much does it cost?"},
                {"speaker": "Driver", "es": "Unos treinta euros, depende del tráfico.", "en": "About thirty euros, depending on traffic."},
                {"speaker": "You",    "es": "¿Cuánto tiempo tarda?", "en": "How long does it take?"},
                {"speaker": "Driver", "es": "Unos cuarenta minutos.", "en": "About forty minutes."},
                {"speaker": "You",    "es": "Perfecto. ¿Acepta tarjeta?", "en": "Perfect. Do you accept card?"},
                {"speaker": "Driver", "es": "Sí, sin problema.", "en": "Yes, no problem."},
            ],
            "B1": [
                {"speaker": "You",    "es": "¡Hola! ¿Está libre?", "en": "Hi! Are you free?"},
                {"speaker": "Driver", "es": "Sí, ¿adónde va?", "en": "Yes, where are you going?"},
                {"speaker": "You",    "es": "Al aeropuerto, por favor. ¿Cuánto cuesta?", "en": "To the airport, please. How much does it cost?"},
                {"speaker": "Driver", "es": "Unos treinta euros, depende del tráfico.", "en": "About thirty euros, depending on traffic."},
                {"speaker": "You",    "es": "Bien. ¿Cuánto tiempo tarda?", "en": "OK. How long does it take?"},
                {"speaker": "Driver", "es": "Unos cuarenta minutos si no hay tráfico.", "en": "About forty minutes if there's no traffic."},
                {"speaker": "You",    "es": "Perfecto. ¿Acepta tarjeta?", "en": "Perfect. Do you accept card?"},
                {"speaker": "Driver", "es": "Sí, sin problema.", "en": "Yes, no problem."},
                {"speaker": "You",    "es": "Gracias. Puede dejarme en la entrada principal.", "en": "Thank you. You can drop me at the main entrance."},
                {"speaker": "Driver", "es": "¡Claro! Buen viaje.", "en": "Of course! Have a good trip."},
            ],
        },
    },
    "shopping": {
        "phrases": [
            {"es": "¿Cuánto cuesta esto?", "en": "How much does this cost?", "tip": "💡 The most universal shopping phrase."},
            {"es": "¿Tiene en talla M / grande / pequeña?", "en": "Do you have it in size M / large / small?", "tip": "💡 Sizes: XS, S, M, L, XL — same as English!"},
            {"es": "¿Me lo puedo probar?", "en": "Can I try it on?", "tip": "💡 'Los probadores' = the fitting rooms."},
            {"es": "¿Tiene en otro color?", "en": "Do you have it in another color?", "tip": "💡 Colors: rojo, azul, verde, negro, blanco, gris."},
            {"es": "Me lo llevo.", "en": "I'll take it.", "tip": "💡 The magic phrase when you've decided to buy."},
            {"es": "¿Está en oferta?", "en": "Is it on sale?", "tip": "💡 'Rebajas' = sales season (January & July in Spain)."},
            {"es": "¿Aceptan devoluciones?", "en": "Do you accept returns?", "tip": "💡 Always check the return policy!"},
            {"es": "Me queda bien / mal.", "en": "It fits well / doesn't fit.", "tip": "💡 'Grande' = too big, 'pequeño' = too small."},
            {"es": "¿Puede envolverlo para regalo?", "en": "Can you gift wrap it?", "tip": "💡 Many Spanish shops offer free gift wrapping."},
            {"es": "¿Dónde está la caja?", "en": "Where is the checkout?", "tip": "💡 'Caja' literally means 'box' but means checkout."},
        ],
        "dialogues": {
            "A1": [
                {"speaker": "You",   "es": "Hola, ¿cuánto cuesta esto?", "en": "Hi, how much does this cost?"},
                {"speaker": "Staff", "es": "Veintidós euros.", "en": "Twenty-two euros."},
                {"speaker": "You",   "es": "¿Tiene en talla M?", "en": "Do you have it in size M?"},
                {"speaker": "Staff", "es": "Sí, un momento.", "en": "Yes, one moment."},
                {"speaker": "You",   "es": "Me queda bien. Me lo llevo.", "en": "It fits well. I'll take it."},
                {"speaker": "Staff", "es": "¿En efectivo o tarjeta?", "en": "Cash or card?"},
            ],
            "A2": [
                {"speaker": "You",   "es": "Hola, ¿cuánto cuesta esta camiseta?", "en": "Hi, how much does this t-shirt cost?"},
                {"speaker": "Staff", "es": "Está a veintidós euros.", "en": "It's twenty-two euros."},
                {"speaker": "You",   "es": "¿Tiene en talla M y en azul?", "en": "Do you have it in size M and in blue?"},
                {"speaker": "Staff", "es": "Sí, un momento. ¿Se la quiere probar?", "en": "Yes, one moment. Would you like to try it on?"},
                {"speaker": "You",   "es": "Sí, por favor. ¿Dónde están los probadores?", "en": "Yes, please. Where are the fitting rooms?"},
                {"speaker": "Staff", "es": "Al fondo a la derecha.", "en": "At the back on the right."},
                {"speaker": "You",   "es": "Me queda bien. Me la llevo.", "en": "It fits well. I'll take it."},
                {"speaker": "Staff", "es": "¿Paga en efectivo o con tarjeta?", "en": "Are you paying cash or by card?"},
            ],
            "B1": [
                {"speaker": "You",   "es": "Hola, ¿cuánto cuesta esta camiseta?", "en": "Hi, how much does this t-shirt cost?"},
                {"speaker": "Staff", "es": "Está a veintidós euros.", "en": "It's twenty-two euros."},
                {"speaker": "You",   "es": "¿Tiene en talla M?", "en": "Do you have it in size M?"},
                {"speaker": "Staff", "es": "Sí, un momento. ¿De qué color la quiere?", "en": "Yes, one moment. What color would you like?"},
                {"speaker": "You",   "es": "En azul, por favor. ¿Me la puedo probar?", "en": "In blue, please. Can I try it on?"},
                {"speaker": "Staff", "es": "Claro, los probadores están al fondo.", "en": "Of course, the fitting rooms are at the back."},
                {"speaker": "You",   "es": "Me queda bien. Me la llevo.", "en": "It fits well. I'll take it."},
                {"speaker": "Staff", "es": "¿Paga en efectivo o con tarjeta?", "en": "Are you paying cash or by card?"},
                {"speaker": "You",   "es": "Con tarjeta, por favor. ¿Aceptan devoluciones?", "en": "By card, please. Do you accept returns?"},
                {"speaker": "Staff", "es": "Sí, con el ticket en los próximos treinta días.", "en": "Yes, with the receipt within thirty days."},
            ],
        },
    },
    "hotel": {
        "phrases": [
            {"es": "Tengo una reserva a nombre de...", "en": "I have a reservation under the name of...", "tip": "💡 Have your booking confirmation ready on your phone."},
            {"es": "¿A qué hora es el desayuno?", "en": "What time is breakfast?", "tip": "💡 In Spain, breakfast is usually 7–10am."},
            {"es": "¿Hay WiFi? ¿Cuál es la contraseña?", "en": "Is there WiFi? What's the password?", "tip": "💡 Two questions in one — very efficient!"},
            {"es": "El aire acondicionado no funciona.", "en": "The air conditioning doesn't work.", "tip": "💡 Swap for: calefacción (heating), ducha (shower), TV."},
            {"es": "¿Me puede cambiar de habitación?", "en": "Can you change my room?", "tip": "💡 Be polite but firm if there's a real problem."},
            {"es": "Necesito más toallas, por favor.", "en": "I need more towels, please.", "tip": "💡 Also: almohadas (pillows), mantas (blankets)."},
            {"es": "¿Pueden despertarme a las siete?", "en": "Can you wake me up at seven?", "tip": "💡 A classic hotel request."},
            {"es": "¿A qué hora es el check-out?", "en": "What time is check-out?", "tip": "💡 Usually noon in Spain."},
            {"es": "¿Puede guardarme el equipaje?", "en": "Can you store my luggage?", "tip": "💡 Great when check-out is before your flight."},
            {"es": "La llave no funciona.", "en": "The key doesn't work.", "tip": "💡 Very common with electronic key cards!"},
        ],
        "dialogues": {
            "A1": [
                {"speaker": "Receptionist", "es": "¡Buenas tardes! ¿En qué puedo ayudarle?", "en": "Good afternoon! How can I help you?"},
                {"speaker": "You",          "es": "Tengo una reserva. Me llamo García.", "en": "I have a reservation. My name is García."},
                {"speaker": "Receptionist", "es": "Perfecto. Su habitación es la 204.", "en": "Perfect. Your room is 204."},
                {"speaker": "You",          "es": "¿Hay WiFi?", "en": "Is there WiFi?"},
                {"speaker": "Receptionist", "es": "Sí, la contraseña está aquí.", "en": "Yes, the password is here."},
                {"speaker": "You",          "es": "Gracias. ¿A qué hora es el desayuno?", "en": "Thank you. What time is breakfast?"},
            ],
            "A2": [
                {"speaker": "Receptionist", "es": "¡Buenas tardes! ¿En qué puedo ayudarle?", "en": "Good afternoon! How can I help you?"},
                {"speaker": "You",          "es": "Hola, tengo una reserva a nombre de García.", "en": "Hi, I have a reservation under the name García."},
                {"speaker": "Receptionist", "es": "Perfecto. ¿Me puede dar su pasaporte?", "en": "Perfect. Can you give me your passport?"},
                {"speaker": "You",          "es": "Aquí tiene. ¿A qué hora es el desayuno?", "en": "Here you go. What time is breakfast?"},
                {"speaker": "Receptionist", "es": "De siete a diez y media.", "en": "From seven to ten thirty."},
                {"speaker": "You",          "es": "¿Hay WiFi en la habitación?", "en": "Is there WiFi in the room?"},
                {"speaker": "Receptionist", "es": "Sí, la contraseña está en esta tarjeta.", "en": "Yes, the password is on this card."},
                {"speaker": "You",          "es": "¿A qué hora es el check-out?", "en": "What time is check-out?"},
            ],
            "B1": [
                {"speaker": "Receptionist", "es": "¡Buenas tardes! ¿En qué le puedo ayudar?", "en": "Good afternoon! How can I help you?"},
                {"speaker": "You",          "es": "Hola, tengo una reserva a nombre de García.", "en": "Hi, I have a reservation under the name García."},
                {"speaker": "Receptionist", "es": "Perfecto. ¿Me puede dar su pasaporte?", "en": "Perfect. Can you give me your passport?"},
                {"speaker": "You",          "es": "Aquí tiene. ¿A qué hora es el desayuno?", "en": "Here you go. What time is breakfast?"},
                {"speaker": "Receptionist", "es": "El desayuno es de siete a diez y media.", "en": "Breakfast is from seven to ten thirty."},
                {"speaker": "You",          "es": "Genial. ¿Hay WiFi en la habitación?", "en": "Great. Is there WiFi in the room?"},
                {"speaker": "Receptionist", "es": "Sí, la contraseña está en esta tarjeta.", "en": "Yes, the password is on this card."},
                {"speaker": "You",          "es": "Muchas gracias. ¿A qué hora es el check-out?", "en": "Thank you very much. And what time is check-out?"},
                {"speaker": "Receptionist", "es": "A las doce del mediodía.", "en": "At twelve noon."},
                {"speaker": "You",          "es": "¿Pueden guardarme el equipaje hasta las tres?", "en": "Can you store my luggage until three?"},
            ],
        },
    },
    "health": {
        "phrases": [
            {"es": "Necesito ver a un médico.", "en": "I need to see a doctor.", "tip": "💡 In an emergency say: '¡Llame a una ambulancia!'"},
            {"es": "Me duele la cabeza / el estómago.", "en": "My head / stomach hurts.", "tip": "💡 'Me duele + body part' is the key pattern for pain."},
            {"es": "Tengo fiebre / tos / náuseas.", "en": "I have a fever / cough / nausea.", "tip": "💡 'Tengo + symptom' for symptoms you have."},
            {"es": "Soy alérgico/a a...", "en": "I'm allergic to...", "tip": "💡 Critical to know! Penicilina, nueces, gluten, etc."},
            {"es": "¿Dónde está la farmacia más cercana?", "en": "Where is the nearest pharmacy?", "tip": "💡 Green cross sign = farmacia in Spain."},
            {"es": "¿Tiene algo para el dolor de cabeza?", "en": "Do you have something for a headache?", "tip": "💡 Swap 'dolor de cabeza' for your ailment."},
            {"es": "Necesito una receta.", "en": "I need a prescription.", "tip": "💡 Some medicines in Spain require a prescription."},
            {"es": "¿Cuándo puedo pedir una cita?", "en": "When can I make an appointment?", "tip": "💡 'Pedir una cita' = to book an appointment."},
            {"es": "Llevo dos días sintiéndome mal.", "en": "I've been feeling unwell for two days.", "tip": "💡 Context helps the doctor a lot."},
            {"es": "¿Tiene seguro médico?", "en": "Do you have health insurance?", "tip": "💡 Have your EHIC card ready if you're in the EU."},
        ],
        "dialogues": {
            "A1": [
                {"speaker": "Doctor", "es": "¿Qué le pasa?", "en": "What's wrong?"},
                {"speaker": "You",    "es": "Me duele la cabeza. Tengo fiebre.", "en": "My head hurts. I have a fever."},
                {"speaker": "Doctor", "es": "¿Desde cuándo?", "en": "Since when?"},
                {"speaker": "You",    "es": "Desde ayer.", "en": "Since yesterday."},
                {"speaker": "Doctor", "es": "¿Alergia a medicamentos?", "en": "Allergy to medicine?"},
                {"speaker": "You",    "es": "Soy alérgico/a a la penicilina.", "en": "I'm allergic to penicillin."},
            ],
            "A2": [
                {"speaker": "Doctor", "es": "Buenos días, ¿qué le pasa?", "en": "Good morning, what's wrong?"},
                {"speaker": "You",    "es": "Me duele la cabeza y tengo fiebre.", "en": "My head hurts and I have a fever."},
                {"speaker": "Doctor", "es": "¿Desde cuándo se siente así?", "en": "How long have you felt this way?"},
                {"speaker": "You",    "es": "Desde ayer por la noche.", "en": "Since last night."},
                {"speaker": "Doctor", "es": "¿Es alérgico/a a algún medicamento?", "en": "Are you allergic to any medication?"},
                {"speaker": "You",    "es": "Soy alérgico/a a la penicilina.", "en": "I'm allergic to penicillin."},
                {"speaker": "Doctor", "es": "Voy a recetarle algo para el dolor.", "en": "I'm going to prescribe something for the pain."},
                {"speaker": "You",    "es": "¿Necesito volver para otra cita?", "en": "Do I need to come back for another appointment?"},
            ],
            "B1": [
                {"speaker": "Doctor", "es": "Buenos días, ¿qué le pasa?", "en": "Good morning, what's wrong?"},
                {"speaker": "You",    "es": "Me duele mucho la cabeza y tengo fiebre.", "en": "I have a bad headache and I have a fever."},
                {"speaker": "Doctor", "es": "¿Desde cuándo se siente así?", "en": "How long have you been feeling like this?"},
                {"speaker": "You",    "es": "Llevo dos días sintiéndome mal.", "en": "I've been feeling unwell for two days."},
                {"speaker": "Doctor", "es": "¿Es alérgico/a a algún medicamento?", "en": "Are you allergic to any medication?"},
                {"speaker": "You",    "es": "Soy alérgico/a a la penicilina.", "en": "I'm allergic to penicillin."},
                {"speaker": "Doctor", "es": "De acuerdo. Voy a recetarle algo para el dolor.", "en": "Alright. I'm going to prescribe something for the pain."},
                {"speaker": "You",    "es": "¿Necesito volver para otra cita?", "en": "Do I need to come back for another appointment?"},
                {"speaker": "Doctor", "es": "Si no mejora en tres días, vuelva.", "en": "If you don't improve in three days, come back."},
                {"speaker": "You",    "es": "Muchas gracias, doctor.", "en": "Thank you very much, doctor."},
            ],
        },
    },
    "work": {
        "phrases": [
            {"es": "Me llamo... y soy de...", "en": "My name is... and I'm from...", "tip": "💡 Always start with a clear, confident introduction."},
            {"es": "Tengo X años de experiencia en...", "en": "I have X years of experience in...", "tip": "💡 Swap X for your number and fill in your field."},
            {"es": "Mis puntos fuertes son...", "en": "My strengths are...", "tip": "💡 Prepare 2-3 adjectives: organizado, creativo, responsable."},
            {"es": "Me gustaría trabajar aquí porque...", "en": "I'd like to work here because...", "tip": "💡 Always show you've researched the company."},
            {"es": "Trabajo bien en equipo.", "en": "I work well in a team.", "tip": "💡 Also useful: 'de forma independiente' (independently)."},
            {"es": "¿Cuál sería mi rol exactamente?", "en": "What would my exact role be?", "tip": "💡 Shows you're serious and detail-oriented."},
            {"es": "¿Hay posibilidades de formación?", "en": "Are there training opportunities?", "tip": "💡 Great question that shows ambition."},
            {"es": "Puedo empezar cuando sea necesario.", "en": "I can start whenever necessary.", "tip": "💡 Shows flexibility — employers love this."},
            {"es": "¿Cuál es el horario de trabajo?", "en": "What are the working hours?", "tip": "💡 Completely normal to ask this in an interview."},
            {"es": "¿Tiene alguna pregunta para mí?", "en": "Do you have any questions for me?", "tip": "💡 A confident way to close the interview."},
        ],
        "dialogues": {
            "A1": [
                {"speaker": "Interviewer", "es": "Buenos días. ¿Cómo se llama?", "en": "Good morning. What's your name?"},
                {"speaker": "You",         "es": "Me llamo Ana. Encantada.", "en": "My name is Ana. Nice to meet you."},
                {"speaker": "Interviewer", "es": "¿Por qué quiere este trabajo?", "en": "Why do you want this job?"},
                {"speaker": "You",         "es": "Me gusta mucho esta empresa.", "en": "I really like this company."},
                {"speaker": "Interviewer", "es": "¿Habla otros idiomas?", "en": "Do you speak other languages?"},
                {"speaker": "You",         "es": "Sí, inglés y un poco de español.", "en": "Yes, English and a little Spanish."},
            ],
            "A2": [
                {"speaker": "Interviewer", "es": "Buenos días, siéntese.", "en": "Good morning, sit down."},
                {"speaker": "You",         "es": "Buenos días, encantado/a de conocerle.", "en": "Good morning, nice to meet you."},
                {"speaker": "Interviewer", "es": "Cuénteme sobre usted.", "en": "Tell me about yourself."},
                {"speaker": "You",         "es": "Me llamo Ana. Tengo cinco años de experiencia en marketing.", "en": "My name is Ana. I have five years of experience in marketing."},
                {"speaker": "Interviewer", "es": "¿Por qué quiere trabajar aquí?", "en": "Why do you want to work here?"},
                {"speaker": "You",         "es": "Admiro mucho esta empresa. Trabajo bien en equipo.", "en": "I really admire this company. I work well in a team."},
                {"speaker": "Interviewer", "es": "¿Cuáles son sus puntos fuertes?", "en": "What are your strengths?"},
                {"speaker": "You",         "es": "Soy organizada, creativa y muy responsable.", "en": "I'm organised, creative and very responsible."},
            ],
            "B1": [
                {"speaker": "Interviewer", "es": "Buenos días, siéntese por favor.", "en": "Good morning, please sit down."},
                {"speaker": "You",         "es": "Buenos días, encantado/a de conocerle.", "en": "Good morning, nice to meet you."},
                {"speaker": "Interviewer", "es": "Cuénteme un poco sobre usted.", "en": "Tell me a bit about yourself."},
                {"speaker": "You",         "es": "Me llamo Ana. Tengo cinco años de experiencia en marketing.", "en": "My name is Ana. I have five years of experience in marketing."},
                {"speaker": "Interviewer", "es": "¿Por qué quiere trabajar en nuestra empresa?", "en": "Why do you want to work at our company?"},
                {"speaker": "You",         "es": "Me gustaría trabajar aquí porque admiro su innovación.", "en": "I'd like to work here because I admire your innovation."},
                {"speaker": "Interviewer", "es": "¿Cuáles son sus puntos fuertes?", "en": "What are your strengths?"},
                {"speaker": "You",         "es": "Soy muy organizada, creativa y trabajo bien en equipo.", "en": "I'm very organized, creative and work well in a team."},
                {"speaker": "Interviewer", "es": "¿Tiene alguna pregunta para nosotros?", "en": "Do you have any questions for us?"},
                {"speaker": "You",         "es": "Sí, ¿hay posibilidades de formación y crecimiento?", "en": "Yes, are there training and growth opportunities?"},
            ],
        },
    },
    "social": {
        "phrases": [
            {"es": "¡Hola! Me llamo..., ¿y tú?", "en": "Hi! My name is..., and yours?", "tip": "💡 Simple and warm — perfect opener."},
            {"es": "¿De dónde eres?", "en": "Where are you from?", "tip": "💡 One of the most common conversation starters."},
            {"es": "¿A qué te dedicas?", "en": "What do you do for work?", "tip": "💡 More natural than '¿Cuál es tu profesión?'"},
            {"es": "¿Quieres tomar algo?", "en": "Do you want to grab a drink?", "tip": "💡 Works for any drink — coffee, beer, etc."},
            {"es": "¿Qué planes tienes para el finde?", "en": "What are your plans for the weekend?", "tip": "💡 'Finde' = weekend (informal, very Spanish)."},
            {"es": "Me alegra mucho conocerte.", "en": "Really nice to meet you.", "tip": "💡 Warmer than just 'encantado/a'."},
            {"es": "¿Puedo invitarte a una copa?", "en": "Can I buy you a drink?", "tip": "💡 Classic and direct — works in any social setting."},
            {"es": "¿Tienes WhatsApp? ¿Nos intercambiamos el número?", "en": "Do you have WhatsApp? Shall we exchange numbers?", "tip": "💡 WhatsApp is the primary messaging app in Spain."},
            {"es": "¿Cuánto tiempo llevas en España?", "en": "How long have you been in Spain?", "tip": "💡 Great for connecting with fellow expats."},
            {"es": "¡Ha sido un placer! Hasta pronto.", "en": "It's been a pleasure! See you soon.", "tip": "💡 A warm way to end any social interaction."},
        ],
        "dialogues": {
            "A1": [
                {"speaker": "Person", "es": "¡Hola! ¿Cómo te llamas?", "en": "Hi! What's your name?"},
                {"speaker": "You",    "es": "Me llamo Alex. ¿Y tú?", "en": "My name is Alex. And you?"},
                {"speaker": "Person", "es": "Soy María. ¿De dónde eres?", "en": "I'm María. Where are you from?"},
                {"speaker": "You",    "es": "Soy de Alemania. ¿Y tú?", "en": "I'm from Germany. And you?"},
                {"speaker": "Person", "es": "¡Qué bien! ¿Quieres tomar algo?", "en": "How nice! Do you want something to drink?"},
                {"speaker": "You",    "es": "Sí, gracias. Me alegra conocerte.", "en": "Yes, thank you. Nice to meet you."},
            ],
            "A2": [
                {"speaker": "Person", "es": "¡Hola! ¿Eres nuevo/a aquí?", "en": "Hi! Are you new here?"},
                {"speaker": "You",    "es": "Sí, llegué hace una semana. Me llamo Alex.", "en": "Yes, I arrived a week ago. My name is Alex."},
                {"speaker": "Person", "es": "¡Qué bien! Yo soy María. ¿De dónde eres?", "en": "How nice! I'm María. Where are you from?"},
                {"speaker": "You",    "es": "Soy de Alemania. ¿Y tú, a qué te dedicas?", "en": "I'm from Germany. And you, what do you do?"},
                {"speaker": "Person", "es": "Soy profesora. ¿Te gusta España?", "en": "I'm a teacher. Do you like Spain?"},
                {"speaker": "You",    "es": "¡Me encanta! ¿Quieres tomar algo?", "en": "I love it! Do you want to grab a drink?"},
                {"speaker": "Person", "es": "¡Claro! Con mucho gusto.", "en": "Of course! With pleasure."},
                {"speaker": "You",    "es": "¿Tienes WhatsApp? ¿Nos intercambiamos el número?", "en": "Do you have WhatsApp? Shall we exchange numbers?"},
            ],
            "B1": [
                {"speaker": "Person", "es": "¡Hola! ¿Eres nuevo/a aquí?", "en": "Hi! Are you new here?"},
                {"speaker": "You",    "es": "Sí, llegué hace una semana. Me llamo Alex.", "en": "Yes, I arrived a week ago. My name is Alex."},
                {"speaker": "Person", "es": "¡Qué bien! Yo soy María. ¿De dónde eres?", "en": "How nice! I'm María. Where are you from?"},
                {"speaker": "You",    "es": "Soy de Alemania, pero vivo aquí por trabajo.", "en": "I'm from Germany, but I live here for work."},
                {"speaker": "Person", "es": "¡Qué interesante! ¿Y a qué te dedicas?", "en": "How interesting! And what do you do?"},
                {"speaker": "You",    "es": "Soy ingeniero/a de software. ¿Y tú?", "en": "I'm a software engineer. And you?"},
                {"speaker": "Person", "es": "Soy profesora. ¿Te gusta Barcelona hasta ahora?", "en": "I'm a teacher. Do you like Barcelona so far?"},
                {"speaker": "You",    "es": "¡Me encanta! ¿Qué recomiendas visitar?", "en": "I love it! What do you recommend visiting?"},
                {"speaker": "Person", "es": "El barrio gótico es increíble. ¿Quedamos un día?", "en": "The Gothic quarter is incredible. Shall we meet up one day?"},
                {"speaker": "You",    "es": "¡Me encantaría! ¿Tienes WhatsApp?", "en": "I'd love that! Do you have WhatsApp?"},
            ],
        },
    },
    "housing": {
        "phrases": [
            {"es": "Hay un problema con la calefacción / el agua.", "en": "There's a problem with the heating / the water.", "tip": "💡 Swap for your issue: luz (electricity), goteras (leaks)."},
            {"es": "El grifo / la caldera está roto/a.", "en": "The tap / boiler is broken.", "tip": "💡 'Roto' for masculine nouns, 'rota' for feminine."},
            {"es": "¿Cuándo puede mandar a alguien a arreglarlo?", "en": "When can you send someone to fix it?", "tip": "💡 Firm but polite — sets a clear expectation."},
            {"es": "Llevo X días sin calefacción / agua caliente.", "en": "I've been without heating / hot water for X days.", "tip": "💡 Stating duration makes your complaint more urgent."},
            {"es": "¿Está incluido el agua / la luz en el alquiler?", "en": "Is water / electricity included in the rent?", "tip": "💡 Critical to clarify before signing anything."},
            {"es": "Necesito una copia del contrato.", "en": "I need a copy of the contract.", "tip": "💡 Always get everything in writing."},
            {"es": "¿Cuándo se paga el alquiler?", "en": "When is rent due?", "tip": "💡 Usually the first of the month in Spain."},
            {"es": "Los vecinos hacen mucho ruido.", "en": "The neighbours are making a lot of noise.", "tip": "💡 'Ruido' = noise. A very common complaint!"},
            {"es": "¿Me puede devolver la fianza?", "en": "Can you return my deposit?", "tip": "💡 'Fianza' = deposit. Know your rights!"},
            {"es": "Voy a llamar a un fontanero / electricista.", "en": "I'm going to call a plumber / electrician.", "tip": "💡 Useful if the landlord isn't responding."},
        ],
        "dialogues": {
            "A1": [
                {"speaker": "You",      "es": "Hola, hay un problema en el piso.", "en": "Hi, there's a problem in the flat."},
                {"speaker": "Landlord", "es": "¿Qué pasa?", "en": "What's happening?"},
                {"speaker": "You",      "es": "El grifo está roto.", "en": "The tap is broken."},
                {"speaker": "Landlord", "es": "¿Desde cuándo?", "en": "Since when?"},
                {"speaker": "You",      "es": "Desde ayer.", "en": "Since yesterday."},
                {"speaker": "Landlord", "es": "Mando a alguien mañana.", "en": "I'll send someone tomorrow."},
            ],
            "A2": [
                {"speaker": "You",      "es": "Hola, soy el/la inquilino/a del piso 3B.", "en": "Hi, I'm the tenant in flat 3B."},
                {"speaker": "Landlord", "es": "Hola, ¿qué tal? ¿En qué puedo ayudarle?", "en": "Hi, how are you? How can I help you?"},
                {"speaker": "You",      "es": "Hay un problema con la calefacción.", "en": "There's a problem with the heating."},
                {"speaker": "Landlord", "es": "Lo siento. ¿Cuándo empezó?", "en": "I'm sorry. When did it start?"},
                {"speaker": "You",      "es": "El lunes. ¿Cuándo puede mandar a alguien?", "en": "On Monday. When can you send someone?"},
                {"speaker": "Landlord", "es": "Mañana por la mañana.", "en": "Tomorrow morning."},
                {"speaker": "You",      "es": "¿A qué hora?", "en": "At what time?"},
                {"speaker": "Landlord", "es": "Entre las nueve y las doce.", "en": "Between nine and twelve."},
            ],
            "B1": [
                {"speaker": "You",      "es": "Hola, soy el/la inquilino/a del piso 3B.", "en": "Hi, I'm the tenant in flat 3B."},
                {"speaker": "Landlord", "es": "Hola, ¿qué tal? ¿En qué puedo ayudarle?", "en": "Hi, how are you? How can I help you?"},
                {"speaker": "You",      "es": "Hay un problema con la calefacción. Llevo tres días sin calor.", "en": "There's a problem with the heating. I've been without heat for three days."},
                {"speaker": "Landlord", "es": "Vaya, lo siento. ¿Cuándo empezó el problema?", "en": "Oh dear, I'm sorry. When did the problem start?"},
                {"speaker": "You",      "es": "El lunes por la noche dejó de funcionar.", "en": "Monday night it stopped working."},
                {"speaker": "Landlord", "es": "Entiendo. Voy a mandar a un técnico mañana.", "en": "I understand. I'll send a technician tomorrow."},
                {"speaker": "You",      "es": "¿A qué hora puede venir?", "en": "What time can they come?"},
                {"speaker": "Landlord", "es": "Por la mañana, entre las nueve y las doce.", "en": "In the morning, between nine and twelve."},
                {"speaker": "You",      "es": "Perfecto. ¿Puede confirmarme por mensaje?", "en": "Perfect. Can you confirm by message?"},
                {"speaker": "Landlord", "es": "Sí, claro. Le mando un mensaje ahora mismo.", "en": "Yes, of course. I'll send you a message right now."},
            ],
        },
    },
    "general": {
        "phrases": [
            {"es": "¿Puede ayudarme, por favor?", "en": "Can you help me, please?", "tip": "💡 Works in absolutely any situation."},
            {"es": "No entiendo. ¿Puede repetir más despacio?", "en": "I don't understand. Can you repeat more slowly?", "tip": "💡 Your most important survival phrase!"},
            {"es": "¿Habla inglés?", "en": "Do you speak English?", "tip": "💡 A useful backup — but try Spanish first!"},
            {"es": "¿Dónde está...?", "en": "Where is...?", "tip": "💡 Essential for navigation anywhere."},
            {"es": "¿Cuánto cuesta?", "en": "How much does it cost?", "tip": "💡 Universal and always useful."},
            {"es": "Por favor / Gracias / De nada.", "en": "Please / Thank you / You're welcome.", "tip": "💡 These three phrases open every door."},
            {"es": "Buenos días / Buenas tardes / Buenas noches.", "en": "Good morning / Good afternoon / Good evening.", "tip": "💡 Always greet before asking for anything."},
            {"es": "Disculpe, ¿me puede decir...?", "en": "Excuse me, could you tell me...?", "tip": "💡 Polite way to start any question."},
            {"es": "Soy de... / No hablo español muy bien.", "en": "I'm from... / I don't speak Spanish very well.", "tip": "💡 Being upfront gets you more patience from locals."},
            {"es": "¿Puede escribirlo, por favor?", "en": "Can you write it down, please?", "tip": "💡 Incredibly useful when you can't catch a word."},
        ],
        "dialogues": {
            "A1": [
                {"speaker": "Local", "es": "¡Hola! ¿Qué necesita?", "en": "Hi! What do you need?"},
                {"speaker": "You",   "es": "Disculpe. No hablo español bien.", "en": "Excuse me. I don't speak Spanish well."},
                {"speaker": "Local", "es": "No hay problema. ¿Qué busca?", "en": "No problem. What are you looking for?"},
                {"speaker": "You",   "es": "¿Puede repetir despacio?", "en": "Can you repeat slowly?"},
                {"speaker": "Local", "es": "Claro. Es por allí.", "en": "Of course. It's over there."},
                {"speaker": "You",   "es": "Muchas gracias.", "en": "Thank you very much."},
            ],
            "A2": [
                {"speaker": "Local", "es": "¡Hola! ¿En qué le puedo ayudar?", "en": "Hi! How can I help you?"},
                {"speaker": "You",   "es": "Hola, disculpe. No hablo español muy bien.", "en": "Hi, excuse me. I don't speak Spanish very well."},
                {"speaker": "Local", "es": "No hay problema, ¿qué necesita?", "en": "No problem, what do you need?"},
                {"speaker": "You",   "es": "Busco... ¿Puede ayudarme?", "en": "I'm looking for... Can you help me?"},
                {"speaker": "Local", "es": "Claro, con mucho gusto.", "en": "Of course, with pleasure."},
                {"speaker": "You",   "es": "¿Puede repetir más despacio, por favor?", "en": "Can you repeat more slowly, please?"},
                {"speaker": "Local", "es": "Sí, claro. Es por allí.", "en": "Yes, of course. It's over there."},
                {"speaker": "You",   "es": "¿Puede escribirlo, por favor?", "en": "Can you write it down, please?"},
            ],
            "B1": [
                {"speaker": "Local", "es": "¡Hola! ¿En qué le puedo ayudar?", "en": "Hi! How can I help you?"},
                {"speaker": "You",   "es": "Hola, disculpe. No hablo español muy bien.", "en": "Hi, excuse me. I don't speak Spanish very well."},
                {"speaker": "Local", "es": "No hay problema, ¿qué necesita?", "en": "No problem, what do you need?"},
                {"speaker": "You",   "es": "Busco... ¿Puede ayudarme?", "en": "I'm looking for... Can you help me?"},
                {"speaker": "Local", "es": "Claro, con mucho gusto.", "en": "Of course, with pleasure."},
                {"speaker": "You",   "es": "¿Puede repetir más despacio, por favor?", "en": "Can you repeat more slowly, please?"},
                {"speaker": "Local", "es": "Sí, claro. Es por allí.", "en": "Yes, of course. It's over there."},
                {"speaker": "You",   "es": "¿Puede escribirlo, por favor?", "en": "Can you write it down, please?"},
                {"speaker": "Local", "es": "Por supuesto.", "en": "Of course."},
                {"speaker": "You",   "es": "Muchas gracias, muy amable.", "en": "Thank you very much, very kind of you."},
            ],
        },
    },
}

LEVEL_INFO = {
    "A1 — Beginner":      {"code": "A1", "desc": "Basic greetings and numbers. Real conversations feel overwhelming.", "known_vocab": 300,  "color": "#58CC02"},
    "A2 — Elementary":    {"code": "A2", "desc": "Simple transactions, but struggle with fast or complex speech.",   "known_vocab": 800,  "color": "#1CB0F6"},
    "B1 — Intermediate":  {"code": "B1", "desc": "Manage most daily situations but miss nuance and idioms.",         "known_vocab": 2000, "color": "#FF9F1C"},
}

SCENARIO_LABELS = {
    "restaurant": "🍽️ Restaurant", "transport": "🚕 Transport",
    "shopping":   "🛍️ Shopping",   "hotel":     "🏨 Hotel",
    "health":     "🏥 Health",     "work":      "💼 Work",
    "social":     "🥂 Social",     "housing":   "🏠 Housing",
    "general":    "🌍 General",
}

# ─────────────────────────────────────────────
#  NLP HELPERS
# ─────────────────────────────────────────────

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

def build_scenario_data(matched_keys: list, user_level_code: str) -> dict:
    if not matched_keys or matched_keys == ["general"]:
        base = KNOWLEDGE_BASE["general"]
        all_phrases = filter_phrases_by_level(base["phrases"], user_level_code)
        dialogue = base["dialogues"][user_level_code]
        return {"phrases": all_phrases, "dialogue": dialogue,
                "primary_key": "general"}

    primary = KNOWLEDGE_BASE[matched_keys[0]]
    merged = list(primary["phrases"])
    if len(matched_keys) > 1:
        existing = {p["es"] for p in merged}
        for p in KNOWLEDGE_BASE[matched_keys[1]]["phrases"][:3]:
            if p["es"] not in existing:
                merged.append(p)

    filtered = filter_phrases_by_level(merged, user_level_code)
    dialogue = primary["dialogues"][user_level_code]

    return {"phrases": filtered, "dialogue": dialogue,
            "primary_key": matched_keys[0]}

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
    scenario_data   = build_scenario_data(matched_keys, user_level_code)
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
                plevel   = get_phrase_level(phrase["es"])
                ppattern = get_phrase_pattern(phrase["es"])
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
                from corpus_data import PHRASE_DIFFICULTY as PD
                record_session(
                    scenario          = primary_key,
                    level             = user_level_code,
                    confidence_map    = st.session_state.confidence,
                    dialogue          = dialogue,
                    phrase_pattern_fn = lambda es: PD.get(es, ("present_simple", "A2"))[0],
                )
                st.session_state[session_key] = True

            strengths,   weaknesses   = get_strengths_and_weaknesses()
            predicted                  = get_predicted_readiness(primary_key, user_level_code)
            session_count              = get_session_count()
            recommendation             = get_recommended_focus()

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
                    pattern = get_phrase_pattern(line["es"])
                    level_tag = get_phrase_level(line["es"])
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
                plevel   = get_phrase_level(phrase["es"])
                ppattern = get_phrase_pattern(phrase["es"])
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
                    kit_text += f"  ES: {line['es']}\n  EN: {line['en']}\n  Pattern: {get_phrase_pattern(line['es'])}\n\n"
                kit_text += "\nALL PHRASES:\n"
            for p in scenario_data["phrases"]:
                plevel   = get_phrase_level(p["es"])
                ppattern = get_phrase_pattern(p["es"])
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
