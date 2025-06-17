from flask import Flask, request, render_template, redirect, url_for, Response
from twilio.twiml.messaging_response import MessagingResponse
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import datetime

app = Flask(__name__)
auth = HTTPBasicAuth()

# Utilisateur admin
users = {
    "admin": generate_password_hash("askely2025")
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

# Page d'accueil
@app.route('/')
def index():
    return "🚀 Askely Express est en ligne."

# Webhook WhatsApp
@app.route("/webhook/whatsapp", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.form.get('Body', '').lower()
    from_number = request.form.get('From')

    print(f"📩 Message WhatsApp reçu de {from_number}: {incoming_msg}")

    resp = MessagingResponse()
    msg = resp.message()

    if "bonjour" in incoming_msg:
        msg.body("👋 Bonjour ! Bienvenue chez Askely Express. Répondez par :
1️⃣ Envoyer un colis
2️⃣ Devenir transporteur
3️⃣ Suivre un colis")
    elif "1" in incoming_msg or "envoyer" in incoming_msg:
        msg.body("✈️ Très bien ! Veuillez nous envoyer les détails du colis :
- Ville de départ
- Ville d'arrivée
- Poids estimé
- Numéro de téléphone")
    elif "2" in incoming_msg or "transporteur" in incoming_msg:
        msg.body("🚚 Super ! Pour devenir transporteur, veuillez envoyer :
- Vos destinations régulières
- Votre numéro WhatsApp
- Une pièce d'identité en photo")
    elif "3" in incoming_msg or "suivre" in incoming_msg:
        msg.body("🔍 Entrez le numéro de suivi du colis (si vous en avez un).")
    else:
        msg.body("🤖 Je n'ai pas compris. Répondez par 'Bonjour' pour afficher le menu.")

    return str(resp)

# Poster un colis
@app.route('/poster_colis', methods=['POST'])
def poster_colis():
    data = request.get_json()
    nom = data.get('nom_client')
    tel = data.get('tel_client')
    depart = data.get('ville_depart')
    arrivee = data.get('ville_arrivee')
    poids = data.get('poids_kg')
    montant = data.get('prix_total')

    conn = sqlite3.connect('paiements.db')
    c = conn.cursor()
    c.execute("INSERT INTO paiements (nom_client, tel_client, ville_depart, ville_arrivee, poids_kg, prix_total, date) VALUES (?, ?, ?, ?, ?, ?, ?)", 
              (nom, tel, depart, arrivee, poids, montant, datetime.datetime.now()))
    conn.commit()
    conn.close()

    return {"status": "success", "message": "Colis enregistré"}

# Dashboard admin
@app.route('/admin/paiements')
@auth.login_required
def voir_paiements():
    conn = sqlite3.connect('paiements.db')
    c = conn.cursor()
    c.execute("SELECT * FROM paiements ORDER BY date DESC")
    paiements = c.fetchall()
    conn.close()
    return render_template('paiements.html', paiements=paiements)

# Création automatique de la base de données
def init_db():
    conn = sqlite3.connect('paiements.db')
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS paiements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_client TEXT,
            tel_client TEXT,
            ville_depart TEXT,
            ville_arrivee TEXT,
            poids_kg REAL,
            prix_total REAL,
            date TEXT
        )
    """)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=10000, debug=True)
