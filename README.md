# Learning App Prototype

This repository contains a minimal prototype of a Birkenbihl-inspired learning app.
Users can save texts, resume them later with visible progress, get color-coded feedback on translations, request hints, and receive text suggestions matching known vocabulary.

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

Open <http://localhost:5000> for the landing page. After logging in you can store texts, revisit them later, review vocabulary or try the simple trainer.

To enable Google login set the OAuth credentials:

```bash
export GOOGLE_OAUTH_CLIENT_ID=your_id
export GOOGLE_OAUTH_CLIENT_SECRET=your_secret
```

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
