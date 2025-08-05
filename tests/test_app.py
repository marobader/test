from app import app, learning_app

def test_landing_get():
    client = app.test_client()
    resp = client.get('/')
    assert resp.status_code == 200


def test_add_text_and_translate():
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['user'] = 'tester'
    resp = client.post('/texts', data={'text': 'Hola mundo', 'lang': 'es'})
    assert resp.status_code == 302
    resp = client.get('/texts/1')
    assert b'Hola' in resp.data
    resp = client.post('/translate/1', data={'Hola': 'Hello', 'mundo': 'world'})
    assert resp.status_code == 302
    resp = client.get('/texts/1')
    assert b'value="Hello"' in resp.data


def test_profile_requires_login():
    client = app.test_client()
    resp = client.get('/profile')
    assert resp.status_code == 302


def test_suggest_route():
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['user'] = 'tester'
        sess['settings'] = {'language': 'es'}
    resp = client.get('/suggest')
    assert resp.status_code == 200
