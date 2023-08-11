from fastapi import FastAPI
from app.api.routes import router
from app.db.database import Database
from app.logic.coin_resolver import CoinResolver
import uvicorn

app = FastAPI()
app.include_router(router)


@app.on_event("startup")
def startup_db_client():
    app.coin_resolver = CoinResolver()


@app.on_event("shutdown")
def shutdown_db_client():
    app.coin_resolver.close()


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)
