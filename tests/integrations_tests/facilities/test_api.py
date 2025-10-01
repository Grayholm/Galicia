import pytest


@pytest.mark.parametrize('title, status_code', [
    ('Wi-Fi', 200),
    ('СПА', 200),
    ('Завтрак', 200),
    ('Красивый вид из окна', 200),

])
async def test_add_facility(ac, title, status_code):
    response = await ac.post("/facilities", json={"title": title})
    assert response.status_code == status_code


async def test_get_facilities(ac):
    response = await ac.get("/facilities")
    assert response.status_code == 200
