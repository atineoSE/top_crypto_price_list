from fastapi import FastAPI
from app.api.routes import router
from app.db.database import Database
from app.services.coin_market_cap import CoinMarketCap
from app.services.crypto_compare import CryptoCompare
from app.services.time_service import TimeService
from app.logic.coin_resolver import CoinResolver
import uvicorn

app = FastAPI()
app.include_router(router)


@app.on_event("startup")
def startup_db_client():
    """Startup of app resources"""
    db = Database()
    coin_market_cap = CoinMarketCap()
    crypto_compare = CryptoCompare()
    time_service = TimeService()
    app.coin_resolver = CoinResolver(
        db, coin_market_cap, crypto_compare, time_service)
    app.time_service = time_service


@app.on_event("shutdown")
def shutdown_db_client():
    """Tear down of app resources"""
    app.coin_resolver.close()


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)
