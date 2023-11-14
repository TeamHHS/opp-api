from starlette.exceptions import HTTPException
from src.routers.helpers import check_user_authentication

def test_check_user_authentication():
    # Test case 1: Valid user
    valid_user = {"id": 1, "username": "testuser"}
    try:
        check_user_authentication(valid_user)
    except HTTPException as exc:
        # If authentication fails, the test should fail
        assert False, f"Unexpected HTTPException: {exc}"

    # Test case 2: Invalid user (None)
    invalid_user = None
    try:
        check_user_authentication(invalid_user)
    except HTTPException as exc:
        # Check if the HTTPException has the expected status code and detail message
        assert exc.status_code == 401
        assert exc.detail == 'Authentication Failed'