import json
import logging
from google import genai
from google.genai import types
from .ai_prompts import SYSTEM_INSTRUCTION
 
logger       = logging.getLogger(__name__)
GEMINI_MODEL = "gemini-2.5-flash-lite"
 
 
def get_gemini_client():
    try:
        return genai.Client()
    except ImportError:
        raise ImportError(
            "google-genai is not installed. Run: pip install google-genai"
        )
 
 
def call_gemini_json(user_prompt: str) -> dict | list:
    """
    Gọi Gemini và parse JSON response.
    Trả về dict hoặc list tùy theo prompt.
 
    Dùng cho Deck AI vì cần JSON hoàn chỉnh để tạo cards.
 
    Raises:
        ValueError: nếu response không phải JSON hợp lệ
        Exception:  nếu Gemini API lỗi
    """
    client = get_gemini_client()
 
    response = client.models.generate_content(
        model    = GEMINI_MODEL,
        contents = [user_prompt],
        config   = types.GenerateContentConfig(
            system_instruction = SYSTEM_INSTRUCTION,
            temperature        = 0.8,   # cao hơn 1 chút để tạo variety cho cards
            max_output_tokens  = 4096,  # deck có thể nhiều cards
        ),
    )
 
    raw_text = response.text.strip()
 
    # Strip markdown code block nếu có (đôi khi Gemini vẫn trả về ```json)
    if raw_text.startswith('```'):
        lines    = raw_text.split('\n')
        raw_text = '\n'.join(lines[1:-1])
 
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as e:
        logger.error("Failed to parse Gemini JSON response: %s\nRaw: %s", e, raw_text[:500])
        raise ValueError(f"AI returned invalid JSON: {str(e)}")