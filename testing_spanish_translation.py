from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "your-secret-key"

# --- Translation dictionaries ---
translations = {
    "en": {
        "title": "Welcome to Our Website",
        "subtitle": "Choose an option below:",
        "button1": "Start",
        "button2": "About",
        "lang_label": "Language",
    },
    "es": {
        "title": "Bienvenido a Nuestro Sitio Web",
        "subtitle": "Elige una opción abajo:",
        "button1": "Comenzar",
        "button2": "Acerca de",
        "lang_label": "Idioma",
    }
}

# --- Helper to get current language ---
def get_lang():
    return session.get("lang", "en")

# --- Route to change language ---
@app.route("/set_language", methods=["POST"])
def set_language():
    lang = request.form.get("language")
    if lang in translations:
        session["lang"] = lang
    return redirect(request.referrer or url_for("home"))

# --- Main page ---
@app.route("/")
def home():
    lang = get_lang()
    text = translations[lang]
    return render_template("index.html", text=text, lang=lang)

if __name__ == "__main__":
    app.run(debug=True)
