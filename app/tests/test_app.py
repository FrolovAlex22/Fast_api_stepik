from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_user():
    testing_user = {
        'username': 'testusername',
        'email': 'testemail.com'
    }
    response = client.post('/user/', json=testing_user)
    assert response.status_code == 201
    response_json = response.json()
    assert response_json is not None
    del response_json['id']
    assert response_json == testing_user
