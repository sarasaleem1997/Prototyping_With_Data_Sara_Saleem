"""
user_model.py
─────────────
In-app learning model for ConvoReady.

Tracks grammar pattern performance across sessions using Supabase
(cloud PostgreSQL database) so data persists across Streamlit Cloud
deployments and browser sessions.

Single demo user: all data stored under key 'demo_user'.

Data schema (stored as JSONB in Supabase):
{
    "sessions": [...],
    "pattern_stats": {
        "present_simple": {"confident": 12, "struggled": 3},
        ...
    },
    "scenario_stats": {
        "restaurant": {"sessions": 3, "avg_readiness": 72},
        ...
    }
}
"""

import os
from datetime import datetime
import streamlit as st

DEMO_USER_ID = "demo_user"

# ── Supabase connection ──────────────────────────────────────────────────────

def _get_client():
    """Return a Supabase client. Reads credentials from Streamlit secrets."""
    try:
        from supabase import create_client
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception:
        return None

# ── Constants ────────────────────────────────────────────────────────────────

PATTERN_LABELS = {
    "present_simple":  "Present tense",
    "basic_question":  "Basic questions",
    "greeting":        "Greetings",
    "future":          "Future (ir + a)",
    "polite_request":  "Polite requests",
    "negation":        "Negation",
    "past_simple":     "Past tense",
    "conditional":     "Conditional",
    "subjunctive":     "Subjunctive",
    "complex":         "Complex sentences",
    "number":          "Numbers",
}

PATTERN_DIFFICULTY = {
    "greeting":       1,
    "number":         1,
    "present_simple": 2,
    "basic_question": 2,
    "future":         3,
    "polite_request": 3,
    "negation":       3,
    "past_simple":    4,
    "conditional":    5,
    "subjunctive":    5,
    "complex":        5,
}

# ── Empty profile ────────────────────────────────────────────────────────────

def _empty_profile() -> dict:
    return {"sessions": [], "pattern_stats": {}, "scenario_stats": {}}

# ── Load / Save ──────────────────────────────────────────────────────────────

def _load_profile() -> dict:
    """Load profile from Supabase. Falls back to empty profile on error."""
    client = _get_client()
    if client is None:
        return _empty_profile()
    try:
        result = (client.table("user_profile")
                        .select("data")
                        .eq("id", DEMO_USER_ID)
                        .execute())
        if result.data:
            return result.data[0]["data"]
    except Exception:
        pass
    return _empty_profile()

def _save_profile(profile: dict):
    """Upsert profile to Supabase."""
    client = _get_client()
    if client is None:
        return
    try:
        client.table("user_profile").upsert({
            "id":         DEMO_USER_ID,
            "data":       profile,
            "updated_at": datetime.now().isoformat(),
        }).execute()
    except Exception as e:
        st.warning(f"Could not save to database: {e}")

# ── Record session ───────────────────────────────────────────────────────────

def record_session(scenario: str, level: str, confidence_map: dict,
                   dialogue: list, phrase_pattern_fn):
    profile          = _load_profile()
    results          = []
    readiness_scores = []

    for key, verdict in confidence_map.items():
        idx = int(key.split("_")[-1])
        if idx < len(dialogue) and dialogue[idx]["speaker"] == "You":
            phrase_es = dialogue[idx]["es"]
            pattern   = phrase_pattern_fn(phrase_es)
            confident = verdict == "✅"
            results.append({"pattern": pattern, "phrase": phrase_es, "confident": confident})
            readiness_scores.append(1 if confident else 0)

            if pattern not in profile["pattern_stats"]:
                profile["pattern_stats"][pattern] = {"confident": 0, "struggled": 0}
            if confident:
                profile["pattern_stats"][pattern]["confident"] += 1
            else:
                profile["pattern_stats"][pattern]["struggled"] += 1

    avg_readiness = int(
        (sum(readiness_scores) / len(readiness_scores)) * 100
    ) if readiness_scores else 0

    if scenario not in profile["scenario_stats"]:
        profile["scenario_stats"][scenario] = {"sessions": 0, "avg_readiness": 0}
    prev = profile["scenario_stats"][scenario]
    n    = prev["sessions"]
    prev["avg_readiness"] = int((prev["avg_readiness"] * n + avg_readiness) / (n + 1))
    prev["sessions"]     += 1

    profile["sessions"].append({
        "timestamp": datetime.now().isoformat(),
        "scenario":  scenario,
        "level":     level,
        "results":   results,
        "readiness": avg_readiness,
    })

    _save_profile(profile)
    return avg_readiness

# ── Analytics ────────────────────────────────────────────────────────────────

def get_pattern_performance() -> dict:
    stats  = _load_profile().get("pattern_stats", {})
    result = {}
    for pattern, counts in stats.items():
        total = counts["confident"] + counts["struggled"]
        if total == 0:
            continue
        result[pattern] = {
            "confident": counts["confident"],
            "struggled": counts["struggled"],
            "total":     total,
            "rate":      counts["confident"] / total,
            "label":     PATTERN_LABELS.get(pattern, pattern),
            "difficulty":PATTERN_DIFFICULTY.get(pattern, 3),
        }
    return result

def get_strengths_and_weaknesses(min_attempts: int = 2):
    perf      = get_pattern_performance()
    qualified = {k: v for k, v in perf.items() if v["total"] >= min_attempts}
    strengths  = sorted(
        [v for v in qualified.values() if v["rate"] >= 0.7],
        key=lambda x: x["rate"], reverse=True)[:3]
    weaknesses = sorted(
        [v for v in qualified.values() if v["rate"] < 0.7],
        key=lambda x: x["rate"])[:3]
    return strengths, weaknesses

def get_recommended_focus() -> str:
    _, weaknesses = get_strengths_and_weaknesses()
    if not weaknesses:
        return None
    worst = weaknesses[0]
    rate  = int(worst["rate"] * 100)
    tips  = {
        "present_simple":  "Drill yo/tú/él verb endings daily — conjugate 5 verbs each morning.",
        "basic_question":  "Memorise the six question words: qué, cuándo, dónde, cómo, cuánto, quién.",
        "polite_request":  "Practice '¿Puede + infinitive?' — the most versatile polite structure in Spanish.",
        "future":          "Drill 'ir + a + infinitive' — Voy a pedir, Vamos a salir, Van a llegar.",
        "past_simple":     "Learn these 10 irregular preterites first: fui, tuve, hice, puse, vine, dije, traje, pude, supe, quise.",
        "conditional":     "Start with 'me gustaría' — it handles 80% of polite conditional situations.",
        "subjunctive":     "Focus on trigger phrases: quiero que, es importante que, cuando + subjunctive.",
        "complex":         "Split long sentences into two short ones. 'Tengo frío y necesito la calefacción' not one long sentence.",
        "greeting":        "Memorise three greetings by time: Buenos días / Buenas tardes / Buenas noches.",
        "negation":        "Practice no + verb until automatic: no tengo, no entiendo, no puedo, no sé.",
    }
    tip = tips.get(worst["label"].lower().replace(" ", "_"),
                   f"Review {worst['label']} phrases from your last session before moving on.")
    return f"You struggle most with {worst['label']} ({rate}% confident). {tip}"

def get_predicted_readiness(scenario: str, level: str):
    profile = _load_profile()
    if len(profile.get("sessions", [])) < 2:
        return None
    perf = get_pattern_performance()
    if not perf:
        return None
    weighted_sum   = sum(d["rate"] * PATTERN_DIFFICULTY.get(p, 3) for p, d in perf.items())
    weighted_total = sum(PATTERN_DIFFICULTY.get(p, 3) for p in perf)
    return int((weighted_sum / weighted_total) * 100) if weighted_total else None

def get_session_count() -> int:
    return len(_load_profile().get("sessions", []))

def get_scenario_history() -> dict:
    return _load_profile().get("scenario_stats", {})

def clear_profile():
    _save_profile(_empty_profile())
