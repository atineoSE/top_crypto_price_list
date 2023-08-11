from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import PlainTextResponse, JSONResponse
from models.models import CryptoEntry, OutputFormat, time_format
from datetime import datetime as dt
from models.errors import InvalidTime, UnavailableTime
import sys
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)

router = APIRouter()


@router.get("/top_price_list", response_model=None)
def get_user(request: Request, limit: int, datetime: str | None = None, format: str | None = None) -> JSONResponse | PlainTextResponse:
    # Validate limit
    if limit < 10 or limit > 100:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Limit must be between 10 and 100")

    # Validate timestamp
    timestamp = None
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
    results: list[CryptoEntry] = []
    try:
        results = coin_resolver.fetch_top_coins(limit, timestamp)
    except InvalidTime as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Input time was invalid.")
    except UnavailableTime as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No data available for the specified time.")

    # Format output and return
    formatted_output = output_format.output(results)
    if output_format == OutputFormat.JSON:
        return JSONResponse(content=formatted_output)
    else:
        return PlainTextResponse(content=formatted_output)
