# apps/home/docs.py
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from .serializers import LevelSerializer, SourceSerializer


def level_schema():
    return extend_schema(
        tags=["Level"],
        summary="Manage learning levels",
        description="CRUD for Level (N5, N4, Beginner...). "
                    "Only Admin can create, edit, delete. "
                    "Regular users can only view.",
        request=LevelSerializer,
        responses={
            200: LevelSerializer,
            201: LevelSerializer,
            400: OpenApiResponse(
                description="Invalid data.",
                examples={
                    "example": {
                        "name": ["This field is required."],
                        "difficulty_rank": ["A valid integer is required."]
                    }
                }
            ),
            401: OpenApiResponse(
                description="Not logged in or invalid token.",
                examples={
                    "example": {
                        "detail": "Authentication credentials were not provided."
                    }
                }
            ),
            403: OpenApiResponse(
                description="No permission to perform this action. Only Admin is allowed.",
                examples={
                    "example": {
                        "detail": "You do not have permission to perform this action."
                    }
                }
            ),
            404: OpenApiResponse(
                description="Level not found.",
                examples={
                    "example": {
                        "detail": "Not found."
                    }
                }
            ),
        },
        examples=[
            OpenApiExample(
                "Create new Level",
                summary="Example of creating Level",
                description="Code will be automatically generated from name if not provided",
                value={
                    "name": "N5",
                    "color": "#4CAF50",
                    "difficulty_rank": 1
                },
                request_only=True,
            ),
            OpenApiExample(
                "Level Response",
                summary="Example of response returned",
                value={
                    "id": 1,
                    "name": "N5",
                    "code": "n5",
                    "color": "#4CAF50",
                    "difficulty_rank": 1,
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z"
                },
                response_only=True,
            ),
        ]
    )


def source_schema():
    return extend_schema(
        tags=["Level"],
        summary="Manage sources",
        description="CRUD for Source. "
                    "Only Admin can create, edit, delete. "
                    "Regular users can only view.",
        request=SourceSerializer,
        responses={
            200: SourceSerializer,
            201: SourceSerializer,
            400: OpenApiResponse(
                description="Invalid data.",
                examples={
                    "example": {
                        "name": ["This field is required."]
                    }
                }
            ),
            401: OpenApiResponse(
                description="Not logged in or invalid token.",
                examples={
                    "example": {
                        "detail": "Authentication credentials were not provided."
                    }
                }
            ),
            403: OpenApiResponse(
                description="No permission to perform this action. Only Admin is allowed.",
                examples={
                    "example": {
                        "detail": "You do not have permission to perform this action."
                    }
                }
            ),
            404: OpenApiResponse(
                description="Source not found.",
                examples={
                    "example": {
                        "detail": "Not found."
                    }
                }
            ),
        },
        examples=[
            OpenApiExample(
                "Create new Source",
                summary="Example of creating Source",
                description="Code will be automatically generated from name if not provided",
                value={
                    "name": "Example Source",
                    "color": "#4CAF50"
                },
                request_only=True,
            ),
            OpenApiExample(
                "Source Response",
                summary="Example of response returned",
                value={
                    "id": 1,
                    "name": "Example Source",
                    "code": "example-source",
                    "color": "#4CAF50",
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z"
                },
                response_only=True,
            ),
        ]
    )