# PROMPT FOR AI DICTIONARY (WORD/KANJI)

# ---------------------------------------------------------------------------
# SYSTEM INSTRUCTION
# ---------------------------------------------------------------------------
 
SYSTEM_INSTRUCTION = """
You are an expert Japanese language teacher with deep knowledge of linguistics,
etymology, and Japanese culture.
 
Rules:
- Always respond in the user's native language unless showing Japanese examples
- Be concise but thorough
- Always include Japanese text (kanji + furigana) when referencing words
- Format your response clearly with sections
- Provide practical, memorable explanations suitable for the learner's level
"""

# ---------------------------------------------------------------------------
# WORD — ANALYZE
# Phân tích sâu về 1 từ: sắc thái, mẹo nhớ, phân biệt với từ gần nghĩa
# ---------------------------------------------------------------------------
 
WORD_ANALYZE_PROMPT = """
## Context
Learner level: {level}
Native language: {native_language}
 
## Word to analyze:
- Lemma: {lemma}
- Reading: {reading}
- Part of speech: {part_of_speech}
- Known meaning: {meaning}
 
## Task
Provide a deep analysis of this word in {native_language}. Include:
 
### 1. Nuance & Register
- Formality level (casual / neutral / formal / keigo)
- Emotional connotation (positive / negative / neutral)
- When to use this word vs when NOT to use it
- Written vs spoken context
 
### 2. Memory Tip
- A creative mnemonic to remember this word
- Visual association or story if possible
- Sound connection to {native_language} if applicable
 
### 3. Similar Words & How to Distinguish
List 2-3 words with similar meaning and explain the key difference:
- Word (furigana) — how it differs from {lemma}
- A concrete example showing the difference
 
### 4. Common Mistakes
What mistakes do {native_language} speakers commonly make with this word?
 
Keep it practical and memorable for a {level} level learner.
"""

# ---------------------------------------------------------------------------
# WORD — RELATIONS
# Liệt kê từ đồng nghĩa, trái nghĩa và câu ví dụ
# ---------------------------------------------------------------------------
 
WORD_RELATIONS_PROMPT = """
## Context
Learner level: {level}
Native language: {native_language}
 
## Target word:
- Lemma: {lemma}
- Reading: {reading}
- Part of speech: {part_of_speech}
- Meaning: {meaning}
 
## Task
In {native_language}, provide the following:
 
### 1. Synonyms (同義語)
List 3-5 synonyms with:
- Word (furigana) | Meaning in {native_language} | Key difference from {lemma}
 
### 2. Antonyms (反対語)
List 2-3 antonyms with:
- Word (furigana) | Meaning in {native_language}
 
### 3. Common Collocations
List 5 natural word combinations (collocations) using {lemma}:
- Collocation + meaning in {native_language}
- Example: 〜を食べる → natural usage
 
### 4. Example Sentences
Provide 3 example sentences at different levels:
- **Basic ({level})**: Simple sentence with furigana + {native_language} translation
- **Natural**: A natural conversational sentence + translation  
- **Advanced**: A more complex sentence + translation
 
Each sentence should show a different usage or nuance of the word.
"""
 
# ---------------------------------------------------------------------------
# KANJI — ANALYZE
# Phân tích sâu về 1 kanji: cấu trúc, bộ thủ, mẹo nhớ
# ---------------------------------------------------------------------------
 
KANJI_ANALYZE_PROMPT = """
## Context
Learner level: {level}
Native language: {native_language}
 
## Kanji to analyze:
- Character: {character}
- Onyomi: {onyomi}
- Kunyomi: {kunyomi}
- Stroke count: {stroke_count}
- Meaning: {meaning}
 
## Task
Provide a deep analysis of this kanji in {native_language}. Include:
 
### 1. Structure Breakdown
- What radicals (部首) make up this kanji?
- Explain each radical and its meaning
- How do the radicals combine to hint at the overall meaning?
 
### 2. Etymology & Origin
- Brief history or origin of this kanji
- How did the original pictograph evolve into the modern form?
 
### 3. Memory Tip
- A creative story or visual mnemonic using the radical breakdown
- Make it memorable and relevant for a {native_language} speaker
 
### 4. Reading Guide
- When to use onyomi vs kunyomi — give the general rule
- List the most common and useful readings with example words:
  - Onyomi examples: 2-3 common compound words
  - Kunyomi examples: 2-3 common standalone words
 
### 5. Common Mistakes
- Easily confused with which other kanji? Explain how to tell apart.
- Common reading mistakes learners make
"""
 
# ---------------------------------------------------------------------------
# KANJI — RELATIONS
# Các kanji có bộ thủ giống + câu ví dụ liên quan đến kanji gốc
# ---------------------------------------------------------------------------
 
KANJI_RELATIONS_PROMPT = """
## Context
Learner level: {level}
Native language: {native_language}
 
## Target kanji:
- Character: {character}
- Meaning: {meaning}
- Radicals: {radicals_hint}
 
## Task
In {native_language}, provide:
 
### 1. Kanji with Same or Similar Radicals
List 5-7 kanji that share radicals with {character}:
 
| Kanji | Reading | Meaning | Shared Radical | Notes |
|-------|---------|---------|----------------|-------|
 
Group them by which radical they share if possible.
 
### 2. Kanji Family (Same Radical Group)
If {character} contains a major radical, list other kanji in the same family:
- How does the shared radical influence their meanings?
- Pattern recognition tip to remember the group
 
### 3. Common Compound Words (熟語)
List 8 important compound words containing {character}:
 
| Word | Reading | Meaning | Level |
|------|---------|---------|-------|
 
Include a mix of JLPT levels if possible.
 
### 4. Example Sentences
3 example sentences featuring {character} in different compound words:
- Sentence (with furigana on kanji)
- {native_language} translation
- Which reading of {character} is used and why
"""

def build_word_analyze_prompt(word, user) -> str:
    context = _build_word_context(word, user)
    return WORD_ANALYZE_PROMPT.format(**context)

def build_word_relations_prompt(word, user) -> str:
    context = _build_word_context(word, user)
    return WORD_RELATIONS_PROMPT.format(**context)

def build_kanji_analyze_prompt(kanji, user) -> str:
    context = _build_kanji_context(kanji, user)
    return KANJI_ANALYZE_PROMPT.format(**context)

def build_kanji_relations_prompt(kanji, user) -> str:
    context = _build_kanji_context(kanji, user)
    return KANJI_RELATIONS_PROMPT.format(**context)

def _build_user_context(user) -> dict:
    native_language = "Vietnamese"
    level = "N5 Beginner"
    
    try:
        if user.profile.native_language:
            native_language = user.profile.native_language.name
        if user.profile.reading_level:
            level = user.profile.reading_level.name
    except Exception:
        pass
    return {'native_language': native_language, 'level': level}

def _build_word_context(word, user) -> dict:
    ctx = _build_user_context(user)
    
    #Get word pronunciation, priority fugigana
    reading = ''
    furigana = word.pronunciations.filter(type='furigana').first()
    romaji   = word.pronunciations.filter(type='romaji').first()
    if furigana:
        reading = furigana.pronunciation
    elif romaji:
        reading = romaji.pronunciation
        
    #Get word meaning
    meaning = ''
    lang_meaning = word.meanings.filter(
        language__name=ctx['native_language']
    ).first()
    if not lang_meaning:
        lang_meaning = word.meaning.first()
    if lang_meaning:
        meaning = lang_meaning.short_definition
        
    ctx.update({
        'lemma': word.lemma,
        'reading':reading or 'N/A',
        'part_of_speech': word.part_of_speech.name if word.part_of_speech else 'N/A',
        'meaning': meaning or 'N/A',
    })
    return ctx

def _build_kanji_context(kanji, user) -> dict:
    ctx = _build_user_context(user)
    
    #Get kanji meaning
    meaning = ''
    kanji_meaning = kanji.meanings.filter(
        language__name=ctx['native_language']
    ).first()
    if not kanji_meaning:
        kanji_meaning = kanji.meanings.first()
    if kanji_meaning:
        meaning = kanji_meaning
        
    # radicals_hint — gợi ý bộ thủ từ character nếu không có field riêng
    radicals_hint = f"Please identify the radicals in {kanji.character}"
    
    ctx.update({
        'character': kanji.character,
        'onyomi': kanji.onyomi,
        'kunyomi': kanji.kunyomi,
        'stroke_count': kanji.stroke_count,
        'meaning': meaning or "N/A",
        'radicals_hint': radicals_hint
    })
    return ctx
        
    
        
        
