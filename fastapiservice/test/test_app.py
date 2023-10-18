from fastapi.testclient import TestClient
from fastapiservice.src.app import app

client = TestClient(app)

def test_healhcheck():
    response = client.get(
        url='/'
    )

    assert response.status_code == 200
    message = response.json()["message"]
    assert message == "ChatBot API is working"

