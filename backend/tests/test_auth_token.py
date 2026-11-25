from app.core.security import create_access_token, verify_token


def test_create_access_token_returns_decodable_jwt():
    token = create_access_token(subject="admin@smartwork.ai")

    payload = verify_token(token)

    assert payload is not None
    assert payload["sub"] == "admin@smartwork.ai"
    assert "exp" in payload
