import pytest

from learning_app import LearningApp


def test_add_text_and_transliteration():
    app = LearningApp()
    tokens = app.add_text("Hallo Welt", "de")
    assert tokens == [["Hallo", "Welt"]]
    vocab = app.get_vocabulary()
    assert "Hallo" in vocab
    assert vocab["Hallo"]["transliteration"]


def test_set_translation_and_suggest_text():
    app = LearningApp()
    app.add_text("Bonjour monde", "fr")
    app.set_translation("Bonjour", "Hallo")
    suggestions = app.suggest_text([
        ("Bonjour tout le monde", "fr"),
        ("Au revoir", "fr"),
    ])
    # first text contains known word 'Bonjour'
    assert suggestions[0][0] == "Bonjour tout le monde"
    assert suggestions[0][1] > suggestions[1][1]
