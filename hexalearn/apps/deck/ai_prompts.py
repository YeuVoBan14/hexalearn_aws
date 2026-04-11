# PROMPT FOR CREATING DECK AND CARD ENHANCE

# ---------------------------------------------------------------------------
# SYSTEM INSTRUCTION
# ---------------------------------------------------------------------------
 
SYSTEM_INSTRUCTION = """
You are an expert language teacher and flashcard designer specializing in 
creating effective, memorable flashcards for language learners.
 
Rules:
- Always respond with valid JSON only — no markdown, no explanation outside JSON
- Japanese text must always include furigana in parentheses: 食べる(たべる)
- Cards should be concise — front and back text should be short and clear
- Hints should be helpful but not give away the answer
- Difficulty should match the learner's level
- Generate ONLY the JSON structure requested, nothing else
"""

# ---------------------------------------------------------------------------
# SMART DECK GENERATOR
# Tạo deck từ 1 từ seed — AI tìm các từ cùng semantic field
# ---------------------------------------------------------------------------
 
DECK_GENERATOR_PROMPT = """
Generate a flashcard deck for a {level} level Japanese learner.
 
Seed word: {seed_word} (meaning: {seed_meaning})
Target count: {target_count} cards
Native language for definitions: {native_language}
Theme: Words related to the same semantic field as "{seed_word}"
 
Return ONLY this JSON structure:
{{
    "deck_title": "A short descriptive title for this deck",
    "deck_description": "1-2 sentence description of what this deck covers",
    "cards": [
        {{
            "front_text": "Japanese word with furigana: 食べる(たべる)",
            "back_text": "Meaning in {native_language}",
            "hint": "A helpful hint that doesn't give away the answer"
        }}
    ]
}}
 
Rules for cards:
- front_text: Japanese word/phrase with furigana in parentheses
- back_text: concise meaning in {native_language}, max 10 words
- hint: grammar type, category, or partial clue — NOT the answer
- Include the seed word itself as the first card
- Include words at {level} level and slightly above
- Mix: single words, common phrases, and collocations
- NO duplicate words
- Exactly {target_count} cards
 
Generate {target_count} cards now:
"""
 
 # ---------------------------------------------------------------------------
# DECK ENHANCER — enhance toàn bộ cards trong 1 deck (batch)
# Gọi API 1 lần cho cả batch thay vì từng card
# ---------------------------------------------------------------------------
 
DECK_ENHANCER_PROMPT = """
Enhance these flashcards for a {level} level Japanese learner.
Native language: {native_language}

Cards to enhance:
{cards_json}

Return ONLY a JSON array with the same number of cards, in the same order:
[
    {{
        "id": <original card id>,
        "front_text": "Improved front with furigana",
        "back_text": "Meaning: ...\\nExample: ...\\nTranslation: ...",
        "hint": "Better hint"
    }}
]

Enhancement rules for each card:
- Add furigana if missing: 食べる → 食べる(たべる)
- Make meanings more precise and natural in {native_language}

- back_text MUST include:
  1. Meaning in {native_language}
  2. One short, natural Japanese example sentence using the word
  3. Translation of that example in {native_language}

- Example sentence must:
  - be simple and suitable for a {level} learner
  - clearly demonstrate the meaning of the word

- Keep back_text concise but useful (no long explanations)

- Improve hint:
  - helpful for memory
  - does NOT directly reveal the answer

- Keep front_text concise

- Preserve the card id exactly as given
- Return exactly {card_count} objects in the array
"""

def build_deck_generator_prompt(seed_word_data: dict, target_count: int, user) -> str:
    """
    seed_word_data: {
        'lemma': '食べる',
        'meaning': 'ăn',
    }
    """
    ctx = _build_user_context(user)
    return DECK_GENERATOR_PROMPT.format(
        seed_word    = seed_word_data['lemma'],
        seed_meaning = seed_word_data['meaning'],
        target_count = target_count,
        **ctx,
    )
 
def build_deck_enhancer_prompt(cards: list, user) -> str:
    """
    cards: list of card dicts với id, front_text, back_text, hint
    Dùng cho enhance toàn bộ deck — gọi API 1 lần
    """
    import json
    ctx = _build_user_context(user)
 
    cards_json = json.dumps([
        {
            'id'        : c['id'],
            'front_text': c['front_text'],
            'back_text' : c['back_text'],
            'hint'      : c.get('hint', '') or '',
        }
        for c in cards
    ], ensure_ascii=False, indent=2)
 
    return DECK_ENHANCER_PROMPT.format(
        cards_json = cards_json,
        card_count = len(cards),
        **ctx,
    )
 
 
# ---------------------------------------------------------------------------
# INTERNAL HELPERS
# ---------------------------------------------------------------------------
 
def _build_user_context(user) -> dict:
    native_language = 'Vietnamese'
    level           = 'N5 Beginner'
    try:
        if user.profile.native_language:
            native_language = user.profile.native_language.name
        if user.profile.reading_level:
            level = user.profile.reading_level.name
    except Exception:
        pass
    return {'native_language': native_language, 'level': level}