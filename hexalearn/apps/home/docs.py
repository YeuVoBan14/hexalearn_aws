# apps/home/docs.py
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from .serializers import LevelSerializer


def level_schema():
    return extend_schema(
        tags=["Level"],
        summary="Quản lý cấp độ học",
        description="CRUD cho Level (N5, N4, Beginner...). "
                    "Chỉ Admin mới có thể tạo, sửa, xóa. "
                    "User thường chỉ được xem.",
        request=LevelSerializer,
        responses={
            200: LevelSerializer,
            201: LevelSerializer,
            400: OpenApiResponse(
                description="Dữ liệu không hợp lệ.",
                examples={
                    "example": {
                        "name": ["This field is required."],
                        "difficulty_rank": ["A valid integer is required."]
                    }
                }
            ),
            401: OpenApiResponse(
                description="Chưa đăng nhập hoặc token không hợp lệ.",
                examples={
                    "example": {
                        "detail": "Authentication credentials were not provided."
                    }
                }
            ),
            403: OpenApiResponse(
                description="Không có quyền thực hiện hành động này. Chỉ Admin mới được phép.",
                examples={
                    "example": {
                        "detail": "You do not have permission to perform this action."
                    }
                }
            ),
            404: OpenApiResponse(
                description="Không tìm thấy Level.",
                examples={
                    "example": {
                        "detail": "Not found."
                    }
                }
            ),
        },
        examples=[
            OpenApiExample(
                "Tạo Level mới",
                summary="Ví dụ tạo Level",
                description="Code sẽ tự động generate từ name nếu không truyền lên",
                value={
                    "name": "N5",
                    "color": "#4CAF50",
                    "difficulty_rank": 1
                },
                request_only=True,
            ),
            OpenApiExample(
                "Response Level",
                summary="Ví dụ response trả về",
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