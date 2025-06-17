
from flask import Flask, request, jsonify, render_template, Response
from datetime import datetime
import sqlite3
import requests
from twilio.rest import Client

app = Flask(__name__)
DB_PATH = 'askely_express.db'

# Authentification admin
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'askely2025'

# Twilio WhatsApp Credentials (à personnaliser)
TWILIO_SID = "TON_ACCOUNT_SID"
TWILIO_TOKEN = "TON_AUTH_TOKEN"
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"

def envoyer_whatsapp(numero_utilisateur, message):
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            to=f"whatsapp:{numero_utilisateur}",
            body=message
        )
        print(f"✅ WhatsApp envoyé à {numero_utilisateur}")
    except Exception as e:
        print(f"❌ Erreur WhatsApp : {e}")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS transporteurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT, 
            tel TEXT, 
            email TEXT,
            destinations TEXT,
            frequence TEXT,
            orange_money TEXT,
            abonnement_actif BOOLEAN DEFAULT 1,
            date_inscription TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS colis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_client TEXT,
            tel_client TEXT,
            ville_depart TEXT,
            ville_arrivee TEXT,
            poids_kg REAL,
            prix_total REAL,
            id_transporteur INTEGER,
            date_demande TEXT,
            statut TEXT,
            FOREIGN KEY(id_transporteur) REFERENCES transporteurs(id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS paiements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            montant REAL,
            expediteur TEXT,
            recepteur TEXT,
            statut TEXT,
            date_paiement TEXT,
            id_colis INTEGER,
            FOREIGN KEY(id_colis) REFERENCES colis(id)
        )
    ''')
    conn.commit()
    conn.close()

def check_auth(username, password):
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

def authenticate():
    return Response(
        '⚠️ Accès refusé. Veuillez vous authentifier.'', 401,
        {'WWW-Authenticate': 'Basic realm="Askely Admin"'})

def requires_auth(f):
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated

@app.route('/')
def home():
    return "Bienvenue sur Askely Express Pro"

@app.route('/poster_colis', methods=['POST'])
def poster_colis():
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO colis (nom_client, tel_client, ville_depart, ville_arrivee, poids_kg, prix_total, date_demande, statut)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['nom_client'], data['tel_client'], data['ville_depart'], data['ville_arrivee'],
        data['poids_kg'], data['prix_total'], datetime.now().isoformat(), 'en attente'
    ))
    conn.commit()
    conn.close()

    # Notification WhatsApp au client
    envoyer_whatsapp(data['tel_client'], f"📦 Bonjour {data['nom_client']} ! Votre demande d'envoi de {data['ville_depart']} à {data['ville_arrivee']} est bien enregistrée. Nous vous recontactons bientôt.")
    envoyer_whatsapp(data['tel_client'], f"📦 Bonjour {data['nom_client']} ! Votre demande d'envoi de {data['ville_depart']} à {data['ville_arrivee']} est bien enregistrée. Nous vous recontactons bientôt.")

    return jsonify({"message": "Demande de colis enregistrée"}), 201

@app.route('/paiement_commission', methods=['POST'])
def paiement_commission():
    data = request.json
    montant = data['montant']
    expediteur = data['expediteur']
    recepteur = data['recepteur']
    id_colis = data['id_colis']

    API_URL = "https://api.mobilemoneyprovider.com/transfer"
    API_KEY = "VOTRE_CLE_API_ICI"
    HEADERS = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "from": expediteur,
        "to": recepteur,
        "amount": montant,
        "currency": "XOF",
        "description": "Commission Askely Express"
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        statut = "succès" if response.status_code == 200 else "échec"
    except Exception as e:
        statut = "erreur"

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO paiements (montant, expediteur, recepteur, statut, date_paiement, id_colis)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (montant, expediteur, recepteur, statut, datetime.now().isoformat(), id_colis))
    conn.commit()
    conn.close()

    return jsonify({"statut": statut})

@app.route('/admin/paiements')
@requires_auth
def voir_paiements():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, montant, expediteur, recepteur, statut, date_paiement FROM paiements ORDER BY date_paiement DESC')
    paiements = c.fetchall()
    conn.close()
    return render_template("paiements.html", paiements=paiements)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=10000)



@app.route('/assigner_transporteur', methods=['POST'])
def assigner_transporteur():
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Mise à jour du colis
    c.execute('''
        UPDATE colis SET id_transporteur = ?, statut = 'assigné'
        WHERE id = ?
    ''', (data['id_transporteur'], data['id_colis']))
    conn.commit()

    # Récupérer info transporteur
    c.execute('SELECT tel, nom FROM transporteurs WHERE id = ?', (data['id_transporteur'],))
    transporteur = c.fetchone()
    if transporteur:
        tel_transporteur, nom_transporteur = transporteur
        # Message WhatsApp
        message = f"📬 Bonjour {nom_transporteur}, une nouvelle mission vous a été assignée. Veuillez consulter votre tableau de bord Askely Express."
        envoyer_whatsapp(tel_transporteur, message)

    conn.close()
    return jsonify({"message": "Transporteur assigné au colis"}), 200
