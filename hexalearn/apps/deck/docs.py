# apps/deck/docs.py
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)
from rest_framework import serializers

from .serializers import (
    CardSerializer,
    DeckCreateSerializer,
    DeckDetailSerializer,
    DeckOverviewSerializer,
    DeckUpdateSerializer,
    FolderSerializer,
    StudyStateSerializer
)

# ─── SHARED ───────────────────────────────────────────────────────────────────

INT_ID = [OpenApiParameter('id', OpenApiTypes.INT, OpenApiParameter.PATH)]

AUTH_401 = OpenApiResponse(
    description="Not logged in or invalid token.",
    examples=[
        OpenApiExample(
            "Unauthorized",
            value={"detail": "Authentication credentials were not provided."}
        )
    ]
)

PERMISSION_403 = OpenApiResponse(
    description="You do not have permission to perform this action.",
    examples=[
        OpenApiExample(
            "Forbidden",
            value={"detail": "You do not have permission to modify this resource."}
        )
    ]
)

NOT_FOUND_404 = OpenApiResponse(
    description="Resource not found.",
    examples=[
        OpenApiExample(
            "Not Found",
            value={"detail": "Not found."}
        )
    ]
)

# ─── FOLDER ───────────────────────────────────────────────────────────────────

def folder_schema():
    return extend_schema_view(
        list=extend_schema(
            summary="List folders",
            description="Get all folders of the authenticated user with decks inside. Supports search by name.",
            parameters=[
                OpenApiParameter('name', str, description='Search folders by name'),
            ],
            responses={
                200: FolderSerializer(many=True),
                401: AUTH_401,
            },
            examples=[
                OpenApiExample(
                    "Folder List Response",
                    value=[
                        {
                            "id": 1,
                            "name": "JLPT N5",
                            "description": "Basic vocabulary for JLPT N5",
                            "created_at": "2024-01-01T00:00:00Z",
                            "updated_at": "2024-01-01T00:00:00Z",
                            "decks": [
                                {"id": 1, "title": "Greetings", "is_public": False, "created_at": "2024-01-01T00:00:00Z"},
                                {"id": 2, "title": "Numbers", "is_public": True, "created_at": "2024-01-02T00:00:00Z"},
                            ]
                        }
                    ],
                    response_only=True,
                )
            ]
        ),
        retrieve=extend_schema(
            tags=['Flashcard'],
            summary="Get folder detail",
            description="Get detail of a specific folder including all decks inside.",
            parameters=INT_ID,
            responses={
                200: FolderSerializer,
                401: AUTH_401,
                404: NOT_FOUND_404,
            },
            examples=[
                OpenApiExample(
                    "Folder Detail Response",
                    value={
                        "id": 1,
                        "name": "JLPT N5",
                        "description": "Basic vocabulary for JLPT N5",
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z",
                        "decks": [
                            {"id": 1, "title": "Greetings", "is_public": False, "created_at": "2024-01-01T00:00:00Z"},
                        ]
                    },
                    response_only=True,
                )
            ]
        ),
        create=extend_schema(
            summary="Create folder",
            description="Create a new folder for organizing decks.",
            request=FolderSerializer,
            responses={
                201: FolderSerializer,
                400: OpenApiResponse(description="Invalid data."),
                401: AUTH_401,
            },
            examples=[
                OpenApiExample(
                    "Create Folder Request",
                    value={
                        "name": "JLPT N5",
                        "description": "Basic vocabulary for JLPT N5",
                    },
                    request_only=True,
                ),
                OpenApiExample(
                    "Create Folder Response",
                    value={
                        "id": 1,
                        "name": "JLPT N5",
                        "description": "Basic vocabulary for JLPT N5",
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z",
                        "decks": [],
                    },
                    response_only=True,
                ),
            ]
        ),
        partial_update=extend_schema(
            summary="Update folder",
            description="Update folder name or description.",
            parameters=INT_ID,
            request=FolderSerializer,
            responses={
                200: FolderSerializer,
                400: OpenApiResponse(description="Invalid data."),
                401: AUTH_401,
                404: NOT_FOUND_404,
            },
            examples=[
                OpenApiExample(
                    "Update Folder Request",
                    value={"name": "JLPT N5 Updated"},
                    request_only=True,
                ),
            ]
        ),
        destroy=extend_schema(
            summary="Delete folder",
            description="Delete a folder. Decks inside will not be deleted — they become unorganized.",
            parameters=INT_ID,
            responses={
                204: OpenApiResponse(description="Folder deleted successfully."),
                401: AUTH_401,
                404: NOT_FOUND_404,
            },
        ),
    )


def folder_overview_schema():
    return extend_schema(
        tags=['Flashcard'],
        summary="Get overview",
        description=(
            "Get all folders with their decks, plus all decks not in any folder. "
            "Used for the home screen to render everything in a single request."
        ),
        responses={
            200: DeckOverviewSerializer,
            401: AUTH_401,
        },
        examples=[
            OpenApiExample(
                "Overview Response",
                value={
                    "folders": [
                        {
                            "id": 1,
                            "name": "JLPT N5",
                            "description": "Basic vocabulary",
                            "created_at": "2024-01-01T00:00:00Z",
                            "updated_at": "2024-01-01T00:00:00Z",
                            "decks": [
                                {"id": 1, "title": "Greetings", "is_public": False, "created_at": "2024-01-01T00:00:00Z"},
                            ]
                        }
                    ],
                    "unorganized_decks": [
                        {"id": 3, "title": "Random Vocab", "is_public": True, "created_at": "2024-01-03T00:00:00Z"},
                    ]
                },
                response_only=True,
            )
        ]
    )


# ─── DECK ─────────────────────────────────────────────────────────────────────

def deck_schema():
    return extend_schema_view(
        list=extend_schema(
            summary="List public decks",
            description="Get all public decks from all users. Supports filtering by name, source, and level.",
            parameters=[
                OpenApiParameter('name', str, description='Search decks by title'),
                OpenApiParameter('source', str, description='Filter by source code, e.g: jlpt, genki'),
                OpenApiParameter('level', str, description='Filter by level code, e.g: n5, n4'),
            ],
            responses={
                200: DeckDetailSerializer(many=True),
                401: AUTH_401,
            },
            examples=[
                OpenApiExample(
                    "Public Deck List Response",
                    value=[
                        {
                            "id": 1,
                            "title": "JLPT N5 Greetings",
                            "description": "Basic Japanese greetings",
                            "source": 1,
                            "source_name": "JLPT",
                            "estimated_level": 1,
                            "estimated_level_name": "N5",
                            "is_public": True,
                            "created_at": "2024-01-01T00:00:00Z",
                            "updated_at": "2024-01-01T00:00:00Z",
                            "cards": []
                        }
                    ],
                    response_only=True,
                )
            ]
        ),
        retrieve=extend_schema(
            summary="Get deck detail",
            description="Get full detail of a deck including all cards. Accessible if the deck is public or owned by the user.",
            parameters=INT_ID,
            responses={
                200: DeckDetailSerializer,
                401: AUTH_401,
                404: NOT_FOUND_404,
            },
            examples=[
                OpenApiExample(
                    "Deck Detail Response",
                    value={
                        "id": 1,
                        "title": "JLPT N5 Greetings",
                        "description": "Basic Japanese greetings",
                        "source": 1,
                        "source_name": "JLPT",
                        "estimated_level": 1,
                        "estimated_level_name": "N5",
                        "is_public": False,
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z",
                        "cards": [
                            {
                                "id": 1,
                                "front_text": "こんにちは",
                                "back_text": "Hello",
                                "hint": "Greeting used during the day",
                                "front_image": "https://res.cloudinary.com/example/image/upload/front.jpg",
                                "back_image": None,
                            }
                        ]
                    },
                    response_only=True,
                )
            ]
        ),
        create=extend_schema(
            summary="Create deck with cards",
            description=(
                "Create a new deck. Must include at least 1 card. "
                "Image fields accept Cloudinary/S3 URLs — upload images directly "
                "from frontend first using the upload-credential endpoint."
            ),
            request=DeckCreateSerializer,
            responses={
                201: DeckDetailSerializer,
                400: OpenApiResponse(
                    description="Invalid data.",
                    examples=[
                        OpenApiExample(
                            "Missing cards",
                            value={"cards": ["This field is required."]}
                        )
                    ]
                ),
                401: AUTH_401,
            },
            examples=[
                OpenApiExample(
                    "Create Deck Request",
                    summary="Create deck with 2 cards",
                    value={
                        "title": "JLPT N5 Greetings",
                        "description": "Basic Japanese greetings",
                        "is_public": False,
                        "cards": [
                            {
                                "front_text": "こんにちは",
                                "back_text": "Hello",
                                "hint": "Daytime greeting",
                                "front_image": "https://res.cloudinary.com/example/image/upload/front1.jpg",
                                "back_image": "https://res.cloudinary.com/example/image/upload/back1.jpg",
                            },
                            {
                                "front_text": "ありがとう",
                                "back_text": "Thank you",
                                "hint": None,
                                "front_image": None,
                                "back_image": None,
                            }
                        ]
                    },
                    request_only=True,
                ),
            ]
        ),
        partial_update=extend_schema(
            summary="Update deck info",
            description="Update basic deck information (title, description, is_public). Does not update cards — use the card sync endpoint instead.",
            parameters=INT_ID,
            request=DeckUpdateSerializer,
            responses={
                200: DeckUpdateSerializer,
                400: OpenApiResponse(description="Invalid data."),
                401: AUTH_401,
                403: PERMISSION_403,
                404: NOT_FOUND_404,
            },
            examples=[
                OpenApiExample(
                    "Update Deck Request",
                    value={
                        "title": "Updated Title",
                        "description": "Updated description",
                        "is_public": True,
                    },
                    request_only=True,
                ),
            ]
        ),
        destroy=extend_schema(
            summary="Delete deck",
            description="Delete a deck and all its cards permanently. Only the owner can delete.",
            parameters=INT_ID,
            responses={
                204: OpenApiResponse(description="Deck deleted successfully."),
                401: AUTH_401,
                403: PERMISSION_403,
                404: NOT_FOUND_404,
            },
        ),
    )


def deck_copy_schema():
    return extend_schema(
        tags=['Flashcard'],
        summary="Copy public deck",
        description=(
            "Copy a public deck into the authenticated user's collection. "
            "All cards will be duplicated. The new deck will be private by default."
        ),
        parameters=INT_ID,
        responses={
            201: DeckDetailSerializer,
            401: AUTH_401,
            404: OpenApiResponse(description="Deck not found or not public."),
        },
        examples=[
            OpenApiExample(
                "Copy Deck Response",
                value={
                    "id": 5,
                    "title": "JLPT N5 Greetings (copy)",
                    "description": "Basic Japanese greetings",
                    "is_public": False,
                    "cards": [
                        {
                            "id": 10,
                            "front_text": "こんにちは",
                            "back_text": "Hello",
                            "hint": "Daytime greeting",
                            "front_image": "https://res.cloudinary.com/example/image/upload/front1.jpg",
                            "back_image": None,
                        }
                    ]
                },
                response_only=True,
            )
        ]
    )


# ─── CARD ─────────────────────────────────────────────────────────────────────

def card_schema():
    return extend_schema_view(
        retrieve=extend_schema(
            summary="Get card detail",
            description="Get detail of a single card by ID. Used when editing a specific card.",
            parameters=INT_ID,
            responses={
                200: CardSerializer,
                401: AUTH_401,
                404: NOT_FOUND_404,
            },
            examples=[
                OpenApiExample(
                    "Card Detail Response",
                    value={
                        "id": 1,
                        "front_text": "こんにちは",
                        "back_text": "Hello",
                        "hint": "Daytime greeting",
                        "front_image": "https://res.cloudinary.com/example/image/upload/front.jpg",
                        "back_image": None,
                    },
                    response_only=True,
                )
            ]
        ),
        update=extend_schema(
            summary="Update card (full)",
            description="Full update of a card. All fields required. Only the deck owner can update.",
            parameters=INT_ID,
            request=CardSerializer,
            responses={
                200: CardSerializer,
                400: OpenApiResponse(description="Invalid data."),
                401: AUTH_401,
                403: PERMISSION_403,
                404: NOT_FOUND_404,
            },
            examples=[
                OpenApiExample(
                    "Full Update Card Request",
                    value={
                        "front_text": "こんにちは",
                        "back_text": "Hello",
                        "hint": "Daytime greeting",
                        "front_image": "https://res.cloudinary.com/example/image/upload/front.jpg",
                        "back_image": None,
                    },
                    request_only=True,
                ),
            ]
        ),
        partial_update=extend_schema(
            summary="Partial update card",
            description="Update one or more fields of a card. Only the deck owner can update.",
            parameters=INT_ID,
            request=CardSerializer,
            responses={
                200: CardSerializer,
                400: OpenApiResponse(description="Invalid data."),
                401: AUTH_401,
                403: PERMISSION_403,
                404: NOT_FOUND_404,
            },
            examples=[
                OpenApiExample(
                    "Partial Update Card Request",
                    value={
                        "front_text": "おはよう",
                        "back_text": "Good morning",
                    },
                    request_only=True,
                ),
                OpenApiExample(
                    "Update image only",
                    value={
                        "front_image": "https://res.cloudinary.com/example/image/upload/new_front.jpg",
                    },
                    request_only=True,
                ),
            ]
        ),
    )


def card_sync_schema():
    return extend_schema(
        tags=['Flashcard'],
        summary="Sync cards in deck",
        description=(
            "Add and/or delete cards in a deck in a single request. "
            "Can be used for add only, delete only, or both at once. "
            "Only the deck owner can sync cards."
        ),
        request=inline_serializer(
            name='CardSyncRequest',
            fields={
                'deck_id': serializers.IntegerField(),
                'add': CardSerializer(many=True, required=False),
                'delete': serializers.ListField(
                    child=serializers.IntegerField(),
                    required=False,
                ),
            }
        ),
        responses={
            200: inline_serializer(
                name='CardSyncResponse',
                fields={
                    'deleted': serializers.IntegerField(),
                    'added': CardSerializer(many=True),
                }
            ),
            400: OpenApiResponse(description="Invalid data."),
            401: AUTH_401,
            404: NOT_FOUND_404,
        },
        examples=[
            OpenApiExample(
                "Add and delete cards",
                summary="Add 1 card and delete 2 cards",
                value={
                    "deck_id": 1,
                    "add": [
                        {
                            "front_text": "さようなら",
                            "back_text": "Goodbye",
                            "hint": "Farewell",
                            "front_image": "https://res.cloudinary.com/example/image/upload/front.jpg",
                            "back_image": None,
                        }
                    ],
                    "delete": [3, 5]
                },
                request_only=True,
            ),
            OpenApiExample(
                "Add cards only",
                value={
                    "deck_id": 1,
                    "add": [
                        {"front_text": "いただきます", "back_text": "Let's eat", "hint": None, "front_image": None, "back_image": None}
                    ]
                },
                request_only=True,
            ),
            OpenApiExample(
                "Delete cards only",
                value={"deck_id": 1, "delete": [3, 5, 7]},
                request_only=True,
            ),
            OpenApiExample(
                "Sync Response",
                value={
                    "deleted": 2,
                    "added": [
                        {
                            "id": 10,
                            "front_text": "さようなら",
                            "back_text": "Goodbye",
                            "hint": "Farewell",
                            "front_image": "https://res.cloudinary.com/example/image/upload/front.jpg",
                            "back_image": None,
                        }
                    ]
                },
                response_only=True,
            ),
        ]
    )


# ─── STUDY ────────────────────────────────────────────────────────────────────

# apps/deck/docs.py

def decks_in_progress_schema():
    return extend_schema(
        tags=['Flashcard'],
        summary="Get decks in progress",
        description=(
            "Get all decks that the user has started studying (has at least 1 StudyState). "
            "Use this to render the 'Continue Learning' section on the home screen. "
            "Do NOT use this to start a study session — use study_session instead."
        ),
        responses={
            200: inline_serializer(
                name='DeckInProgressResponse',
                fields={
                    'deck_id': serializers.IntegerField(),
                    'deck_title': serializers.CharField(),
                    'total_cards': serializers.IntegerField(),
                    'studied_cards': serializers.IntegerField(),
                    'due_today': serializers.IntegerField(),
                    'progress_percent': serializers.IntegerField(),
                }
            ),
            401: AUTH_401,
        },
        examples=[
            OpenApiExample(
                "Decks In Progress Response",
                value=[
                    {
                        "deck_id": 1,
                        "deck_title": "JLPT N5 Greetings",
                        "total_cards": 50,
                        "studied_cards": 30,
                        "due_today": 8,
                        "progress_percent": 60,
                    },
                    {
                        "deck_id": 3,
                        "deck_title": "Genki Chapter 1",
                        "total_cards": 20,
                        "studied_cards": 5,
                        "due_today": 0,
                        "progress_percent": 25,
                    },
                ],
                response_only=True,
            )
        ]
    )


def study_session_schema():
    return extend_schema(
        tags=['Flashcard'],
        summary="Get study session",
        description=(
            "Get all cards to study today for a specific deck. "
            "Returns 2 groups: new cards (never studied) and review cards (due today). "
            "Call this when user taps on a deck to start studying. "
            "Frontend uses this data to render cards one by one — "
            "do NOT call this repeatedly during a session, call it once at the start."
        ),
        parameters=[
            OpenApiParameter(
                'deck_id',
                OpenApiTypes.INT,
                description='ID of the deck to study. Required.',
            ),
        ],
        responses={
            200: inline_serializer(
                name='StudySessionResponse',
                fields={
                    'deck_id': serializers.IntegerField(),
                    'deck_title': serializers.CharField(),
                    'new_cards': StudyStateSerializer(many=True),
                    'review_cards': StudyStateSerializer(many=True),
                    'total': serializers.IntegerField(),
                }
            ),
            400: OpenApiResponse(
                description="deck_id is required.",
                examples=[
                    OpenApiExample(
                        "Missing deck_id",
                        value={"detail": "deck_id is required."}
                    )
                ]
            ),
            401: AUTH_401,
            403: PERMISSION_403,
            404: NOT_FOUND_404,
        },
        examples=[
            OpenApiExample(
                "Study Session Response",
                value={
                    "deck_id": 1,
                    "deck_title": "JLPT N5 Greetings",
                    "new_cards": [
                        {
                            "id": None,
                            "card": 5,
                            "card_front_text": "いただきます",
                            "card_back_text": "Let's eat",
                            "card_hint": None,
                            "card_front_image": None,
                            "card_back_image": None,
                            "repetition": 0,
                            "interval_days": 1,
                            "last_reviewed": None,
                            "last_result": False,
                            "next_review": "2024-01-07",
                            "review_count": 0,
                        }
                    ],
                    "review_cards": [
                        {
                            "id": 1,
                            "card": 1,
                            "card_front_text": "こんにちは",
                            "card_back_text": "Hello",
                            "card_hint": "Daytime greeting",
                            "card_front_image": "https://res.cloudinary.com/example/image/upload/front.jpg",
                            "card_back_image": None,
                            "repetition": 2,
                            "interval_days": 6,
                            "last_reviewed": "2024-01-01T10:00:00Z",
                            "last_result": True,
                            "next_review": "2024-01-07",
                            "review_count": 3,
                        }
                    ],
                    "total": 2,
                },
                response_only=True,
            )
        ]
    )


def submit_review_schema():
    return extend_schema(
        tags=['Flashcard'],
        summary="Submit card review",
        description=(
            "Submit the result of reviewing a single card. "
            "Call this immediately after user flips a card and self-evaluates. "
            "The StudyState will be updated using SM-2 binary algorithm: "
            "result=true means remembered (interval doubles), "
            "result=false means forgot (interval resets to 1 day). "
            "If the card has never been studied, a new StudyState will be created automatically. "
            "For submitting multiple cards at once after an offline session, use bulk_submit instead."
        ),
        request=inline_serializer(
            name='SubmitReviewRequest',
            fields={'result': serializers.BooleanField()}
        ),
        responses={
            200: StudyStateSerializer,
            400: OpenApiResponse(
                description="result field is required.",
                examples=[
                    OpenApiExample(
                        "Missing result",
                        value={"detail": "result is required."}
                    )
                ]
            ),
            401: AUTH_401,
            403: PERMISSION_403,
            404: NOT_FOUND_404,
        },
        examples=[
            OpenApiExample(
                "Remembered",
                summary="User remembered the card",
                value={"result": True},
                request_only=True,
            ),
            OpenApiExample(
                "Forgot",
                summary="User forgot the card",
                value={"result": False},
                request_only=True,
            ),
            OpenApiExample(
                "Submit Review Response — Remembered",
                value={
                    "id": 1,
                    "card": 5,
                    "card_front_text": "こんにちは",
                    "card_back_text": "Hello",
                    "card_hint": "Daytime greeting",
                    "card_front_image": None,
                    "card_back_image": None,
                    "repetition": 3,
                    "interval_days": 12,
                    "last_reviewed": "2024-01-07T10:00:00Z",
                    "last_result": True,
                    "next_review": "2024-01-19",
                    "review_count": 4,
                },
                response_only=True,
            ),
            OpenApiExample(
                "Submit Review Response — Forgot",
                value={
                    "id": 1,
                    "card": 5,
                    "card_front_text": "こんにちは",
                    "card_back_text": "Hello",
                    "card_hint": "Daytime greeting",
                    "card_front_image": None,
                    "card_back_image": None,
                    "repetition": 0,
                    "interval_days": 1,
                    "last_reviewed": "2024-01-07T10:00:00Z",
                    "last_result": False,
                    "next_review": "2024-01-08",
                    "review_count": 5,
                },
                response_only=True,
            ),
        ]
    )


def study_stats_schema():
    return extend_schema(
        tags=['Flashcard'],
        summary="Get study stats for a deck",
        description=(
            "Get study progress statistics for a specific deck. "
            "Use this to render progress bars, charts, or summary screens. "
            "Do NOT use this to start a study session — use study_session instead. "
            "A card is considered 'mastered' when the user has successfully recalled it 5 times in a row (repetition >= 5)."
        ),
        parameters=[
            OpenApiParameter(
                'deck_id',
                OpenApiTypes.INT,
                description='ID of the deck to get stats for. Required.',
            ),
        ],
        responses={
            200: inline_serializer(
                name='StudyStatsResponse',
                fields={
                    'deck_id': serializers.IntegerField(),
                    'deck_title': serializers.CharField(),
                    'total_cards': serializers.IntegerField(),
                    'studied': serializers.IntegerField(),
                    'not_studied': serializers.IntegerField(),
                    'due_today': serializers.IntegerField(),
                    'mastered': serializers.IntegerField(),
                }
            ),
            400: OpenApiResponse(
                description="deck_id is required.",
                examples=[
                    OpenApiExample(
                        "Missing deck_id",
                        value={"detail": "deck_id is required."}
                    )
                ]
            ),
            401: AUTH_401,
            404: NOT_FOUND_404,
        },
        examples=[
            OpenApiExample(
                "Study Stats Response",
                value={
                    "deck_id": 1,
                    "deck_title": "JLPT N5 Greetings",
                    "total_cards": 50,
                    "studied": 30,
                    "not_studied": 20,
                    "due_today": 8,
                    "mastered": 5,
                },
                response_only=True,
            )
        ]
    )
    
deck_ai_generate_schema = extend_schema(
    summary     = 'AI Smart Deck Generator',
    description = """
Tạo 1 deck mới từ **1 từ seed** — AI tự tìm các từ cùng semantic field
và generate toàn bộ cards với furigana, meaning, hint.
 
## Flow
 
```
1. Chọn seed_word_id (Word từ Dictionary)
2. AI tìm {target_count} từ cùng semantic field
3. Tạo Deck + Cards tự động
4. Trả về DeckDetail với toàn bộ cards
```
 
## Ví dụ
 
Seed word: `食べる (ăn)` → AI tạo deck "Food & Eating":
- 食べる(たべる) → ăn
- 飲む(のむ) → uống  
- 料理する(りょうりする) → nấu ăn
- 味わう(あじわう) → thư味わう
- ...
 
## Lưu ý
 
- Response **không streaming** — phải chờ AI xử lý xong (5-15 giây)
- Tối đa 50 cards mỗi lần generate
- Trừ 1 `daily_ai_limit`
- `folder_id` optional — nếu không truyền thì deck không có folder
    """,
    tags        = ['AI'],
    request     = {
        'application/json': {
            'type'      : 'object',
            'required'  : ['seed_word_id'],
            'properties': {
                'seed_word_id': {
                    'type'       : 'integer',
                    'description': 'ID của Word trong Dictionary app làm từ khóa gốc',
                },
                'target_count': {
                    'type'       : 'integer',
                    'minimum'    : 5,
                    'maximum'    : 50,
                    'default'    : 20,
                    'description': 'Số lượng cards muốn tạo',
                },
                'folder_id': {
                    'type'       : 'integer',
                    'nullable'   : True,
                    'description': 'ID folder để gán deck vào (optional)',
                },
            },
        }
    },
    responses   = {
        201: OpenApiResponse(
            description = 'Deck created successfully',
            examples    = [
                OpenApiExample(
                    'Success',
                    value = {
                        'id'         : 10,
                        'title'      : 'Food & Eating Vocabulary',
                        'description': 'Essential vocabulary for food and eating in Japanese',
                        'total_cards': 20,
                        'cards'      : [
                            {
                                'id'        : 1,
                                'front_text': '食べる(たべる)',
                                'back_text' : 'ăn',
                                'hint'      : 'động từ nhóm 2',
                            },
                        ],
                    },
                    response_only = True,
                    status_codes  = ['201'],
                ),
            ],
        ),
        404: OpenApiResponse(description = 'seed_word_id không tồn tại'),
        429: OpenApiResponse(description = 'Daily AI limit reached'),
        502: OpenApiResponse(description = 'AI service error hoặc trả về JSON không hợp lệ'),
    },
    examples    = [
        OpenApiExample(
            'Generate deck từ 食べる',
            value = {
                'seed_word_id': 42,
                'target_count': 20,
                'folder_id'   : 1,
            },
            request_only = True,
        ),
        OpenApiExample(
            'Generate deck không có folder',
            value = {
                'seed_word_id': 42,
                'target_count': 15,
            },
            request_only = True,
        ),
    ],
)
 
# ---------------------------------------------------------------------------
# CARD CONTENT ENHANCER
# ---------------------------------------------------------------------------
 
deck_ai_enhance_schema = extend_schema(
    summary     = 'AI Card Content Enhancer',
    description = """
Enhance toàn bộ (hoặc 1 số) cards trong deck.
 
AI cải thiện:
- Thêm **furigana** nếu thiếu: `食べる` → `食べる(たべる)`
- Làm **meaning** chính xác và tự nhiên hơn trong native language
- Cải thiện **hint** hữu ích hơn mà không spoil đáp án
 
## Batch processing
 
AI xử lý **tất cả cards trong 1 API call** — nhanh hơn gọi từng card.
Tối đa 30 cards mỗi lần. Nếu deck có nhiều hơn 30 cards,
dùng `card_ids` để chỉ định cards cần enhance.
 
## Lưu ý
 
- Response **không streaming** — phải chờ (10-30 giây tùy số lượng cards)
- Trừ 1 `daily_ai_limit` cho toàn bộ batch
- Cards được **update trực tiếp trong DB**
- `card_ids` trống = enhance tất cả cards trong deck
    """,
    tags        = ['AI'],
    request     = {
        'application/json': {
            'type'      : 'object',
            'properties': {
                'card_ids': {
                    'type'       : 'array',
                    'items'      : {'type': 'integer'},
                    'nullable'   : True,
                    'description': 'List card IDs cần enhance. Bỏ trống = enhance tất cả (tối đa 30)',
                },
            },
        }
    },
    responses   = {
        200: OpenApiResponse(
            description = 'Cards enhanced successfully',
            examples    = [
                OpenApiExample(
                    'Success',
                    value = {
                        'enhanced_count'    : 5,
                        'daily_ai_remaining': 14,
                        'cards'             : [
                            {
                                'id'        : 1,
                                'front_text': '食べる(たべる)',
                                'back_text' : 'ăn, tiêu thụ',
                                'hint'      : 'động từ nhóm 2 — て form: 食べて',
                            },
                        ],
                    },
                    response_only = True,
                    status_codes  = ['200'],
                ),
            ],
        ),
        400: OpenApiResponse(description = 'Không có cards hoặc vượt quá 30 cards'),
        403: OpenApiResponse(description = 'Không phải owner của deck'),
        429: OpenApiResponse(description = 'Daily AI limit reached'),
        502: OpenApiResponse(description = 'AI service error'),
    },
    examples    = [
        OpenApiExample(
            'Enhance tất cả cards trong deck',
            value        = {},
            request_only = True,
        ),
        OpenApiExample(
            'Enhance 3 cards cụ thể',
            value        = {'card_ids': [1, 2, 3]},
            request_only = True,
        ),
    ],
)