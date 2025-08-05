from flask import Flask, render_template, request, redirect, url_for
from learning_app import LearningApp

app = Flask(__name__)
learning_app = LearningApp()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form.get('text', '')
        lang = request.form.get('lang', '') or 'en'
        tokens = learning_app.add_text(text, lang)
        return render_template('tokens.html', tokens=tokens, app=learning_app)
    vocab = learning_app.get_vocabulary()
    return render_template('index.html', vocab=vocab)

@app.route('/translate', methods=['POST'])
def translate():
    for word, translation in request.form.items():
        learning_app.set_translation(word, translation)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
