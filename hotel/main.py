import os, uvicorn, psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

PORT=8390

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Load enviroment variables
load_dotenv()
DB_URL = os.getenv("DB_URL")

print(DB_URL)
# Create DB connection
conn = psycopg.connect(DB_URL, autocommit=True, row_factory=dict_row)



@app.get("/temp")
def temp():
    return {"msg ":"Hello" }


rooms = [
    {"nummer":"101","type":"single","status":"available"},
    {"nummer":"102","type":"single","status":"occupied"},
    {"nummer":"103","type":"double","status":"available"},
    {"nummer":"104","type":"double","status":"occupied"},
    {"nummer":"105","type":"triple","status":"available"},
    {"nummer":"106","type":"triple","status":"occupied"},
    {"nummer":"201","type":"suite","status":"available"},
    {"nummer":"202","type":"suite","status":"occupied"},
]

#all rooms
@app.get("/rooms/")
def vacants():
    return rooms
    
#one room
@app.get("/rooms/{id}")
def vacant_room(id: int):
    try:
        return rooms[id]
    except:
        return{"error": "Room not found"}

@app.post("/bookings")
def create_booking(request: Request):
    return {"msg": "booking created!"}



if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        ssl_keyfile="/etc/letsencrypt/privkey.pem",
        ssl_certfile="/etc/letsencrypt/fullchain.pem",
    )