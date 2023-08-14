from fastapi.testclient import TestClient
import json
from urllib import parse

from app.main import app

from tests.services.time_service_mock import TimeServiceMock, SAMPLE_TIME, SAMPLE_TIME_SHORTLY_AFTER
from tests.logic.coin_resolver_mock import CoinResolverMock, SAMPLE_RESULTS, SAMPLE_RESULTS_JSON, SAMPLE_RESULTS_CSV


def test_top_price_request_fails_if_limit_is_out_of_range():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/top_price_list?limit=9")

    # Assert
    assert response.status_code == 400
    assert "limit" in response.json()["detail"].lower()

    # Act
    response = client.get("/top_price_list?limit=101")

    # Assert
    assert response.status_code == 400
    assert "limit" in response.json()["detail"].lower()


def test_top_price_request_fails_if_timestamp_has_wrong_format():
    # Arrange
    time_service_mock = TimeServiceMock(SAMPLE_TIME)
    app.time_service = time_service_mock
    client = TestClient(app)
    non_iso_timestamp = "2023 08 12"

    # Act
    response = client.get(
        f"/top_price_list?limit=10&datetime={parse.quote(non_iso_timestamp)}")

    # Assert
    assert response.status_code == 400
    assert "format" in response.json()["detail"].lower()


def test_top_price_request_fails_if_timestamp_is_in_the_future():
    # Arrange
    time_service_mock = TimeServiceMock(SAMPLE_TIME)
    app.time_service = time_service_mock
    client = TestClient(app)
    future_timestamp = SAMPLE_TIME_SHORTLY_AFTER.isoformat()

    # Act
    response = client.get(
        f"/top_price_list?limit=10&datetime={parse.quote(future_timestamp)}")

    # Assert
    assert response.status_code == 400
    assert "past" in response.json()["detail"].lower()


def test_top_price_request_fails_if_output_format_is_not_supported():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/top_price_list?limit=10&format=xml")

    # Assert
    assert response.status_code == 400
    assert "format" in response.json()["detail"].lower()


def test_top_price_request_for_current_data_succeeds():
    # Arrange
    time_service_mock = TimeServiceMock(SAMPLE_TIME)
    coin_resolver_mock = CoinResolverMock(SAMPLE_RESULTS)
    app.time_service = time_service_mock
    app.coin_resolver = coin_resolver_mock
    client = TestClient(app)

    # Act
    response = client.get("/top_price_list?limit=10")

    # Assert
    assert response.status_code == 200
    assert response.json() == json.loads(SAMPLE_RESULTS_JSON)


def test_top_price_request_for_historical_data_succeeds():
    # Arrange
    time_service_mock = TimeServiceMock(SAMPLE_TIME)
    coin_resolver_mock = CoinResolverMock(SAMPLE_RESULTS)
    app.time_service = time_service_mock
    app.coin_resolver = coin_resolver_mock
    client = TestClient(app)
    timestamp = SAMPLE_TIME.isoformat()

    # Act
    response = client.get(
        f"/top_price_list?limit=10&datetime={parse.quote(timestamp)}")

    # Assert
    assert response.status_code == 200
    assert response.json() == json.loads(SAMPLE_RESULTS_JSON)


def test_top_price_request_for_historical_data_fails_if_data_is_not_found():
    # Arrange
    time_service_mock = TimeServiceMock(SAMPLE_TIME)
    coin_resolver_mock = CoinResolverMock()
    app.time_service = time_service_mock
    app.coin_resolver = coin_resolver_mock
    client = TestClient(app)
    timestamp = SAMPLE_TIME.isoformat()

    # Act
    response = client.get(
        f"/top_price_list?limit=10&datetime={parse.quote(timestamp)}")

    # Assert
    assert response.status_code == 404
    assert "no data" in response.json()["detail"].lower()


def test_top_price_request_can_be_formatted_as_csv():
    # Arrange
    time_service_mock = TimeServiceMock(SAMPLE_TIME)
    coin_resolver_mock = CoinResolverMock(SAMPLE_RESULTS)
    app.time_service = time_service_mock
    app.coin_resolver = coin_resolver_mock
    client = TestClient(app)

    # Act
    response = client.get(f"/top_price_list?limit=10&format=csv")

    # Assert
    assert response.status_code == 200
    assert response.text == SAMPLE_RESULTS_CSV
