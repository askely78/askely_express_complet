from flask import Flask, request, render_template, redirect, url_for, Response
from twilio.twiml.messaging_response import MessagingResponse
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import datetime
import re

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
1. Envoyer un colis
2. Devenir transporteur
3. Suivre un colis")
1. Envoyer un colis
2. Devenir transporteur
3. Suivre un colis")
    elif "1" in incoming_msg or "envoyer" in incoming_msg:
        msg.body("👋 Bonjour ! Bienvenue chez Askely Express. Répondez par :
1. Envoyer un colis
2. Devenir transporteur
3. Suivre un colis") - Téléphone

Exemple : Casa - Dakar - 5 - +212600000000")
    elif re.match(r"^[a-zA-Zéèàçù\s]+ - [a-zA-Zéèàçù\s]+ - \d+ - \+?\d+$", incoming_msg.strip()):
        try:
            parts = incoming_msg.strip().split(" - ")
            depart = parts[0].strip().capitalize()
            arrivee = parts[1].strip().capitalize()
            poids = float(parts[2].strip())
            tel = parts[3].strip()
            montant = round(poids * 10, 2)  # ex: 10 MAD/kg

            conn = sqlite3.connect('paiements.db')
            c = conn.cursor()
            c.execute("INSERT INTO paiements (nom_client, tel_client, ville_depart, ville_arrivee, poids_kg, prix_total, date) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                      ("Client WhatsApp", tel, depart, arrivee, poids, montant, datetime.datetime.now()))
            conn.commit()
            conn.close()

            msg.body("👋 Bonjour ! Bienvenue chez Askely Express. Répondez par :
1. Envoyer un colis
2. Devenir transporteur
3. Suivre un colis")
        except:
            msg.body("👋 Bonjour ! Bienvenue chez Askely Express. Répondez par :
1. Envoyer un colis
2. Devenir transporteur
3. Suivre un colis")
    elif "2" in incoming_msg or "transporteur" in incoming_msg:
        msg.body("👋 Bonjour ! Bienvenue chez Askely Express. Répondez par :
1. Envoyer un colis
2. Devenir transporteur
3. Suivre un colis")
    elif "3" in incoming_msg or "suivre" in incoming_msg:
        msg.body("👋 Bonjour ! Bienvenue chez Askely Express. Répondez par :
1. Envoyer un colis
2. Devenir transporteur
3. Suivre un colis").")
    else:
        msg.body("👋 Bonjour ! Bienvenue chez Askely Express. Répondez par :
1. Envoyer un colis
2. Devenir transporteur
3. Suivre un colis")

    return str(resp)

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
