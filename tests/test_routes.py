from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_limit_is_rejected_if_out_of_range():
    response = client.get("/top_price_list?limit=9")
    assert response.status_code == 400
    response = client.get("/top_price_list?limit=101")
    assert response.status_code == 400
