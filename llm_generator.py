"""
llm_generator.py
────────────────
Gemini API integration for ConvoReady.

Generates:
  1. Dynamic survival phrases tailored to the user's exact scenario
  2. A practice dialogue grounded in the user's specific situation
  3. A smart, contextual learning recommendation based on grammar history

Uses gemini-1.5-flash (free tier, fast, sufficient quality for this use case).
Falls back gracefully to static knowledge base content if API call fails.
"""

import json
import streamlit as st

LEVEL_DESCRIPTIONS = {
    "A1": "absolute beginner — only present tense, very short sentences, basic vocabulary",
    "A2": "elementary — simple past and future, slightly longer sentences, everyday vocabulary",
    "B1": "intermediate — can use conditional and subjunctive, complex sentences, nuanced vocabulary",
}

DIALOGUE_LENGTHS = {"A1": 6, "A2": 8, "B1": 10}


def _get_gemini_client():
    """Initialise and return Gemini client. Returns None if unavailable."""
    try:
        from google import genai
        key = st.secrets.get("GEMINI_KEY", None)
        if not key:
            st.warning("⚠️ GEMINI_KEY not found in secrets.")
            return None
        return genai.Client(api_key=key)
    except Exception as e:
        st.warning(f"⚠️ Could not initialise Gemini: {e}")
        return None

MODEL = "gemini-2.5-flash"


# ── Phrase generation ────────────────────────────────────────────────────────

def generate_phrases(user_scenario: str, scenario_category: str,
                     level_code: str, fallback_phrases: list) -> list:
    """
    Generate 6 survival phrases tailored to the user's exact scenario.
    Returns list of {es, en, tip} dicts.
    Falls back to static phrases on any error.
    """
    client = _get_gemini_client()
    if client is None:
        return fallback_phrases

    level_desc = LEVEL_DESCRIPTIONS.get(level_code, LEVEL_DESCRIPTIONS["A1"])

    prompt = f"""You are a Spanish language expert helping a learner prepare for a real-life situation.

The learner's situation: "{user_scenario}"
Scenario category: {scenario_category}
Learner level: {level_code} — {level_desc}

Generate exactly 6 survival phrases in Spanish that are SPECIFICALLY tailored to this exact situation.
Do NOT generate generic phrases — every phrase must be directly useful for "{user_scenario}".

Return ONLY a valid JSON array with exactly 6 objects. Each object must have:
- "es": the Spanish phrase (natural, native-sounding)
- "en": the English translation
- "tip": a practical usage tip starting with 💡 (1 sentence, specific to this situation)
- "level": one of "A1", "A2", or "B1" based on grammar complexity
- "pattern": one of "present_simple", "basic_question", "polite_request", "future", "past_simple", "conditional", "subjunctive", "complex", "greeting", "negation"

Level guide:
- A1: present tense only, very short, basic vocab
- A2: simple past/future, slightly longer
- B1: conditional, subjunctive, complex structures

Rules:
- Match complexity strictly to {level_code} level — most phrases should be {level_code}
- Phrases must be immediately usable in this exact situation
- No markdown, no explanation, just the JSON array

Example format:
[
  {{"es": "...", "en": "...", "tip": "💡 ...", "level": "A1", "pattern": "present_simple"}},
  ...
]"""

    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        text = response.text.strip()
        # Strip markdown code fences if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        phrases = json.loads(text.strip())
        if isinstance(phrases, list) and len(phrases) > 0:
            return phrases[:6]
    except Exception as e:
        st.warning(f"⚠️ LLM phrase generation failed: {e} — using static fallback.")

    return fallback_phrases


# ── Dialogue generation ──────────────────────────────────────────────────────

def generate_dialogue(user_scenario: str, scenario_category: str,
                      level_code: str, fallback_dialogue: list) -> list:
    """
    Generate a practice dialogue tailored to the user's exact scenario.
    Returns list of {speaker, es, en} dicts alternating between 'You' and other party.
    Falls back to static dialogue on any error.
    """
    client = _get_gemini_client()
    if client is None:
        return fallback_dialogue

    level_desc   = LEVEL_DESCRIPTIONS.get(level_code, LEVEL_DESCRIPTIONS["A1"])
    n_lines      = DIALOGUE_LENGTHS.get(level_code, 6)
    other_speaker = _get_other_speaker(scenario_category)

    prompt = f"""You are a Spanish language expert creating a practice dialogue for a learner.

The learner's situation: "{user_scenario}"
Scenario category: {scenario_category}
Learner level: {level_code} — {level_desc}
Number of lines: exactly {n_lines}

Create a realistic dialogue for this EXACT situation — not a generic {scenario_category} dialogue.
The dialogue should reflect the specific details of "{user_scenario}".

Speakers: "You" (the learner) and "{other_speaker}"
Start with "{other_speaker}" speaking first.
Alternate between speakers. "You" must have {n_lines // 2} lines.

Return ONLY a valid JSON array with exactly {n_lines} objects. Each object must have:
- "speaker": either "You" or "{other_speaker}"
- "es": the Spanish line (appropriate for {level_code} level)
- "en": the English translation

Rules:
- Match complexity strictly to {level_code} level
- Make it realistic and immediately practical
- No markdown, no explanation, just the JSON array"""

    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        dialogue = json.loads(text.strip())
        if isinstance(dialogue, list) and len(dialogue) >= 4:
            return dialogue
    except Exception as e:
        st.warning(f"⚠️ LLM dialogue generation failed: {e} — using static fallback.")

    return fallback_dialogue


# ── Smart recommendation ─────────────────────────────────────────────────────

def generate_smart_recommendation(struggled_phrases: list,
                                   pattern_stats: dict,
                                   scenario: str,
                                   level_code: str,
                                   fallback: str) -> str:
    """
    Generate a contextual, specific recommendation based on what the user
    actually struggled with in this session.
    Falls back to rule-based recommendation on any error.
    """
    client = _get_gemini_client()
    if client is None:
        return fallback

    if not struggled_phrases:
        return None

    struggled_text = "\n".join([f"- {p['es']} ({p['en']})" for p in struggled_phrases[:5]])

    weak_patterns = []
    for pattern, counts in pattern_stats.items():
        total = counts.get("confident", 0) + counts.get("struggled", 0)
        if total >= 2:
            rate = counts.get("confident", 0) / total
            if rate < 0.7:
                weak_patterns.append(f"{pattern} ({int(rate*100)}% confident)")

    pattern_text = ", ".join(weak_patterns[:3]) if weak_patterns else "insufficient data yet"

    prompt = f"""You are a Spanish language tutor giving personalised feedback to a learner.

Scenario they just practised: {scenario}
Learner level: {level_code}

Phrases they struggled with in this session:
{struggled_text}

Grammar patterns they consistently struggle with across sessions: {pattern_text}

Write a SHORT (2-3 sentences max), specific, actionable recommendation.
- Reference the actual phrases they struggled with
- Give a concrete tip they can practise TODAY
- Be encouraging but honest
- Do NOT be generic — no "practise more" type advice
- Write in second person ("You struggled with...")
- Plain text only, no markdown, no bullet points"""

    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        text = response.text.strip()
        if text:
            return text
    except Exception:
        pass

    return fallback



# ── Conversation chat ─────────────────────────────────────────────────────────

def build_conversation_system_prompt(scenario_category: str, user_scenario: str,
                                      level_code: str, weak_patterns: list) -> str:
    """Build the system prompt for the conversation practice chatbot."""
    role       = _get_other_speaker(scenario_category)
    level_desc = LEVEL_DESCRIPTIONS.get(level_code, LEVEL_DESCRIPTIONS["A1"])
    weak_text  = ", ".join([p["label"] for p in weak_patterns[:3]]) if weak_patterns else "none identified yet"

    return f"""You are playing the role of a {role} in Spain. The user is a Spanish learner practising a real conversation.

Their situation: "{user_scenario}"
Their level: {level_code} — {level_desc}
Their weak grammar patterns: {weak_text}

Your rules:
1. ALWAYS respond in Spanish. Keep your Spanish complexity appropriate for a {level_code} learner.
2. After your Spanish response, add a line break and then an English translation in parentheses like: (Translation: ...)
3. If the user writes in English, respond ONLY with: "¡En español, por favor! Try to say it in Spanish. 💪" — do not answer their question until they try in Spanish.
4. If the user makes a grammar mistake, gently correct it at the end of your response in a friendly way.
5. Naturally steer the conversation so the user needs to use: {weak_text}. Do not force it unnaturally.
6. Stay in character as a {role} at all times. Keep the conversation realistic and grounded in: "{user_scenario}".
7. Keep your responses concise — 1 to 3 sentences maximum.
8. Return your response as a JSON object with two fields: "spanish" and "english". 
   Example: {{"spanish": "¡Buenas tardes! ¿En qué puedo ayudarle?", "english": "Good afternoon! How can I help you?"}}
   Only return the JSON, nothing else."""


def chat_with_local(chat_history: list, user_message: str,
                    system_prompt: str) -> dict:
    """
    Send a user message and chat history to Gemini.
    Returns dict with 'spanish' and 'english' keys.
    Falls back to a safe default on error.
    """
    client = _get_gemini_client()
    if client is None:
        return {"spanish": "Lo siento, hay un problema técnico.", "english": "Sorry, there is a technical problem."}

    # Build contents list — system prompt as first user turn (Gemini style)
    contents = [{"role": "user",  "parts": [{"text": system_prompt}]},
                {"role": "model", "parts": [{"text": '{"spanish": "¡Hola! ¿En qué puedo ayudarle?", "english": "Hello! How can I help you?"}'}]}]

    for msg in chat_history:
        contents.append({
            "role":  "user" if msg["role"] == "user" else "model",
            "parts": [{"text": msg["content"]}]
        })

    contents.append({"role": "user", "parts": [{"text": user_message}]})

    try:
        response = client.models.generate_content(model=MODEL, contents=contents)
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        parsed = json.loads(text.strip())
        if "spanish" in parsed and "english" in parsed:
            return parsed
    except Exception as e:
        pass

    return {"spanish": "No entiendo. ¿Puede repetir?", "english": "I don't understand. Can you repeat?"}


def generate_conversation_feedback(chat_history: list, scenario: str,
                                    level_code: str, weak_patterns: list) -> dict:
    """
    Analyse the full conversation and return structured feedback.
    Returns dict with: score (int), summary, strengths, improvements, next_focus
    """
    client = _get_gemini_client()
    if client is None:
        return None

    if len(chat_history) < 2:
        return None

    conversation_text = "\n".join([
        f"{'User' if m['role'] == 'user' else 'AI'}: {m['content']}"
        for m in chat_history
    ])

    weak_text = ", ".join([p["label"] for p in weak_patterns[:3]]) if weak_patterns else "none"

    prompt = f"""You are a Spanish language tutor analysing a practice conversation.

Scenario: {scenario}
Learner level: {level_code}
Known weak patterns: {weak_text}

Conversation transcript:
{conversation_text}

Analyse the learner's Spanish and return ONLY a JSON object with these exact fields:
- "score": integer from 0 to 100
- "summary": 1 sentence overall assessment
- "strengths": list of 2 strings describing what they did well
- "improvements": list of 2 strings describing specific mistakes or areas to improve (reference actual phrases they used)
- "next_focus": 1 actionable string — the single most important thing to practise before their next conversation

Return only the JSON, no markdown, no explanation."""

    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        parsed = json.loads(text.strip())
        if "score" in parsed and "summary" in parsed:
            return parsed
    except Exception:
        pass

    return None


def _get_other_speaker(scenario_category: str) -> str:
    speakers = {
        "restaurant":  "Waiter",
        "transport":   "Driver",
        "shopping":    "Shop Assistant",
        "hotel":       "Receptionist",
        "health":      "Doctor",
        "work":        "Colleague",
        "social":      "Friend",
        "housing":     "Landlord",
        "general":     "Local",
    }
    return speakers.get(scenario_category, "Local")
