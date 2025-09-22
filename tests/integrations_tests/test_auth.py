from src.services.auth import AuthService


def test_encode_and_decode_access_token():
    data = {'user_id': 1}
    jwt_token = AuthService().create_access_token(data=data)

    assert jwt_token is not None
    assert isinstance(jwt_token, str)

    payload = AuthService().decode_token(jwt_token)
    assert payload is not None
    assert payload['user_id'] == data['user_id']