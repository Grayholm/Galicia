import pytest
import logging

from src.api.dependencies import RoomsFilterDep

"""
Применяется для одиночного тестирования функции с комнатами. Закомментите, если делаете все тесты
"""
@pytest.mark.parametrize('title, status_code', [
    ('Wi-Fi', 200),
    ('СПА', 200),
    ('Завтрак', 200),
    ('Красивый вид из окна', 200),

])
async def test_add_facility(ac, title, status_code):
    response = await ac.post("/facilities", json={"title": title})
    assert response.status_code == status_code



@pytest.mark.parametrize('hotel_id, title, description, price, quantity, facilities_ids, status_code', [
    (1, 'Имба_0', 'Имбище комната отвечаю', 1599, 2, [1], 200),
    (2, 'Имба_1', '', 2990, 3, [2], 200),
    (1, 'Имба_2', 'dfgdh', 15999, 5, [], 200),
    (1, '', 'dfgdh', 15999, 5, [4], 400),
    (1, '123', 'dfgdh', 15999, 5, [4], 400),
    (1, '   ', 'dfgdh', 15999, 5, [4], 400),
    (142, 'Rus', 'dfgdh', 15999, 5, [1,4], 404),
])
async def test_create_room(
        ac,
        hotel_id,
        title,
        description,
        price,
        quantity,
        facilities_ids,
        status_code,
):
    response = await ac.post(
        f"/hotels/{hotel_id}/rooms",
        json={
            'title': title,
            'description': description,
            'price': price,
            'quantity': quantity,
            'facilities_ids': facilities_ids,
        }
    )

    assert response.status_code == status_code


@pytest.mark.parametrize('hotel_id, filters, date_from, date_to, status_code', [
    (1, {"title": "Имба_0", "price_min": 1000, "price_max": 5000}, "2025-01-01", "2025-12-31", 200),
    (1, {"price_min": 500}, "2025-01-01", "2025-12-31", 200),
    (1, {}, "2025-01-01", "2025-12-31", 200),  # без фильтров
    (1, {"title": "Имба_2"}, "2025-01-01", "2025-12-31", 200),
    (142, {"title": "Имба_2"}, "2025-01-01", "2025-12-31", 404),
])
async def test_get_rooms_by_filter(hotel_id: int, filters: RoomsFilterDep, date_from, date_to, status_code, ac):
    params = {
        "date_from": date_from,
        "date_to": date_to,
        **filters,
    }

    response = await ac.get(
        f"/hotels/{hotel_id}/rooms",
        params=params
    )

    assert response.status_code == status_code


@pytest.mark.parametrize('hotel_id, room_id, f_ids_to_add, f_ids_to_dlt, data, status_code', [
    # Успешное обновление
    (
            1, 1,
            [2,3,4],  # добавить facilities
            [],  # удалить facilities
            {
                "title": "Обновленное название",
                "description": "Новое описание",
                "price": 2500,
                "quantity": 5
            },
            200
    ),
    (
            1, 1,
            [], [],
            {
                "title": "Только название обновил",
                "price": 3000
            },
            200
    ),
    (
            1, 1,
            [], [1,2],
            {
                "title": "Удаление удобств",
                "price": 1245
            },
            200
    ),
    (
            1, 1,
            [], [],
            {},
            400
    ),
    (
            124, 1,
            [2,3,4],  # добавить facilities
            [],  # удалить facilities
            {
                "title": "Обновленное название",
                "description": "Новое описание",
                "price": 2500,
                "quantity": 5
            },
            404
    ),
    (
            1, 4142,
            [2,3,4],  # добавить facilities
            [],  # удалить facilities
            {
                "title": "Обновленное название",
                "description": "Новое описание",
                "price": 2500,
                "quantity": 5
            },
            404
    ),
])
async def test_update_room(
        ac,
        hotel_id,
        room_id,
        f_ids_to_add,
        f_ids_to_dlt,
        data,
        status_code
):
    body = {
        "f_ids_to_add": f_ids_to_add if f_ids_to_add is not None else [],
        "f_ids_to_dlt": f_ids_to_dlt if f_ids_to_dlt is not None else [],
        "data": data
    }

    logging.debug(f"ДЕБАГ ТЕСТА:")
    logging.debug(f"hotel_id: {hotel_id}")
    logging.debug(f"room_id: {room_id}")
    logging.debug(f"f_ids_to_add: {f_ids_to_add}")
    logging.debug(f"f_ids_to_dlt: {f_ids_to_dlt}")
    logging.debug(f"data: {data}")
    logging.debug(f"ИТОГОВЫЙ BODY: {body}")

    response = await ac.put(
        f"/hotels/{hotel_id}/rooms/{room_id}",
        json=body
    )

    logging.debug(f"ОТВЕТ СЕРВЕРА:")
    logging.debug(f"Status: {response.status_code}")
    logging.debug(f"Body: {response.text}")

    assert response.status_code == status_code, f"Ожидался {status_code}, получили {response.status_code}. Ответ: {response.text}"

    if status_code == 200:
        response_data = response.json()
        assert "message" in response_data
        assert "Информация обновлена" in response_data["message"]


@pytest.mark.parametrize('hotel_id, room_id, f_ids_to_add, f_ids_to_dlt, data, status_code', [
    # Успешное частичное обновление с facilities
    (
            1, 1,
            [2, 3, 4],  # добавить facilities
            [1],  # удалить facilities
            {
                "title": "Частично обновленное название",
                "price": 3500
            },
            200
    ),
    # Только обновление данных без facilities
    (
            1, 1,
            [],  # пустые списки facilities
            [],
            {
                "description": "Только описание обновил",
                "quantity": 3
            },
            200
    ),
    # Только добавление facilities
    (
            1, 1,
            [1, 2],
            [],
            {},  # без обновления данных
            200
    ),
    # Только удаление facilities
    (
            1, 1,
            [],
            [2, 3],  # только удалить facilities
            {},  # без обновления данных
            200
    ),
    (
            1, 1,
            [1],
            [4],
            {
                "title": "Полное обновление",
                "description": "Новое описание",
                "price": 5000,
                "quantity": 10
            },
            200
    ),
    # Пустой запрос - ДОЛЖЕН ПАДАТЬ
    (
            1, 1,
            [],  # пустые списки
            [],
            None,  # нет данных
            400
    ),
    # None вместо списков
    (
            1, 1,
            None,
            None,
            None,
            400
    ),
])
async def test_partially_update_room(
        ac,
        hotel_id,
        room_id,
        f_ids_to_add,
        f_ids_to_dlt,
        data,
        status_code
):
    body = {}

    if f_ids_to_add is not None:
        body["f_ids_to_add"] = f_ids_to_add
    if f_ids_to_dlt is not None:
        body["f_ids_to_dlt"] = f_ids_to_dlt

    if data is not None:
        body["data"] = data

    logging.debug(f"PATCH Request body: {body}")

    response = await ac.patch(
        f"/hotels/{hotel_id}/rooms/{room_id}",
        json=body
    )

    logging.debug(f"PATCH Response status: {response.status_code}")
    logging.debug(f"PATCH Response body: {response.json()}")

    assert response.status_code == status_code

    if status_code == 200:
        response_data = response.json()
        assert "message" in response_data
        assert "Информация обновлена" in response_data["message"]


@pytest.mark.parametrize('hotel_id, room_id, status_code', [
    # Успешное удаление
    (1, 1, 200),
    (1, 2, 200),
    (2, 3, 200),
    # Несуществующие ID (должны возвращать 404)
    (999, 1, 404),
    (1, 999, 404),
    (999, 999, 404),
    # Некорректные ID
    (0, 1, 404),
    (1, 0, 404),
    (-1, 1, 404),
    (1, -1, 404),
])
async def test_delete_room(ac, hotel_id, room_id, status_code):
    response = await ac.delete(f"/hotels/{hotel_id}/rooms/{room_id}")

    logging.debug(f"DELETE Request: /hotels/{hotel_id}/rooms/{room_id}")
    logging.debug(f"Response status: {response.status_code}")
    logging.debug(f"Response body: {response.json()}")

    assert response.status_code == status_code

    if status_code == 200:
        response_data = response.json()
        assert "status" in response_data
        assert f"Комната {room_id} успешно удалена" in response_data["status"]

    elif status_code == 404:
        response_data = response.json()
        assert "detail" in response_data