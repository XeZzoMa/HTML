from fastapi import HTTPException, status


def not_found(entity: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"message": f"{entity} not found", "details": None},
    )


def bad_request(message: str, details: dict | None = None) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={"message": message, "details": details},
    )
