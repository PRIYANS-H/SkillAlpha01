import logging
import httpx
from typing import List, Optional
from app.config import settings

logger = logging.getLogger("skillalpha.llm")

def generate_llm_route_reasoning(
    goal: str,
    skipped: List[str],
    focus: List[str],
    reinforce: List[str]
) -> Optional[str]:
    """
    Uses Groq LLM (Llama-3.3-70b) to generate transparent, personalized route reasoning.
    Falls back gracefully if GROQ_API_KEY is not configured or network call fails.
    """
    api_key = settings.GROQ_API_KEY or settings.LLM_API_KEY
    if not api_key or not api_key.strip():
        return None

    try:
        headers = {
            "Authorization": f"Bearer {api_key.strip()}",
            "Content-Type": "application/json"
        }
        prompt = (
            f"You are SkillAlpha's AI Learning Intelligence Engine. "
            f"Generate a concise 2-sentence route explanation for a learner aiming to: '{goal}'.\n"
            f"- Mastered/Skipped skills: {', '.join(skipped) if skipped else 'None'}\n"
            f"- Skills needing reinforcement: {', '.join(reinforce) if reinforce else 'None'}\n"
            f"- Primary target focus: {', '.join(focus) if focus else 'None'}\n"
            f"Explain clearly why introductory steps were bypassed or where emphasis is placed."
        )
        payload = {
            "model": settings.LLM_MODEL,
            "messages": [
                {"role": "system", "content": "You are a concise, precise AI learning path advisor. Write professional, encouraging explanations under 50 words."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 120
        }
        with httpx.Client(timeout=3.5) as client:
            resp = client.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                if content:
                    return content
    except Exception as e:
        logger.warning(f"Groq LLM call skipped/failed: {e}")

    return None


def generate_llm_diagnostic_questions(goal: str, count: int = 2) -> Optional[List[Dict]]:
    """
    Uses Groq LLM (Llama-3.3-70b) to dynamically generate relevant diagnostic questions for any goal.
    Returns JSON parsed list of question dicts, or None if fallback needed.
    """
    api_key = settings.GROQ_API_KEY or settings.LLM_API_KEY
    if not api_key or not api_key.strip():
        return None

    try:
        headers = {
            "Authorization": f"Bearer {api_key.strip()}",
            "Content-Type": "application/json"
        }
        prompt = (
            f"Generate exactly {count} technical diagnostic multiple-choice questions for a learner aiming to: '{goal}'.\n"
            f"Respond ONLY with a valid JSON array of objects. Do not include markdown codeblocks or extra text.\n"
            f"Structure:\n"
            f"[\n"
            f"  {{\n"
            f'    "id": "diag_q_1",\n'
            f'    "title": "Category Name",\n'
            f'    "question_text": "Practical question?",\n'
            f'    "options": ["Option A", "Option B", "Option C", "Option D"],\n'
            f'    "correct_option_index": 0,\n'
            f'    "explanation": "Why Option A is correct."\n'
            f"  }}\n"
            f"]"
        )
        payload = {
            "model": settings.LLM_MODEL,
            "messages": [
                {"role": "system", "content": "You are a senior technical curriculum author. Output raw JSON array only."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4,
            "max_tokens": 650
        }
        with httpx.Client(timeout=4.5) as client:
            resp = client.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
            if resp.status_code == 200:
                raw_text = resp.json()["choices"][0]["message"]["content"].strip()
                if raw_text.startswith("```"):
                    parts = raw_text.split("```")
                    raw_text = parts[1]
                    if raw_text.startswith("json"):
                        raw_text = raw_text[4:]
                    raw_text = raw_text.strip()
                import json
                questions = json.loads(raw_text)
                if isinstance(questions, list) and len(questions) > 0:
                    return questions
    except Exception as e:
        logger.warning(f"Groq diagnostic question generation failed: {e}")

    return None

