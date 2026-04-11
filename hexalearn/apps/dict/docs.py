from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiResponse, OpenApiExample,
)
from drf_spectacular.types import OpenApiTypes
from .serializers import SavedWordListWriteSerializer, SavedWordListSerializer

# ---------------------------------------------------------------------------
# COMMON PARAMETERS
# ---------------------------------------------------------------------------

WORD_PK_PARAM = OpenApiParameter(
    name='word_pk',
    type=OpenApiTypes.INT,
    location=OpenApiParameter.PATH,
    description='Word ID'
)

KANJI_PK_PARAM = OpenApiParameter(
    name='kanji_pk',
    type=OpenApiTypes.INT,
    location=OpenApiParameter.PATH,
    description='Kanji ID'
)

SAVED_WORD_LIST_ID_PARAM = OpenApiParameter(
    name='id',
    type=OpenApiTypes.INT,
    location=OpenApiParameter.PATH,
    description='Saved word list ID',
)

# ---------------------------------------------------------------------------
# PART OF SPEECH
# ---------------------------------------------------------------------------

def part_of_speech_schema():
    return extend_schema_view(
        list=extend_schema(
            tags=['Dictionary - Word'],
            summary='List part-of-speech entries',
            description='Return all part-of-speech entries. language=null means the entry is shared across all languages.',
        ),
        retrieve=extend_schema(
            tags=['Dictionary - Word'],
            summary='Retrieve part-of-speech details',
        ),
        create=extend_schema(
            tags=['Dictionary - Word'],
            summary='Create a new part-of-speech entry',
            description='`code` must be unique within the same language. If language=null, the code must be globally unique.',
        ),
        update=extend_schema(
            tags=['Dictionary - Word'],
            summary='Update a part-of-speech',
        ),
        partial_update=extend_schema(
            tags=['Dictionary - Word'],
            summary='Update a part-of-speech entry',
        ),
        destroy=extend_schema(
            tags=['Dictionary - Word'],
            summary='Delete a part-of-speech entry',
        ),
    )


# ---------------------------------------------------------------------------
# WORD
# ---------------------------------------------------------------------------

def word_schema():
    return extend_schema_view(
        list=extend_schema(
            tags=['Dictionary - Word'],
            summary='List words',
            description='Return a list of words with nested meanings, pronunciations, images, kanji_words, and examples.',
        ),
        retrieve=extend_schema(
            tags=['Dictionary - Word'],
            summary='Retrieve word details',
        ),
        create=extend_schema(
            tags=['Dictionary - Word'],
            summary='Create a new word',
            description="""
Create a new word together with nested data in a single request.
All nested fields are optional.

**Image upload notes:**
1. Call `GET /auth/upload-credential/?app=dict` to get a signature
2. Upload the file to Cloudinary
3. Send the metadata (file_url, file_path, file_name, mime_type) in `word_images[]`
            """,
            examples=[
                OpenApiExample(
                    'Create word 食べる',
                    value={
                        "lemma": "食べる",
                        "language": 1,
                        "level": 1,
                        "part_of_speech": 1,
                        "meanings": [
                            {
                                "language": 3,
                                "short_definition": "eat",
                                "full_definition": "1. eat 2. make a living 3. corrode"
                            }
                        ],
                        "pronunciations": [
                            {"type": "furigana", "pronunciation": "たべる"},
                            {"type": "romaji", "pronunciation": "taberu"}
                        ],
                        "kanji_words": [
                            {"kanji": 1, "reading_in_word": "た"}
                        ],
                        "examples": [
                            {
                                "sentence": "私は毎日朝ごはんを食べる。",
                                "language": 1,
                                "translation": "I eat breakfast every day.",
                                "language_of_translation": 3
                            }
                        ],
                        "word_images": [
                            {
                                "file_url": "https://res.cloudinary.com/xxx/image/upload/dict/words/taberu.jpg",
                                "file_path": "dict/words/taberu",
                                "file_name": "taberu.jpg",
                                "mime_type": "image/jpeg",
                                "alt_text": "Illustration for 食べる",
                                "file_size": 24500
                            }
                        ]
                    },
                    request_only=True,
                )
            ]
        ),
        partial_update=extend_schema(
            tags=['Dictionary - Word'],
            summary='Update basic word fields',
            description='Only lemma, language, level, and part_of_speech can be updated here. Meanings, pronunciations, images, and examples should be managed through their dedicated endpoints.',
            examples=[
                OpenApiExample(
                    'Change level',
                    value={"level": 2},
                    request_only=True,
                )
            ]
        ),
        destroy=extend_schema(
            tags=['Dictionary - Word'],
            summary='Delete a word',
            description='Delete the word and all related data such as meanings, pronunciations, images, and examples.',
        ),
    )


def word_suggest_schema():
    return extend_schema(
        tags=['Dictionary - Word'],
        summary='Realtime word search',
        description='Quickly search by lemma, pronunciation, or meaning. Limited to 10 results.',
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search keyword. Example: たべ, taberu, eat',
                required=True,
            ),
            OpenApiParameter(
                name='language',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Language code for returned meanings. Default: vi',
                required=False,
                examples=[
                    OpenApiExample('Vietnamese', value='vi'),
                    OpenApiExample('English', value='en'),
                ]
            ),
        ],
    )


# ---------------------------------------------------------------------------
# WORD — NESTED
# ---------------------------------------------------------------------------

def word_meaning_schema():
    return extend_schema_view(
        list=extend_schema(
            tags=['Dictionary - Word'],
            summary='List meanings of a word',
            parameters=[WORD_PK_PARAM]
        ),
        retrieve=extend_schema(
            tags=['Dictionary - Word'],
            summary='Retrieve meaning details',
            parameters=[WORD_PK_PARAM]
        ),
        create=extend_schema(
            tags=['Dictionary - Word'],
            summary='Add a new meaning to a word',
            parameters=[WORD_PK_PARAM],
            description='Each word can have only one meaning entry per language.',
            examples=[
                OpenApiExample(
                    'Add Vietnamese meaning',
                    value={
                        "language": 3,
                        "short_definition": "eat",
                        "full_definition": "1. eat 2. make a living 3. corrode"
                    },
                    request_only=True,
                )
            ]
        ),
        partial_update=extend_schema(
            tags=['Dictionary - Word'],
            summary='Update a meaning',
            parameters=[WORD_PK_PARAM]
        ),
        destroy=extend_schema(
            tags=['Dictionary - Word'],
            summary='Delete a meaning',
            parameters=[WORD_PK_PARAM]
        ),
    )


def word_pronunciation_schema():
    return extend_schema_view(
        list=extend_schema(
            tags=['Dictionary - Word'],
            summary='List pronunciations of a word',
            parameters=[WORD_PK_PARAM]
        ),
        retrieve=extend_schema(
            tags=['Dictionary - Word'],
            summary='Retrieve pronunciation details',
            parameters=[WORD_PK_PARAM]
        ),
        create=extend_schema(
            tags=['Dictionary - Word'],
            summary='Add a new pronunciation',
            parameters=[WORD_PK_PARAM],
            description='Each word can have only one pronunciation per type. Furigana should only be used for Japanese words.',
            examples=[
                OpenApiExample(
                    'Add furigana',
                    value={"type": "furigana", "pronunciation": "たべる"},
                    request_only=True,
                ),
                OpenApiExample(
                    'Add romaji',
                    value={"type": "romaji", "pronunciation": "taberu"},
                    request_only=True,
                ),
            ]
        ),
        partial_update=extend_schema(
            tags=['Dictionary - Word'],
            summary='Update a pronunciation',
            parameters=[WORD_PK_PARAM]
        ),
        destroy=extend_schema(
            tags=['Dictionary - Word'],
            summary='Delete a pronunciation',
            parameters=[WORD_PK_PARAM]
        ),
    )


def word_image_schema():
    return extend_schema_view(
        list=extend_schema(
            tags=['Dictionary - Word'],
            summary='List images of a word',
            parameters=[WORD_PK_PARAM]
        ),
        retrieve=extend_schema(
            tags=['Dictionary - Word'],
            summary='Retrieve image details',
            parameters=[WORD_PK_PARAM]
        ),
        create=extend_schema(
            tags=['Dictionary - Word'],
            summary='Add an image to a word',
            parameters=[WORD_PK_PARAM],
            description="""
Receive metadata after the client has uploaded the file to Cloudinary/S3.

**Flow:**
1. `GET /auth/upload-credential/?app=dict` → get signature
2. Upload file to Cloudinary
3. Send file metadata to this endpoint
            """,
            examples=[
                OpenApiExample(
                    'Add image from Cloudinary',
                    value={
                        "file_url": "https://res.cloudinary.com/xxx/image/upload/dict/words/taberu.jpg",
                        "file_path": "dict/words/taberu",
                        "file_name": "taberu.jpg",
                        "mime_type": "image/jpeg",
                        "alt_text": "Illustration",
                        "file_size": 24500
                    },
                    request_only=True,
                )
            ]
        ),
        destroy=extend_schema(
            tags=['Dictionary - Word'],
            summary='Delete an image',
            parameters=[WORD_PK_PARAM]
        ),
    )


def word_example_schema():
    return extend_schema_view(
        list=extend_schema(
            tags=['Dictionary - Word'],
            summary='List example sentences of a word',
            parameters=[WORD_PK_PARAM]
        ),
        retrieve=extend_schema(
            tags=['Dictionary - Word'],
            summary='Retrieve example sentence details',
            parameters=[WORD_PK_PARAM]
        ),
        create=extend_schema(
            tags=['Dictionary - Word'],
            summary='Add an example sentence to a word',
            parameters=[WORD_PK_PARAM],
            examples=[
                OpenApiExample(
                    'Add example sentence',
                    value={
                        "sentence": "私は毎日朝ごはんを食べる。",
                        "language": 1,
                        "translation": "I eat breakfast every day.",
                        "language_of_translation": 3
                    },
                    request_only=True,
                )
            ]
        ),
        partial_update=extend_schema(
            tags=['Dictionary - Word'],
            summary='Update an example sentence',
            parameters=[WORD_PK_PARAM]
        ),
        destroy=extend_schema(
            tags=['Dictionary - Word'],
            summary='Delete an example sentence',
            parameters=[WORD_PK_PARAM]
        ),
    )


def word_kanji_schema():
    return extend_schema_view(
        list=extend_schema(
            tags=['Dictionary - Word'],
            summary='List kanji linked to a word',
            parameters=[WORD_PK_PARAM]
        ),
        retrieve=extend_schema(
            tags=['Dictionary - Word'],
            summary='Retrieve Word-Kanji link details',
            parameters=[WORD_PK_PARAM]
        ),
        create=extend_schema(
            tags=['Dictionary - Word'],
            summary='Add kanji to a word',
            parameters=[WORD_PK_PARAM],
            examples=[
                OpenApiExample(
                    'Add Kanji 食 to 食べる',
                    value={
                        "kanji": 1,
                        "reading_in_word": "た"
                    },
                    request_only=True,
                )
            ]
        ),
        partial_update=extend_schema(
            tags=['Dictionary - Word'],
            summary='Update Word-Kanji link',
            parameters=[WORD_PK_PARAM]
        ),
        destroy=extend_schema(
            tags=['Dictionary - Word'],
            summary='Remove kanji from a word',
            parameters=[WORD_PK_PARAM]
        ),
    )


# ---------------------------------------------------------------------------
# KANJI
# ---------------------------------------------------------------------------

def kanji_schema():
    return extend_schema_view(
        list=extend_schema(
            tags=['Dictionary - Kanji'],
            summary='List kanji',
        ),
        retrieve=extend_schema(
            tags=['Dictionary - Kanji'],
            summary='Retrieve kanji details',
        ),
        create=extend_schema(
            tags=['Dictionary - Kanji'],
            summary='Create a new kanji',
            examples=[
                OpenApiExample(
                    'Create Kanji 食',
                    value={
                        "character": "食",
                        "level": 1,
                        "onyomi": "ショク, ジキ",
                        "kunyomi": "た.べる, く.う",
                        "stroke_count": 9,
                        "meanings": [
                            {"language": 3, "meaning": "eat, food"},
                            {"language": 2, "meaning": "eat, food"}
                        ],
                        "examples": [
                            {
                                "sentence": "食べ物が好きです。",
                                "language": 1,
                                "translation": "I like food.",
                                "language_of_translation": 3
                            }
                        ]
                    },
                    request_only=True,
                )
            ]
        ),
        partial_update=extend_schema(
            tags=['Dictionary - Kanji'],
            summary='Update kanji',
            description='Only basic fields can be updated here: character, level, onyomi, kunyomi, and stroke_count.',
        ),
        destroy=extend_schema(
            tags=['Dictionary - Kanji'],
            summary='Delete kanji',
        ),
    )


def kanji_suggest_schema():
    return extend_schema(
        tags=['Dictionary - Kanji'],
        summary='Realtime kanji search',
        description='Quickly search by character, onyomi, kunyomi, or meaning. Limited to 10 results.',
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Keyword. Example: 食, ショク, た.べる, eat',
                required=True,
            ),
            OpenApiParameter(
                name='language',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Language code for returned meanings. Default: vi',
                required=False,
            ),
        ],
    )


# ---------------------------------------------------------------------------
# KANJI — NESTED
# ---------------------------------------------------------------------------

def kanji_meaning_schema():
    return extend_schema_view(
        list=extend_schema(
            tags=['Dictionary - Kanji'],
            summary='List meanings of a kanji',
            parameters=[KANJI_PK_PARAM]
        ),
        retrieve=extend_schema(
            tags=['Dictionary - Kanji'],
            summary='Retrieve kanji meaning details',
            parameters=[KANJI_PK_PARAM]
        ),
        create=extend_schema(
            tags=['Dictionary - Kanji'],
            summary='Add a new meaning to a kanji',
            description='Each kanji can have only one meaning entry per language.',
            parameters=[KANJI_PK_PARAM],
            examples=[
                OpenApiExample(
                    'Add Vietnamese meaning',
                    value={"language": 3, "meaning": "eat, food"},
                    request_only=True,
                )
            ]
        ),
        partial_update=extend_schema(
            tags=['Dictionary - Kanji'],
            summary='Update a kanji meaning',
            parameters=[KANJI_PK_PARAM]
        ),
        destroy=extend_schema(
            tags=['Dictionary - Kanji'],
            summary='Delete a kanji meaning',
            parameters=[KANJI_PK_PARAM]
        ),
    )


def kanji_example_schema():
    return extend_schema_view(
        list=extend_schema(
            tags=['Dictionary - Kanji'],
            summary='List example sentences of a kanji',
            parameters=[KANJI_PK_PARAM]
        ),
        retrieve=extend_schema(
            tags=['Dictionary - Kanji'],
            summary='Retrieve kanji example details',
            parameters=[KANJI_PK_PARAM]
        ),
        create=extend_schema(
            tags=['Dictionary - Kanji'],
            summary='Add an example sentence to a kanji',
            parameters=[KANJI_PK_PARAM],
            examples=[
                OpenApiExample(
                    'Add example sentence',
                    value={
                        "sentence": "食べ物が好きです。",
                        "language": 1,
                        "translation": "I like food.",
                        "language_of_translation": 3
                    },
                    request_only=True,
                )
            ]
        ),
        partial_update=extend_schema(
            tags=['Dictionary - Kanji'],
            summary='Update an example sentence',
            parameters=[KANJI_PK_PARAM]
        ),
        destroy=extend_schema(
            tags=['Dictionary - Kanji'],
            summary='Delete an example sentence',
            parameters=[KANJI_PK_PARAM],
        ),
    )


def word_pin_schema():
    return extend_schema(
        summary="Pin a word",
        tags=['Dictionary - Word'],
        description="""
Pin a word for the current authenticated user.

Supported behaviors:

1. Send no body:
- Only pin the word
- Do not create or add to any list

2. Send `list_id`:
- Pin the word if not already pinned
- Add the word into an existing list of the current user

3. Send `list_name`:
- Create a new list, then add the word into that new list
- If `list_name` is an empty string, a new list is still created
- Empty list name will be auto-renamed by model logic, for example:
  `New List`, `New List (1)`, `New List (2)`, ...

Notes:
- `list_id` and `list_name` are optional
- Pinning and adding to list are independent actions
- If the word is already pinned, the existing pinned record will be reused
- If the word is already in the target list, no duplicate list item will be created
""",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "list_id": {
                        "type": "integer",
                        "nullable": True,
                        "description": "Existing list ID of current user"
                    },
                    "list_name": {
                        "type": "string",
                        "nullable": True,
                        "description": "New list name. If empty string is sent, a new list is still created and its name will be auto-generated"
                    }
                },
                "examples": {
                    "pin_only": {
                        "summary": "Only pin word",
                        "value": {}
                    },
                    "add_to_existing_list": {
                        "summary": "Add to existing list",
                        "value": {"list_id": 12}
                    },
                    "create_new_list": {
                        "summary": "Create new list",
                        "value": {"list_name": "My favorite words"}
                    }
                }
            }
        },
        responses={
            200: OpenApiResponse(
                description="Success (already existed)",
                examples=[
                    OpenApiExample(
                        "Pin only - already pinned",
                        value={
                            "pinned_word_id": 5,
                            "already_pinned": True
                        },
                    ),
                    OpenApiExample(
                        "Already in list",
                        value={
                            "pinned_word_id": 5,
                            "list_id": 12,
                            "list_name": "My JLPT N3",
                            "item_id": 33,
                            "position": 4,
                            "already_in_list": True
                        },
                    )
                ]
            ),
            201: OpenApiResponse(
                description="Created",
                examples=[
                    OpenApiExample(
                        "Created",
                        value={
                            "pinned_word_id": 5,
                            "list_id": 12,
                            "list_name": "My JLPT N3",
                            "item_id": 34,
                            "position": 5,
                            "already_in_list": False
                        },
                    )
                ]
            ),
        }
    )


def word_my_pinned_schema():
    return extend_schema(
        summary="Get all pinned words of current user",
        tags=['Dictionary - Word'],
        description="""
        Return all words that the current authenticated user has pinned.

        - Require authentication
        - Support pagination
        """,
        responses={
                    200: OpenApiResponse(
                        description="List of pinned words",
                        examples=[
                            OpenApiExample(
                                "Success",
                                value={
                                    "count": 2,
                                    "next": None,
                                    "previous": None,
                                    "results": [
                                        {
                                            "id": 1,
                                            "lemma": "食べる",
                                            "language_name": "Japanese",
                                            "part_of_speech_name": "Verb",
                                            "short_definition": "ăn"
                                        },
                                        {
                                            "id": 2,
                                            "lemma": "飲む",
                                            "language_name": "Japanese",
                                            "part_of_speech_name": "Verb",
                                            "short_definition": "uống"
                                        }
                                    ]
                                }
                            )
                        ]
                    )
        }
    )


def unpin_word_schema():
    return extend_schema(
        tags=["Dictionary - Word"],
        summary="Unpin a word",
        parameters=[
            OpenApiParameter(
                name="id",
                type=int,
                location=OpenApiParameter.PATH,
                description="Word ID to unpin",
            ),
        ],
        description=(
            "Remove a word from the user's pinned words list.\n\n"
            "If the word is not currently pinned, a 404 error will be returned."
        ),
        request=None,  # ❗ không có body
        responses={
            204: OpenApiResponse(
                description="Word successfully unpinned (no content)."
            ),
            403: OpenApiResponse(
                description="User is not authenticated.",
                examples=[
                    OpenApiExample(
                        "Unauthorized",
                        value={
                            "detail": "Authentication credentials were not provided."},
                        response_only=True,
                        status_codes=["403"],
                    ),
                ],
            ),
            404: OpenApiResponse(
                description="Word is not pinned.",
                examples=[
                    OpenApiExample(
                        "Not pinned",
                        value={"detail": "Word is not pinned."},
                        response_only=True,
                        status_codes=["404"],
                    ),
                ],
            ),
        },
        examples=[
            OpenApiExample(
                "Unpin Request",
                summary="Unpin a word by ID",
                value=None,
                request_only=True,
            ),
        ],
    )


def saved_word_list_schema():
    return extend_schema_view(
        # Standard actions
        list=extend_schema(
            tags=['Dictionary - Word'],
            summary='List saved word lists',
            description='Return all saved word lists of the current user.',
        ),
        retrieve=extend_schema(
            tags=['Dictionary - Word'],
            summary='Retrieve a saved word list',
            parameters=[SAVED_WORD_LIST_ID_PARAM],
            responses={200: SavedWordListSerializer},
        ),
        create=extend_schema(
            tags=['Dictionary - Word'],
            summary='Create a saved word list',
            description='Create a new saved word list. If name is empty, auto-generated as "New List".',
            request=SavedWordListWriteSerializer,
            responses={201: SavedWordListSerializer},
        ),
        update=extend_schema(
            tags=['Dictionary - Word'],
            summary='Update a saved word list',
            parameters=[SAVED_WORD_LIST_ID_PARAM],
            request=SavedWordListWriteSerializer,
            responses={200: SavedWordListSerializer},
        ),
        partial_update=extend_schema(
            tags=['Dictionary - Word'],
            summary='Update a saved word list',
            parameters=[SAVED_WORD_LIST_ID_PARAM],
            request=SavedWordListWriteSerializer,
            responses={200: SavedWordListSerializer},
        ),
        destroy=extend_schema(
            tags=['Dictionary - Word'],
            summary='Delete a saved word list',
            parameters=[SAVED_WORD_LIST_ID_PARAM],
        ),
    )


def saved_word_list_reorder_schema():
    return extend_schema(
        tags=["Dictionary - Word"],
        summary="Reorder items in a saved word list",
        parameters=[
            OpenApiParameter("id", int, OpenApiParameter.PATH),
        ],
        description=(
            "Reorder items in a saved word list.\n\n"
            "Only the owner of the list is allowed to reorder.\n\n"
            "Send an array of SavedWordListItem IDs in the new order.\n"
            "Example: `[3, 1, 5, 2, 4]`"
        ),
        request={
            "application/json": {
                "type": "array",
                "items": {"type": "integer"},
                "example": [3, 1, 5, 2, 4],
            }
        },
        responses={
            200: SavedWordListSerializer,
            400: OpenApiResponse(description="Invalid request body or invalid item IDs."),
            403: OpenApiResponse(description="Not the owner of the list."),
            404: OpenApiResponse(description="List not found."),
        },
    )


def saved_word_list_remove_item_schema():
    return extend_schema(
        tags=["Dictionary - Word"],
        summary="Remove an item from a saved word list",
        parameters=[
            OpenApiParameter('id',      int, OpenApiParameter.PATH),
            OpenApiParameter('item_pk', int, OpenApiParameter.PATH),
        ],
        description=(
            "Remove a word from a saved word list.\n\n"
            "- Only the owner can remove items\n"
            "- This only deletes the list item\n"
            "- The word itself is NOT deleted\n"
            "- The pin state (UserPinnedWord) is NOT affected"
        ),
        responses={
            204: OpenApiResponse(description="Item removed successfully."),
            403: OpenApiResponse(description="Permission denied"),
            404: OpenApiResponse(description="Item not found"),
        },
    )
    
def saved_word_list_create_deck_schema():
    return extend_schema(
        tags=["Dictionary - Word"],
        summary="Create a deck from a saved word list",
        parameters=[
            OpenApiParameter(
                name="id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="Saved word list ID",
            ),
        ],
        description="""
Create a flashcard deck from a saved word list.

**Behavior:**
- Each word in the list becomes one card
- `front_text` = word lemma
- `back_text` = meaning (based on user's native language)

**Meaning selection:**
- Automatically uses `request.user.userprofile.native_language`
- If no meaning found → fallback to `word.lemma`

**Definition type:**
- `short` → use `short_definition`
- `full` → use `full_definition` (if available, otherwise fallback to short)

**Notes:**
- Deck is always created as `is_public = False`
- Source is automatically set to `"user"`
- If list is empty → returns `400`
""",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Custom deck title. If not provided, uses list name."
                    },
                    "definition_type": {
                        "type": "string",
                        "enum": ["short", "full"],
                        "default": "short",
                        "description": "Choose which definition to use for card back."
                    },
                },
                "examples": {
                    "default": {
                        "summary": "Create deck with default settings",
                        "value": {}
                    },
                    "custom_title": {
                        "summary": "Custom title",
                        "value": {
                            "title": "My JLPT N5 Deck"
                        }
                    },
                    "full_definition": {
                        "summary": "Use full definitions",
                        "value": {
                            "definition_type": "full"
                        }
                    },
                    "full_custom": {
                        "summary": "Custom everything",
                        "value": {
                            "title": "N4 Study Deck",
                            "definition_type": "full"
                        }
                    }
                }
            }
        },
        responses={
            201: OpenApiResponse(
                description="Deck created successfully",
                examples=[
                    OpenApiExample(
                        "Success",
                        value={
                            "id": 10,
                            "title": "My JLPT N5 Deck",
                            "description": "Created from saved word list: N5 words",
                            "total_cards": 20,
                            "is_public": False,
                            "created_at": "2026-04-04T10:00:00Z",
                            "cards": [
                                {
                                    "id": 1,
                                    "front_text": "食べる",
                                    "back_text": "ăn"
                                },
                                {
                                    "id": 2,
                                    "front_text": "飲む",
                                    "back_text": "uống"
                                }
                            ]
                        },
                        response_only=True,
                        status_codes=["201"],
                    )
                ],
            ),
            400: OpenApiResponse(
                description="Invalid request",
                examples=[
                    OpenApiExample(
                        "Empty list",
                        value={"detail": "Cannot create deck from an empty list."},
                        response_only=True,
                        status_codes=["400"],
                    ),
                    OpenApiExample(
                        "Invalid definition_type",
                        value={"detail": '`definition_type` must be "short" or "full".'},
                        response_only=True,
                        status_codes=["400"],
                    ),
                ],
            ),
            403: OpenApiResponse(
                description="Permission denied"
            ),
            404: OpenApiResponse(
                description="Saved word list not found"
            ),
        },
    )
    
word_ai_schema = extend_schema(
    summary     = 'AI Word Analysis',
    description = """
Stream AI analysis về 1 từ tiếng Nhật.
 
## Modes
 
| Mode | Nội dung |
|------|----------|
| `analyze` | Sắc thái từ, register (formal/casual), mẹo nhớ, phân biệt với từ gần nghĩa, lỗi thường gặp |
| `relations` | Từ đồng nghĩa, trái nghĩa, collocations phổ biến, 3 câu ví dụ ở các level khác nhau |
 
## Response
 
Stream **SSE** — giống Reading AI.
Header `X-AI-Limit-Remaining` trả về số lần còn lại trong ngày.
    """,
    tags        = ['AI'],
    request     = {
        'application/json': {
            'type'      : 'object',
            'required'  : ['mode'],
            'properties': {
                'mode': {
                    'type'       : 'string',
                    'enum'       : ['analyze', 'relations'],
                    'description': 'analyze | relations',
                },
            },
        }
    },
    responses   = {
        200: OpenApiResponse(description = 'SSE stream — text/event-stream'),
        429: OpenApiResponse(description = 'Daily AI limit reached'),
    },
    examples    = [
        OpenApiExample(
            'Analyze — phân tích sâu từ',
            value        = {'mode': 'analyze'},
            request_only = True,
        ),
        OpenApiExample(
            'Relations — đồng nghĩa, trái nghĩa, ví dụ',
            value        = {'mode': 'relations'},
            request_only = True,
        ),
    ],
)

kanji_ai_schema = extend_schema(
    summary     = 'AI Kanji Analysis',
    description = """
Stream AI analysis về 1 kanji.
 
## Modes
 
| Mode | Nội dung |
|------|----------|
| `analyze` | Phân tích bộ thủ (radicals), etymology, mẹo nhớ bằng visual story, hướng dẫn onyomi/kunyomi, kanji hay nhầm lẫn |
| `relations` | Kanji cùng bộ thủ (bảng), compound words (熟語) quan trọng, 3 câu ví dụ với các reading khác nhau |
 
## Response
 
Stream **SSE** — giống Reading AI.
    """,
    tags        = ['AI'],
    request     = {
        'application/json': {
            'type'      : 'object',
            'required'  : ['mode'],
            'properties': {
                'mode': {
                    'type'       : 'string',
                    'enum'       : ['analyze', 'relations'],
                    'description': 'analyze | relations',
                },
            },
        }
    },
    responses   = {
        200: OpenApiResponse(description = 'SSE stream — text/event-stream'),
        429: OpenApiResponse(description = 'Daily AI limit reached'),
    },
    examples    = [
        OpenApiExample(
            'Analyze — phân tích bộ thủ và etymology',
            value        = {'mode': 'analyze'},
            request_only = True,
        ),
        OpenApiExample(
            'Relations — kanji cùng bộ và compound words',
            value        = {'mode': 'relations'},
            request_only = True,
        ),
    ],
)
