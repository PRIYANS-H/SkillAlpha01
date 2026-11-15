import json
import logging
import httpx
from typing import Dict, List, Optional
from app.config import settings

logger = logging.getLogger("skillalpha.llm")

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"


def _api_key() -> Optional[str]:
    key = (settings.GROQ_API_KEY or settings.LLM_API_KEY or "").strip()
    return key or None


def _chat(messages: List[Dict], temperature: float, max_tokens: int, timeout: float) -> Optional[str]:
    """Single Groq chat completion; returns the message text or None on any failure."""
    api_key = _api_key()
    if not api_key:
        return None
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(
                GROQ_CHAT_URL,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": settings.LLM_MODEL,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )
        if resp.status_code != 200:
            logger.warning(f"Groq returned HTTP {resp.status_code}")
            return None
        content = resp.json()["choices"][0]["message"]["content"]
        return content.strip() if content else None
    except Exception as e:
        logger.warning(f"Groq LLM call skipped/failed: {e}")
        return None


def _parse_json_array(raw_text: str) -> Optional[list]:
    text = raw_text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    start, end = text.find("["), text.rfind("]")
    if start == -1 or end <= start:
        return None
    try:
        data = json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, list) else None


def _valid_question(q: Dict) -> bool:
    options = q.get("options")
    idx = q.get("correct_option_index")
    return (
        isinstance(q, dict)
        and isinstance(q.get("question_text"), str) and q["question_text"].strip() != ""
        and isinstance(options, list) and 2 <= len(options) <= 6
        and all(isinstance(o, str) and o.strip() for o in options)
        and len(set(options)) == len(options)
        and isinstance(idx, int) and 0 <= idx < len(options)
    )


def generate_llm_route_reasoning(
    goal: str,
    skipped: List[str],
    focus: List[str],
    reinforce: List[str]
) -> Optional[str]:
    """
    Uses the Groq LLM to write a short, personalized route explanation.
    Returns None when GROQ_API_KEY is not configured or the call fails (callers fall back).
    """
    prompt = (
        f"Generate a concise 2-sentence route explanation for a learner aiming to: '{goal}'.\n"
        f"- Mastered/Skipped skills: {', '.join(skipped) if skipped else 'None'}\n"
        f"- Skills needing reinforcement: {', '.join(reinforce) if reinforce else 'None'}\n"
        f"- Primary target focus: {', '.join(focus) if focus else 'None'}\n"
        f"Explain clearly why introductory steps were bypassed or where emphasis is placed."
    )
    return _chat(
        [
            {"role": "system", "content": "You are a concise, precise AI learning path advisor. Write professional, encouraging explanations under 50 words."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3, max_tokens=120, timeout=3.5,
    )


def generate_llm_diagnostic_questions(goal: str, skill_names: List[str], count: int = 4) -> Optional[List[Dict]]:
    """
    Generates onboarding diagnostic questions, each tagged with the skill (from skill_names)
    it calibrates. Returns None if the LLM is unavailable or returns unusable output.
    """
    if not skill_names:
        return None
    prompt = (
        f"Write exactly {count} multiple-choice diagnostic questions for a learner aiming to: '{goal}'.\n"
        f"Each question must test ONE of these skills and name it exactly in skill_name: {json.dumps(skill_names)}.\n"
        f"Use 4 plausible options with exactly one correct answer. Practical, intermediate level.\n"
        f'Respond ONLY with a JSON array of objects with keys: "title", "skill_name", "question_text", '
        f'"options", "correct_option_index", "explanation".'
    )
    raw = _chat(
        [
            {"role": "system", "content": "You are a senior technical curriculum author. Output a raw JSON array only."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4, max_tokens=900, timeout=6.0,
    )
    items = _parse_json_array(raw) if raw else None
    if not items:
        return None

    allowed = {name.lower(): name for name in skill_names}
    questions = []
    for i, q in enumerate(items[:count]):
        if not _valid_question(q):
            continue
        skill = allowed.get(str(q.get("skill_name", "")).lower())
        questions.append({
            "id": f"diag_q_{i + 1}",
            "title": q.get("title") or (skill or "Diagnostic"),
            "skill_name": skill,
            "question_text": q["question_text"].strip(),
            "options": [o.strip() for o in q["options"]],
            "correct_option_index": q["correct_option_index"],
            "explanation": q.get("explanation") or "",
        })
    return questions or None


def generate_llm_skill_questions(skill_name: str, difficulty: str = "INTERMEDIATE", count: int = 3) -> Optional[List[Dict]]:
    """
    Generates a short skill-check quiz for a skill not covered by the curated question bank.
    Returns validated dicts with question_text/options/correct_option_index/explanation, or None.
    """
    prompt = (
        f"Write exactly {count} multiple-choice questions that check practical understanding of "
        f"'{skill_name}' at {difficulty.lower()} level. 4 options each, exactly one correct.\n"
        f'Respond ONLY with a JSON array of objects with keys: "question_text", "options", '
        f'"correct_option_index", "explanation".'
    )
    raw = _chat(
        [
            {"role": "system", "content": "You are a senior technical curriculum author. Output a raw JSON array only."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4, max_tokens=900, timeout=6.0,
    )
    items = _parse_json_array(raw) if raw else None
    if not items:
        return None
    questions = [
        {
            "question_text": q["question_text"].strip(),
            "options": [o.strip() for o in q["options"]],
            "correct_option_index": q["correct_option_index"],
            "explanation": q.get("explanation") or "",
        }
        for q in items[:count] if _valid_question(q)
    ]
    return questions or None
