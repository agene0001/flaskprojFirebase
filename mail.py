from flask import Flask, request
import requests

app = Flask(__name__)


@app.route('/')
def index():
    return "Hello, world!"


@app.route('/notify', methods=['GET'])
def notify():
    # recipient = request.json.get('recipient', '')
    # subject = request.json.get('subject', '')
    # message = request.json.get('message', '')

    response = requests.post(
        "https://api.mailgun.net/v3/sandbox6b4f0797cfbf492086e73e623fc4ec33.mailgun.org/messages",
        auth=("key-", "77fd79dbc826f6fe0dc017b03059510d-19806d14-41f21d26"),
        data={
            "from": "Your Website <noreply@sandbox6b4f0797cfbf492086e73e623fc4ec33.mailgun.org>",
            "to": ['agene001@umn.edu'],
            "subject": 'hi',
            "text": 'How are you?'
        }
    )
    if response.status_code == 200:
        return "Email sent successfully!"
    else:
        return f"Failed to send email: {response.content}", 400


if __name__ == "__main__":
    app.run()
