import os, uvicorn, psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import date, timedelta
from markupsafe import escape

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
    room_id: int
    datefrom: date
    dateto: date
    addinfo: Optional[str] = ""

#validera API key   
def validate_key(api_key: str = ""):
    if not api_key:
        raise HTTPException(status_code=401, detail={"error":"API-KEY missing"})

    with conn.cursor() as cur:
            cur.execute("""SELECT * FROM hotel_guests WHERE api_key = %s""", [api_key,])
            guest = cur.fetchone()
            if not guest:
                 raise HTTPException(status_code=401, detail={"error":"Bad API key!"})
            print(f"Valid key, guest {guest['id']},{guest['firstname']}")
            return guest


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
@app.get("/rooms")
def vacants():
        with conn.cursor() as cur:
            cur.execute("""
            SELECT * 
            FROM hotel_rooms 
            ORDER BY room_number""")
            messages = cur.fetchall()
        return messages

@app.get("/guests")
def vacants():
        with conn.cursor() as cur:
            cur.execute("""SELECT 
                *,
                (SELECT count(*) 
                    FROM hotel_bookings 
                    WHERE guest_id = hotel_guests.id) AS visits
            FROM hotel_guests 
            ORDER BY name""")
            guests = cur.fetchall()
        return guests
    
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
    
@app.get("/bookings")
def get_bookings(guest: dict=Depends(validate_key)):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                hb.*,
                (hb.dateto - hb.datefrom + 1) AS nights,
                hr.room_number,
                hr.price as price_per_night,
                (hb.dateto - hb.datefrom + 1) * hr.price AS total_price,
                hg.name AS guest_name
            FROM hotel_bookings hb
            INNER JOIN hotel_rooms hr 
                ON hr.id = hb.room_id
            INNER JOIN hotel_guests hg
                ON hg.id = hb.guest_id
            WHERE hb.guest_id = %s
            ORDER BY hb.id DESC""",[guest['id']])
        bookings = cur.fetchall()
        return bookings
        

     


@app.post("/bookings")
def create_booking(booking: Booking, guest: dict = Depends(validate_key)):
    with conn.cursor() as cur:
        cur.execute("""INSERT INTO hotel_booking
                    (guest_id,
                    room_id,
                    datefrom,
                    dateto,
                    addinfo)
                    VALUES(%s,%s,%s,%s,%s) RETURNING id
                    """,[guest['id'], booking.room_id,
                        booking.dateto or booking.datefrom + timedelta(days=1),booking.datefrom,escape(booking.addinfo)])
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