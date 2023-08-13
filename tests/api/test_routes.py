from fastapi.testclient import TestClient

from app.main import app
from app.services.time_service import time_format
from tests.services.time_service_mock import TimeServiceMock, SAMPLE_TIME, SAMPLE_TIME_SHORTLY_AFTER


time_service_mock = TimeServiceMock(SAMPLE_TIME)
app.time_service = time_service_mock
client = TestClient(app)


def test_top_price_request_fails_if_limit_is_out_of_range():
    response = client.get("/top_price_list?limit=9")
    assert response.status_code == 400
    assert "limit" in response.json()["detail"].lower()
    response = client.get("/top_price_list?limit=101")
    assert response.status_code == 400
    assert "limit" in response.json()["detail"].lower()


def test_top_price_request_fails_if_timestamp_has_wrong_format():
    response = client.get("/top_price_list?limit=10&datetime=2020-01-01")
    assert response.status_code == 400
    assert "format" in response.json()["detail"].lower()


def test_top_price_request_fails_if_timestamp_is_in_the_future():
    future_timestamp = SAMPLE_TIME_SHORTLY_AFTER.strftime(time_format)
    response = client.get(
        f"/top_price_list?limit=10&datetime={future_timestamp}")
    assert response.status_code == 400
    assert "past" in response.json()["detail"].lower()


def test_top_price_request_succeeds_for_current_request():
    pass


def test_top_price_request_succeeds_for_historical_request_if_data_is_found():
    pass
