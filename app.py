import os
import random
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session
from flask_dance.contrib.google import make_google_blueprint, google
from learning_app import LearningApp

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev")

learning_app = LearningApp()

SAMPLE_TEXTS = [
    ("Hola mundo otra vez", "es"),
    ("Buenos dias amigo", "es"),
    ("Bonjour mon ami", "fr"),
    ("Salut tout le monde", "fr"),
]

# Google OAuth blueprint
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_OAUTH_CLIENT_ID", ""),
    client_secret=os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", ""),
    redirect_to="google_authorized",
    scope=["profile", "email"],
)
app.register_blueprint(google_bp, url_prefix="/login")


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["user"] = request.form.get("username")
        return redirect(url_for("landing"))
    return render_template("login.html")


@app.route("/google_authorized")
def google_authorized():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    if resp.ok:
        session["user"] = resp.json().get("email")
    return redirect(url_for("landing"))


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("landing"))


@app.route("/texts", methods=["GET", "POST"])
@login_required
def texts():
    if request.method == "POST":
        text = request.form.get("text", "")
        lang = request.form.get("lang", "") or "en"
        text_id = learning_app.add_text(text, lang)
        return redirect(url_for("edit_text", text_id=text_id))
    all_texts = learning_app.list_texts()
    progress = {t["id"]: learning_app.text_progress(t["id"]) for t in all_texts}
    return render_template("texts.html", texts=all_texts, progress=progress)


@app.route("/texts/<int:text_id>")
@login_required
def edit_text(text_id: int):
    entry = learning_app.get_text(text_id)
    user_lang = session.get("settings", {}).get("language", "en")
    statuses = {
        word: learning_app.translation_status(
            word, learning_app.vocab.get(word), entry["lang"], user_lang
        )
        for line in entry["tokens"]
        for word in line
    }
    done, total = learning_app.text_progress(text_id)
    pct = int((done / total * 100) if total else 0)
    return render_template(
        "tokens.html",
        tokens=entry["tokens"],
        app=learning_app,
        text_id=text_id,
        statuses=statuses,
        progress=(done, total, pct),
    )


@app.route("/translate/<int:text_id>", methods=["POST"])
@login_required
def translate(text_id: int):
    for word, translation in request.form.items():
        learning_app.set_translation(word, translation)
    return redirect(url_for("edit_text", text_id=text_id))


@app.route("/hint/<int:text_id>/<word>")
@login_required
def hint(text_id: int, word: str):
    entry = learning_app.get_text(text_id)
    user_lang = session.get("settings", {}).get("language", "en")
    translation = learning_app.get_reference(word, entry["lang"], user_lang)
    learning_app.set_translation(word, translation)
    return redirect(url_for("edit_text", text_id=text_id))


@app.route("/vocab")
@login_required
def vocab():
    vocab = learning_app.get_vocabulary()
    return render_template("vocab.html", vocab=vocab)


@app.route("/trainer")
@login_required
def trainer():
    vocab = learning_app.get_vocabulary()
    if not vocab:
        return render_template("trainer.html", word=None)
    word, data = random.choice(list(vocab.items()))
    return render_template("trainer.html", word=word, data=data)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    settings = session.get("settings", {})
    if request.method == "POST":
        settings["language"] = request.form.get("language")
        session["settings"] = settings
    return render_template("profile.html", settings=settings)


@app.route("/suggest")
@login_required
def suggest():
    user_lang = session.get("settings", {}).get("language", "en")
    candidates = [t for t in SAMPLE_TEXTS if t[1] == user_lang]
    suggestions = learning_app.suggest_text(candidates)
    return render_template("suggest.html", suggestions=suggestions, lang=user_lang)


@app.route("/suggest/add", methods=["POST"])
@login_required
def add_suggested():
    text = request.form["text"]
    lang = request.form["lang"]
    text_id = learning_app.add_text(text, lang)
    return redirect(url_for("edit_text", text_id=text_id))


if __name__ == "__main__":
    app.run(debug=True)
