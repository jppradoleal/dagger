import debugpy
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dagger.api import login, partner, users
from dagger.constants import ENV

app = FastAPI()
public_app = FastAPI()
private_app = FastAPI()

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

private_app.include_router(login.router, tags=["login"])
private_app.include_router(users.router, prefix="/users", tags=["users"])
private_app.include_router(partner.router, prefix="/partners", tags=["partners"])

app.mount("/api", private_app)
app.mount("/public", public_app)

if __name__ == "__main__":
    if ENV == "prod":
        uvicorn.run("dagger.main:app", host="0.0.0.0", port=80, reload=True)
    else:
        debugpy.listen(("0.0.0.0", 5678))
        uvicorn.run("dagger.main:app", host="0.0.0.0", port=8000, reload=True)
