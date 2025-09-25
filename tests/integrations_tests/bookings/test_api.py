import pytest


@pytest.mark.parametrize('room_id, date_from, date_to, status_code', [
    (1, '2025-09-14', '2025-09-24', 200),
    (1, '2025-09-14', '2025-09-24', 200),
    (1, '2025-09-14', '2025-09-24', 200),
    (1, '2025-09-14', '2025-09-24', 200),
    (1, '2025-09-14', '2025-09-24', 200),
    (1, '2025-09-14', '2025-09-24', 400),
    (1, '2025-09-25', '2025-09-29', 200),
    (1, '2025-09-25', '2025-09-29', 200),
])
async def test_add_booking(
        room_id,
        date_from,
        date_to,
        status_code,
        db,
        authenticated_ac
):
    response = await authenticated_ac.post(
        '/bookings',
        json={
            'room_id': room_id,
            'date_from': date_from,
            'date_to': date_to,
        }
    )

    assert response.status_code == status_code
    if status_code == 200:
        res = response.json()
        assert isinstance(res, dict)
        assert res['status'] == 'OK'
        assert 'data' in res


@pytest.fixture()
async def delete_all_bookings(db, authenticated_ac):
    bookings = await db.bookings.get_all()
    for booking in bookings:
        await authenticated_ac.delete(f'/bookings/{booking.id}')

@pytest.mark.parametrize('room_id, date_from, date_to, status_code, quantity', [
    (1, '2025-09-25', '2025-09-29', 200, 1),
    (1, '2025-09-25', '2025-09-29', 200, 2),
    (1, '2025-09-25', '2025-09-29', 200, 3),
    (1, '2025-09-25', '2025-09-29', 200, 4),
    (1, '2025-09-25', '2025-09-29', 200, 5),
])
async def test_add_and_get_my_bookings(
        delete_all_bookings,
        room_id,
        date_from,
        date_to,
        status_code,
        quantity,
        db,
        authenticated_ac,
):

    user = await db.users.get_one_or_none(email="alexsmith1990@gmail.com")
    user_id = user.id

    response = await authenticated_ac.post(
        '/bookings',
        json={
            'room_id': room_id,
            'date_from': date_from,
            'date_to': date_to,
        }
    )

    assert response.status_code == status_code

    bookings_response = await authenticated_ac.get(f'/bookings/{user_id}')
    assert bookings_response.status_code == 200

    bookings = bookings_response.json()

    assert len(bookings) == quantity