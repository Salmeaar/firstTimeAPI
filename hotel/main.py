import os, uvicorn, psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

PORT=8390

# Load enviroment variables
load_dotenv()
DB_URL = os.getenv("DB_URL")

#print(DB_URL)
# Create DB connection
conn = psycopg.connect(DB_URL, autocommit=True, row_factory=dict_row)


app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class Booking(BaseModel):
    guest_id: int
    room_id: int
    


# rooms = [
#     {"nummer":"101","type":"single","status":"available"},
#     {"nummer":"102","type":"single","status":"occupied"},
#     {"nummer":"103","type":"double","status":"available"},
#     {"nummer":"104","type":"double","status":"occupied"},
#     {"nummer":"105","type":"triple","status":"available"},
#     {"nummer":"106","type":"triple","status":"occupied"},
#     {"nummer":"201","type":"suite","status":"available"},
#     {"nummer":"202","type":"suite","status":"occupied"},
# ]

#all rooms
@app.get("/rooms/")
def vacants():
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM hotel_rooms")
            messages = cur.fetchall()
        return messages
    
#one room
@app.get("/rooms/{id}")
def vacant_room(id: int):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM hotel_rooms WHERE id = %s", [id])
        #cur.execute("SELECT * FROM hotel_rooms WHERE id = %s", (id,)
        #cur.execute("SELECT * FROM hotel_rooms WHERE id = %(id)s", {"id":id})
        room = cur.fetchone()
        if not room:
            return{"msg":"Room not found"}
        return room
    

@app.post("/bookings")
def create_booking(booking: Booking):
    with conn.cursor() as cur:
        cur.execute("""INSERT INTO hotel_booking
                    (guest_id,room_id)
                    VALUES(%s,%s) RETURNING id
                    """,[booking.guest_id, booking.room_id])
        new_id = cur.fetchone()['id']
    return {"msg": "booking created!", "id": new_id}



if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        ssl_keyfile="/etc/letsencrypt/privkey.pem",
        ssl_certfile="/etc/letsencrypt/fullchain.pem",
    )