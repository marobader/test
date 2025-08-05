import os
import random
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session
from flask_dance.contrib.google import make_google_blueprint, google
from learning_app import LearningApp

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev")

learning_app = LearningApp()

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


@app.route("/text", methods=["GET", "POST"])
@login_required
def text():
    if request.method == "POST":
        text = request.form.get("text", "")
        lang = request.form.get("lang", "") or "en"
        tokens = learning_app.add_text(text, lang)
        return render_template("tokens.html", tokens=tokens, app=learning_app)
    return render_template("text.html")


@app.route("/translate", methods=["POST"])
@login_required
def translate():
    for word, translation in request.form.items():
        learning_app.set_translation(word, translation)
    return redirect(url_for("vocab"))


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


if __name__ == "__main__":
    app.run(debug=True)
