import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .constants import ENV

app = FastAPI()
public_app = FastAPI()
private_app = FastAPI()

app.mount("/api", public_app)
app.mount("/api", private_app)

origins = ["*"]

public_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

private_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    if ENV == "prod":
        uvicorn.run("dagger.main:app", host="0.0.0.0", port=80, reload=True)
    else:
        uvicorn.run("dagger.main:app", host="0.0.0.0", port=8000, reload=True)
