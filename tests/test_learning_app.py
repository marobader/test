import pytest

from learning_app import LearningApp
from unittest.mock import patch


def test_add_text_and_progress():
    app = LearningApp()
    text_id = app.add_text("Hallo Welt", "de")
    tokens = app.get_text(text_id)["tokens"]
    assert tokens == [["Hallo", "Welt"]]
    done, total = app.text_progress(text_id)
    assert (done, total) == (0, 2)
    vocab = app.get_vocabulary()
    assert vocab["Hallo"]["transliteration"]


def test_set_translation_and_suggest_text():
    app = LearningApp()
    app.add_text("Bonjour monde", "fr")
    app.set_translation("Bonjour", "Hallo")
    suggestions = app.suggest_text([
        ("Bonjour tout le monde", "fr"),
        ("Au revoir", "fr"),
    ])
    assert suggestions[0][0] == "Bonjour tout le monde"
    assert suggestions[0][1] > suggestions[1][1]


def test_translation_status_mock():
    app = LearningApp()
    app.add_text("mundo", "es")
    with patch.object(app, 'get_reference', return_value='world'):
        status = app.translation_status('mundo', 'world', 'es', 'en')
    assert status == 'correct'
