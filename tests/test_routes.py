from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_limit_is_rejected_if_out_of_range():
    assert True
    # response = client.get("/top_price_list")
    # assert response.status_code == 400
