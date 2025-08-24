from fastapi import FastAPI, Query
from models import Hotel, Update_Hotel
import uvicorn

app = FastAPI()

hotels = [
    {"id": 1, "city": "Sochi", "name": "Star"},
    {"id": 2, "city": "Dubai", "name": "Arab"}
]

@app.get("/hotels")
async def get_hotels(
        id: int | None = Query(None, description="Айдишник"),
        title: str | None = Query(None, description="Название отеля"),
):
    
    hotels_ = []

    for hotel in hotels:
        if id and hotel["id"] != id:
            continue
        if title and hotel["title"] != title:
            continue
        hotels_.append(hotel)
    return hotels_

@app.delete("/hotels/{hotel_id}")
async def delete_hotel(hotel_id: int):
    global hotels
    hotels = [hotel for hotel in hotels if hotel["id"] != hotel_id]
    return hotels

@app.post("/hotels")
async def create_hotel(hotel: Hotel):
    global hotels
    hotels.append({
        "id": hotels[-1]["id"] + 1,
        "city": hotel.city,
        "name": hotel.name
    })
    return {"status": "Ok"}

def find_hotel(hotel_id: int):
    for hotel in hotels:
        if hotel["id"] == hotel_id:
            return hotel
    
    return None

@app.put("/hotels")
async def update_hotel(hotel: Update_Hotel):
    hotel_ = find_hotel(hotel.id)

    if hotel_ == None:
        return {"message": "Hotel with that ID is not found"}
    
    if not hotel.city and hotel.name:
        return {"message": "Заполнены не все поля"}
    else:
        hotel_["city"] = hotel.city
        hotel_["name"] = hotel.name

    return {"message": "Информация обновлена"}

@app.patch("/hotels")
async def patch_hotel(hotel: Update_Hotel):
    hotel_ = find_hotel(hotel.id)

    if hotel_ == None:
        return {"message": "Hotel with that ID is not found"}
    
    if not hotel.city and hotel.name:
        return {"message": "Нечего менять"}
    
    if hotel.city:
        hotel_["city"] = hotel.city
    if hotel.name:
        hotel_["name"] = hotel.name

    return {"message": "Информация обновлена"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)