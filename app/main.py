from fastapi import FastAPI
from api.routes.routes import router
from db.database import Database
from services.coin_resolver import CoinResolver
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
