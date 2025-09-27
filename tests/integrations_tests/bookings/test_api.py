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


@pytest.fixture(scope='module')
async def delete_all_bookings(db_module):
    await db_module.bookings.delete()
    await db_module.commit()

@pytest.mark.parametrize('room_id, date_from, date_to, quantity', [
    (1, '2025-09-25', '2025-09-29', 1),
    (1, '2025-09-25', '2025-09-29', 2),
    (1, '2025-09-25', '2025-09-29', 3),
])
async def test_add_and_get_my_bookings(
        room_id,
        date_from,
        date_to,
        quantity,
        delete_all_bookings,
        db,
        authenticated_ac,
):

    response = await authenticated_ac.post(
        '/bookings',
        json={
            'room_id': room_id,
            'date_from': date_from,
            'date_to': date_to,
        }
    )

    assert response.status_code == 200

    bookings_response = await authenticated_ac.get('/bookings/me')
    assert bookings_response.status_code == 200

    bookings = bookings_response.json()

    assert len(bookings) == quantity