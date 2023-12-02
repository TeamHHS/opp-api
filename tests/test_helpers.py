from starlette.exceptions import HTTPException
from src.routers.helpers import check_user_authentication


def test_check_user_authentication():
    valid_user = {"id": 1, "username": "testuser"}
    try:
        check_user_authentication(valid_user)
    except HTTPException as exc:
        assert False, f"Unexpected HTTPException: {exc}"

    invalid_user = None
    try:
        check_user_authentication(invalid_user)
    except HTTPException as exc:
        assert exc.status_code == 401
        assert exc.detail == "Authentication Failed"
