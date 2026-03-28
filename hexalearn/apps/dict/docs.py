from drf_spectacular.utils import (
    extend_schema, extend_schema_view,
    OpenApiParameter, OpenApiResponse, OpenApiExample,
)
from drf_spectacular.types import OpenApiTypes
from .serializers import SavedWordListWriteSerializer, SavedWordListSerializer, ReorderItemSerializer

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
- Add the pinned word into an existing list of the current user

3. Send `list_name`:
- Create a new list, then add the pinned word into that new list
- If `list_name` is an empty string, a new list is still created
- Empty list name will be auto-renamed by model logic, for example:
  `New List`, `New List (1)`, `New List (2)`, ...

Notes:
- `list_id` and `list_name` are optional
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
                        "description": "New list name. If empty string is sent, a new list is still created and its name will be auto-generated, e.g. 'New List'"
                    }
                },
                "examples": {
                    "pin_only": {
                        "summary": "Only pin word",
                        "description": "No body sent. Only create/reuse UserPinnedWord, do not add into any list.",
                        "value": {}
                    },
                    "add_to_existing_list": {
                        "summary": "Add to existing list",
                        "description": "Use an existing list of the current user.",
                        "value": {
                            "list_id": 12
                        }
                    },
                    "create_new_list": {
                        "summary": "Create new list with provided name",
                        "description": "Create a new list, then add pinned word into it.",
                        "value": {
                            "list_name": "My favorite words"
                        }
                    },
                    "create_new_list_empty_name": {
                        "summary": "Create new list with empty name",
                        "description": "A new list is still created. Empty name will be auto-renamed by model logic, e.g. 'New List'.",
                        "value": {
                            "list_name": ""
                        }
                    }
                }
            }
        },
        responses={
            200: OpenApiResponse(
                description="Success. Resource already existed, so no new object was created.",
                examples=[
                    OpenApiExample(
                        "Pin only - already pinned",
                        value={
                            "pinned_word_id": 5,
                            "already_pinned": True
                        },
                        response_only=True,
                        status_codes=["200"]
                    ),
                    OpenApiExample(
                        "Already in existing list",
                        value={
                            "pinned_word_id": 5,
                            "list_id": 12,
                            "list_name": "My JLPT N3",
                            "item_id": 33,
                            "position": 4,
                            "already_in_list": True
                        },
                        response_only=True,
                        status_codes=["200"]
                    )
                ]
            ),
            201: OpenApiResponse(
                description="Success. New pin and/or new list item was created.",
                examples=[
                    OpenApiExample(
                        "Pin only - created",
                        value={
                            "pinned_word_id": 5,
                            "already_pinned": False
                        },
                        response_only=True,
                        status_codes=["201"]
                    ),
                    OpenApiExample(
                        "Added to existing list",
                        value={
                            "pinned_word_id": 5,
                            "list_id": 12,
                            "list_name": "My JLPT N3",
                            "item_id": 34,
                            "position": 5,
                            "already_in_list": False
                        },
                        response_only=True,
                        status_codes=["201"]
                    ),
                    OpenApiExample(
                        "Created new named list and added item",
                        value={
                            "pinned_word_id": 5,
                            "list_id": 20,
                            "list_name": "My favorite words",
                            "item_id": 50,
                            "position": 1,
                            "already_in_list": False
                        },
                        response_only=True,
                        status_codes=["201"]
                    ),
                    OpenApiExample(
                        "Created new auto-named list from empty list_name",
                        value={
                            "pinned_word_id": 5,
                            "list_id": 21,
                            "list_name": "New List",
                            "item_id": 51,
                            "position": 1,
                            "already_in_list": False
                        },
                        response_only=True,
                        status_codes=["201"]
                    )
                ]
            ),
            400: OpenApiResponse(
                description="Invalid request body"
            ),
            401: OpenApiResponse(
                description="Authentication required"
            ),
            404: OpenApiResponse(
                description="List not found or does not belong to current user",
                examples=[
                    OpenApiExample(
                        "List not found",
                        value={
                            "detail": "List not found or not belong to you"
                        },
                        response_only=True,
                        status_codes=["404"]
                    )
                ]
            )
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
    
def saved_word_list_schema():
    return extend_schema(
        tags=["Dictionary - Word"],
        summary="Manage saved word lists",
        description=(
            "CRUD operations for SavedWordList. "
            "Users can only create, update, and delete their own lists. "
            "Public lists from other users can be viewed via GET.\n\n"

            "**POST** — Create a new list. "
            "If `name` is not provided, it will be automatically set to "
            "`New List`, `New List (1)`, ...\n\n"

            "**PATCH** — Update basic fields: `name`, `description`, `is_public`."
        ),
        request=SavedWordListWriteSerializer,
        responses={
            200: SavedWordListSerializer,
            201: SavedWordListSerializer,
            400: OpenApiResponse(description="Invalid data."),
            401: OpenApiResponse(
                description="Not authenticated or invalid token.",
                examples={"example": {"detail": "Authentication credentials were not provided."}}
            ),
            403: OpenApiResponse(
                description="Permission denied.",
                examples={"example": {"detail": "You do not have permission to perform this action."}}
            ),
            404: OpenApiResponse(
                description="List not found.",
                examples={"example": {"detail": "Not found."}}
            ),
        },
        examples=[
            OpenApiExample(
                "Create Request",
                value={"name": "N5 words to review", "description": "Common forgotten N5 words", "is_public": False},
                request_only=True,
            ),
            OpenApiExample(
                "Create Request (auto name)",
                summary="No name provided → auto-generated name",
                value={"is_public": False},
                request_only=True,
            ),
            OpenApiExample(
                "Response",
                value={
                    "id": 1,
                    "name": "N5 words to review",
                    "description": "Common forgotten N5 words",
                    "is_public": False,
                    "word_count": 2,
                    "items": [
                        {"id": 1, "pinned_word": 3, "word_id": 42, "lemma": "食べる", "language": "Japanese", "position": 1},
                        {"id": 2, "pinned_word": 5, "word_id": 18, "lemma": "飲む",   "language": "Japanese", "position": 2},
                    ],
                    "created_at": "2026-03-26T06:00:00Z",
                },
                response_only=True,
            ),
        ],
    )
def saved_word_list_reorder_schema():
    return extend_schema(
        tags=["Dictionary - Word"],
        summary="Reorder items in a saved word list",
        description=(
            "Update the `position` of multiple items at once. "
            "Only the owner of the list is allowed to reorder.\n\n"

            "Send an array of `{id, position}` objects. "
            "You do not need to include all items, only those whose positions should change."
        ),
        request=ReorderItemSerializer(many=True),
        responses={
            200: SavedWordListSerializer,
            400: OpenApiResponse(
                description="Item does not belong to this list.",
                examples={"example": {"detail": "Items not found in this list: [5]"}}
            ),
            403: OpenApiResponse(
                description="Not the owner of the list.",
                examples={"example": {"detail": "You do not have permission to reorder this list."}}
            ),
            404: OpenApiResponse(
                description="List not found.",
                examples={"example": {"detail": "Not found."}}
            ),
        },
        examples=[
            OpenApiExample(
                "Reorder Request",
                value=[
                    {"id": 3, "position": 1},
                    {"id": 1, "position": 2},
                    {"id": 5, "position": 3},
                ],
                request_only=True,
            ),
        ],
    )
    
def saved_word_list_remove_item_schema():
    return extend_schema(
        tags=["Dictionary - Word"],
        summary="Remove an item from a saved word list",
        description=(
            "Remove a word from a saved word list.\n\n"
            "- Only the owner of the list can remove items.\n"
            "- This action only removes the `SavedWordListItem` from the list.\n"
            "- The underlying `UserPinnedWord` record is not deleted."
        ),
        responses={
            204: OpenApiResponse(description="Item removed successfully."),
            403: OpenApiResponse(
                description="You do not have permission to modify this list.",
                examples={
                    "example": {
                        "detail": "You do not have permission to modify this list."
                    }
                }
            ),
            404: OpenApiResponse(
                description="Item not found.",
                examples={
                    "example": {
                        "detail": "Item not found."
                    }
                }
            ),
        },
        examples=[
            OpenApiExample(
                "Success Response",
                summary="Item removed successfully",
                value=None,
                response_only=True,
                status_codes=["204"],
            ),
            OpenApiExample(
                "Forbidden Response",
                summary="Current user is not the owner of the list",
                value={
                    "detail": "You do not have permission to modify this list."
                },
                response_only=True,
                status_codes=["403"],
            ),
            OpenApiExample(
                "Not Found Response",
                summary="Item does not exist in this list",
                value={
                    "detail": "Item not found."
                },
                response_only=True,
                status_codes=["404"],
            ),
        ],
    )