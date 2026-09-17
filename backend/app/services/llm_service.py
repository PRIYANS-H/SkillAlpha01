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
                content = data["choices"][0]["message"]["content"].strip()
                if content:
                    return content
    except Exception as e:
        logger.warning(f"Groq LLM call skipped/failed: {e}")

    return None
