from fastapi import APIRouter, Request, HTTPException, status
from models.models import CryptoEntry, OutputFormat
from datetime import datetime as dt

router = APIRouter()

time_format = '%Y-%m-%d %H:%M:%S'


@router.get("/top_price_list", response_model=str | list[CryptoEntry])
def get_user(request: Request, limit: int, datetime: str | None = None, format: str | None = None) -> str | list[CryptoEntry]:
    # Validate limit
    if limit < 10 or limit > 100:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Limit must be between 10 and 100")

    # Validate timestamp
    timestamp = dt.now()
    if datetime is not None:
        try:
            timestamp = dt.strptime(datetime, time_format)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Datetime must be expressed in the format {}".format(time_format))

    # Validate format
    output_format = OutputFormat.JSON
    if format is not None:
        if format.lower() == "csv":
            output_format = OutputFormat.CSV
        elif format.lower() != "json":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Format must be either CSV or JSON")

    # Fetch results
    coin_resolver = request.app.coin_resolver
    results = coin_resolver.fetch_top_coins(limit, timestamp)

    return output_format.output(results)
