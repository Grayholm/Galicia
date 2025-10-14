import pytest


@pytest.mark.parametrize(
    "room_id, date_from, date_to, status_code",
    [
        (1, "2030-09-14", "2030-09-24", 200),
        (1, "2030-09-14", "2030-09-24", 200),
        (1, "2030-09-14", "2030-09-24", 200),
        (1, "2030-09-14", "2030-09-24", 200),
        (1, "2030-09-14", "2030-09-24", 200),
        (1, "2030-09-14", "2030-09-24", 409),
        (1, "2030-09-25", "2030-09-29", 200),
        (1, "2030-09-25", "2030-09-29", 200),
    ],
)
async def test_add_booking(room_id, date_from, date_to, status_code, db, authenticated_ac):
    response = await authenticated_ac.post(
        "/bookings",
        json={
            "room_id": room_id,
            "date_from": date_from,
            "date_to": date_to,
        },
    )

    assert response.status_code == status_code
    if status_code == 200:
        res = response.json()
        assert isinstance(res, dict)
        assert res["status"] == "OK"
        assert "data" in res


@pytest.fixture(scope="module")
async def delete_all_bookings(db_module):
    await db_module.bookings.delete()
    await db_module.commit()


async def test_add_and_get_my_bookings(
    delete_all_bookings,
    db,
    authenticated_ac,
):
    quantities = [1, 2, 3]

    for expected_qty in quantities:
        response = await authenticated_ac.post(
            "/bookings",
            json={
                "room_id": 1,
                "date_from": "2026-09-25",
                "date_to": "2026-09-29",
            },
        )
        assert response.status_code == 200

        bookings_response = await authenticated_ac.get("/bookings/me")
        assert bookings_response.status_code == 200

        bookings = bookings_response.json()
        assert len(bookings) == expected_qty
