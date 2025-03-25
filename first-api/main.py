import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

PORT=8390

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def hello():
    msg ="Några populära SOA-implementationer" #string variabel
    soa_protocols = ["SOAP", "REST", "GraphQL", "gRPC"] #list
    my_dict = {
        'message' : msg,
        'myList' : soa_protocols
    }#dictionary
    return my_dict

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        ssl_keyfile="/etc/letsencrypt/privkey.pem",
        ssl_certfile="/etc/letsencrypt/fullchain.pem",
    )
