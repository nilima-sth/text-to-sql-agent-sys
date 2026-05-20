"""Gemini-only LLM helper for the Text-to-SQL workflow."""

from __future__ import annotations

from app.config import GEMINI_API_KEY, MODEL

try:
    import google.generativeai as genai
except ImportError as exc:  # pragma: no cover - runtime dependency issue
    genai = None
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)


def chat_complete(system_prompt: str, user_prompt: str, max_tokens: int = 512, temperature: float = 0.0) -> str:
    """Generate text using Gemini only.

    The system prompt is prepended to the user prompt because the Gemini SDK
    version used here accepts a single prompt string for simple workflows.
    """

    if genai is None:
        raise RuntimeError(
            "Gemini client is not installed. Install `google-generativeai` and rebuild the image."
        ) from _IMPORT_ERROR

    if not GEMINI_API_KEY:
        raise RuntimeError("No Gemini API key configured. Set GEMINI_API_KEY.")

    model = genai.GenerativeModel(
        model_name=MODEL,
        system_instruction=system_prompt,
    )
    response = model.generate_content(
        user_prompt,
        generation_config={
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        },
    )
    text = getattr(response, "text", None)
    if text:
        return text.strip()

    # Fallback for older/newer SDK response shapes.
    candidates = getattr(response, "candidates", None) or []
    if candidates:
        parts = getattr(candidates[0], "content", None)
        if parts and getattr(parts, "parts", None):
            return "".join(getattr(part, "text", "") for part in parts.parts).strip()

    raise RuntimeError("Gemini did not return any text output.")
