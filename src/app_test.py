import pytest
import time
from app import app
from flask import jsonify

# 雑テストしかない
# コンテナの依存関係があるので、docker composeを起動したうえでテスト実行すること

app.config['TESTING'] = True

# /
def test_flask_root():
    client = app.test_client()
    resp = client.get('/')
    body = resp.get_json()
    assert body == {"status": "OK"}
    assert resp.status_code == 200

# /tasks
def test_flask_tasks():
    client = app.test_client()
    resp = client.get('/tasks')
    assert resp.status_code == 200

# /enqueue
def test_flask_enqueue():
    client = app.test_client()

    resp = client.post('/enqueue', json={"cmd": "ls"})
    assert resp.status_code == 200

    resp = client.post('/enqueue', json={"cmd": "NOT_FOUND"})
    assert resp.status_code == 200

    body = resp.get_json()
    assert len(body['task_id']) == 36 # task_idの長さ

def test_flask_enqueue_fail():
    client = app.test_client()

    resp = client.post('/enqueue', json={})
    assert resp.status_code == 400

    body = resp.get_json()
    assert len(body['message']) > 0

    resp = client.post('/enqueue')
    assert resp.status_code == 400

    body = resp.get_json()
    assert len(body['message']) > 0
