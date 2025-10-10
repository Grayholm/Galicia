import pytest


@pytest.mark.parametrize(
    "title, location, status_code",
    [
        ("Серп", "Саратов", 200),
        ("", "Саратов", 400),
        ("", "", 400),
        (123, "Саратов", 400),
        ("1244", "Саратов", 400),
    ],
)
async def test_create_hotel(ac, title, location, status_code):
    response = await ac.post(
        "/hotels",
        json={
            "title": title,
            "location": location,
        },
    )

    assert response.status_code == status_code


@pytest.mark.parametrize(
    "date_from, date_to, status_code",
    [
        ("2025-01-01", "2025-12-31", 200),
        ("2025-02-15", "2025-02-20", 200),
        ("2025-06-01", "2025-06-10", 200),
        ("2025-07-30", "2025-06-30", 400),
        ("2026-08-15", "2026-10-15", 200),
    ],
)
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


@pytest.mark.parametrize(
    "hotel_id, title, location, status_code",
    [
        (4, "Молот", "Пекин", 200),
        (4, "", "Пекин", 400),
        (4, "Молот", "", 400),
        (4, "", "", 400),
        (346, "Молот", "Пекин", 404),
    ],
)
async def test_update_hotel(hotel_id: int, title: str, location: str, status_code, ac):
    response = await ac.put(
        f"/hotels/{hotel_id}",
        json={
            "title": title,
            "location": location,
        },
    )

    assert response.status_code == status_code

    if response.status_code == 200:
        hotel_data = await ac.get(f"/hotels/{hotel_id}")

        hotel = hotel_data.json()

        assert hotel["title"] == title
        assert hotel["location"] == location


@pytest.mark.parametrize(
    "hotel_id, title, location, status_code",
    [
        (4, "Человек", "Паук", 200),
        (4, "", "Паук", 200),
        (4, "Человек", "", 200),
        (4, "", "", 400),
        (4143, "Человек", "Паук", 404),
    ],
)
async def test_partially_update_hotel(hotel_id: int, title: str, location: str, status_code, ac):
    response = await ac.patch(
        f"/hotels/{hotel_id}",
        json={
            "title": title,
            "location": location,
        },
    )

    assert response.status_code == status_code

    if response.status_code == 200:
        hotel_data = await ac.get(f"/hotels/{hotel_id}")

        hotel = hotel_data.json()

        assert hotel["title"] == title
        assert hotel["location"] == location
