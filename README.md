# Learning App Prototype

This repository contains a minimal prototype of a Birkenbihl-inspired learning app.

## Setup

```bash
pip install -r requirements.txt
```

## Running tests

```bash
PYTHONPATH=. pytest
```

## Web interface

```bash
FLASK_APP=app.py flask run
```

Open <http://localhost:5000> to paste text, enter translations, and view stored vocabulary.

## Usage

```python
from learning_app import LearningApp

app = LearningApp()
app.add_text("Bonjour monde", "fr")
app.set_translation("Bonjour", "Hallo")
print(app.get_vocabulary())
```

This demonstrates basic text tokenization, per-word translation,
transliteration, and simple text suggestions based on known vocabulary.
