from src.services.auth import AuthService


def test_create_access_token():
    data = {"user": 1}
    jwt_token = AuthService().create_access_token(data=data)

    assert jwt_token is not None
    assert isinstance(jwt_token, str)
