import pytest

@pytest.mark.parametrize('title, location, status_code', [
    ('Серп', 'Саратов', 200),
    ('', 'Саратов', 422),
    ('', '', 422),
    (123, 'Саратов', 422),
    ('1244', 'Саратов', 422),
])
async def test_create_hotel(ac, title, location, status_code):
    response = await ac.post(
        "/hotels",
        json={
            'title': title,
            'location': location,
        }
    )

    assert response.status_code == status_code


@pytest.mark.parametrize('date_from, date_to, status_code', [
    ("2025-01-01", "2025-12-31", 200),
    ("2025-02-15", "2025-02-20", 200),
    ("2025-06-01", "2025-06-10", 200),
    ("2025-07-30", "2025-06-30", 400),
    ("2026-08-15", "2026-10-15", 200),
])
async def test_get_hotels(date_from, date_to, status_code, ac):
    response = await ac.get(
        "/hotels",
        params={
            "date_from": date_from,
            "date_to": date_to,
        },
    )
    print(f"{response.json()=}")

    assert response.status_code == status_code
