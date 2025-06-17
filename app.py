
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    incoming_msg = request.values.get('Body', '').strip().lower()
    resp = MessagingResponse()
    msg = resp.message()

    if incoming_msg in ['bonjour', 'salut', 'hello']:
        msg.body("👋 Bonjour ! Bienvenue chez Askely Express. Répondez par :\n1. Envoyer un colis\n2. Devenir transporteur\n3. Suivre un colis")
    elif incoming_msg == '1':
        msg.body("📦 Merci ! Pour envoyer un colis, veuillez nous indiquer :\n- Le pays de destination\n- Le poids approximatif\n- La date souhaitée pour l’envoi")
    elif incoming_msg == '2':
        msg.body("🚚 Pour devenir transporteur, merci d’envoyer :\n- Vos destinations régulières\n- La fréquence de voyage\n- Votre numéro WhatsApp")
    elif incoming_msg == '3':
        msg.body("🔍 Pour suivre un colis, veuillez entrer le numéro de suivi (ex : ASK1234)")
    else:
        msg.body("❓ Désolé, je n’ai pas compris. Veuillez répondre par :\n1. Envoyer un colis\n2. Devenir transporteur\n3. Suivre un colis")

    return str(resp)

if __name__ == '__main__':
    app.run(debug=True, port=10000)
