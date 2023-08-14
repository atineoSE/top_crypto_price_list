from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import PlainTextResponse, JSONResponse
from app.models.models import CryptoEntry, OutputFormat
from datetime import datetime as dt
from app.services.time_service import TimeService
from app.models.errors import UnavailableTime
from app.logic.coin_resolver import CoinResolver
import sys
import logging
import time

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)

router = APIRouter()


@router.get("/top_price_list", response_model=None)
async def get_user(request: Request, limit: int, datetime: str | None = None, format: str | None = None) -> JSONResponse | PlainTextResponse:
    # Validate limit
    _validate_limit(limit)

    # Validate timestamp
    timestamp = _validate_timestamp(request.app.time_service, datetime)

    # Validate output
    output_format = _validate_output_format(format)

    # Fetch results
    results = await _fetch_results(request.app.coin_resolver, limit, timestamp)

    # Return results in output format
    return _format_output(output_format, results)


def _validate_limit(limit: int) -> None:
    if limit < 10 or limit > 100:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Limit must be between 10 and 100")


def _validate_timestamp(time_service: TimeService, datetime: str | None) -> dt | None:
    timestamp = None
    if datetime is not None:
        # If time format is not recognized, raise error
        try:
            timestamp = dt.fromisoformat(datetime)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Datetime must be expressed in ISO format")

        # If querying about the future, raise error
        time_difference = time_service.now() - timestamp
        if time_difference.total_seconds() < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Datetime must be in the past")
    return timestamp


def _validate_output_format(format: str | None) -> OutputFormat:
    output_format = OutputFormat.JSON
    if format is not None:
        if format.lower() == "csv":
            output_format = OutputFormat.CSV
        elif format.lower() != "json":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Format must be either CSV or JSON")
    return output_format


async def _fetch_results(coin_resolver: CoinResolver, limit: int, timestamp: dt | None) -> list[CryptoEntry]:
    results: list[CryptoEntry] = []
    start_time = time.time()
    try:
        results = await coin_resolver.fetch_top_coins(limit, timestamp)
    except UnavailableTime as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No data available for the specified time.")
    end_time = time.time()
    logging.debug("Router: Time to fetch top coins: {} seconds".format(
        end_time - start_time))
    return results


def _format_output(output_format: OutputFormat, results: list[CryptoEntry]) -> JSONResponse | PlainTextResponse:
    formatted_output = output_format.output(results)
    if output_format == OutputFormat.JSON:
        return JSONResponse(content=formatted_output)
    else:
        return PlainTextResponse(content=formatted_output)
