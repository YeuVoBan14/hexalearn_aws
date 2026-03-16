# apps/home/docs.py
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from .serializers import LevelSerializer, SourceSerializer, UserProfileSerializer


def level_schema():
    return extend_schema(
        tags=["Home"],
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
        tags=["Home"],
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


def user_profile_schema():
    return extend_schema(
        tags=["Home"],
        summary="Get and update user profile",
        description="Retrieve and update the authenticated user's profile information.",
        request=UserProfileSerializer,
        responses={
            200: UserProfileSerializer,
            400: OpenApiResponse(
                description="Invalid data.",
                examples={
                    "example": {
                        "native_language": ["Invalid choice."]
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
        },
        examples=[
            OpenApiExample(
                "Update Profile",
                summary="Example of updating profile",
                description="Update user profile fields like username, first_name, last_name, phone_number, address, date_of_birth, profile_picture, native_language",
                value={
                    "username": "newusername",
                    "first_name": "John",
                    "last_name": "Doe",
                    "phone_number": "+1234567890",
                    "address": "123 Main St",
                    "date_of_birth": "1990-01-01",
                    "native_language": "en"
                },
                request_only=True,
            ),
            OpenApiExample(
                "Profile Response",
                summary="Example of profile response",
                value={
                    "user_id": 1,
                    "username": "exampleuser",
                    "email": "user@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "native_language": "en",
                    "daily_ai_limit": 20,
                    "reading_level_name": "N5",
                    "reading_level_color": "#4CAF50",
                    "created_at": "2024-01-01T00:00:00Z",
                    "image_url": "https://example.com/media/profile_pics/avatar.jpg"
                },
                response_only=True,
            ),
        ]
    )


def delete_account_schema():
    return extend_schema(
        tags=["User"],
        summary="Delete user account",
        description="Soft delete the authenticated user's account.",
        responses={
            200: OpenApiResponse(
                description="Account deleted successfully.",
                examples={
                    "example": {
                        "detail": "Account has been deleted."
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
        }
    )
