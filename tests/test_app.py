from app import app, learning_app

def test_landing_get():
    client = app.test_client()
    resp = client.get('/')
    assert resp.status_code == 200


def test_add_text_and_translate():
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['user'] = 'tester'
    resp = client.post('/text', data={'text': 'Hola mundo', 'lang': 'es'})
    assert resp.status_code == 200
    assert b'Hola' in resp.data
    resp = client.post('/translate', data={'Hola': 'Hello', 'mundo': 'world'})
    assert resp.status_code == 302
    resp = client.get('/vocab')
    assert b'Hello' in resp.data


def test_profile_requires_login():
    client = app.test_client()
    resp = client.get('/profile')
    assert resp.status_code == 302
