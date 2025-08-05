from app import app, learning_app

def test_index_get():
    client = app.test_client()
    resp = client.get('/')
    assert resp.status_code == 200

def test_add_text_and_translate():
    client = app.test_client()
    resp = client.post('/', data={'text': 'Hola mundo', 'lang': 'es'})
    assert resp.status_code == 200
    assert b'Hola' in resp.data
    resp = client.post('/translate', data={'Hola': 'Hello', 'mundo': 'world'})
    assert resp.status_code == 302
    resp = client.get('/')
    assert b'Hello' in resp.data
