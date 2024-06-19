import connexion

from config import CONFIG

app = connexion.FlaskApp(__name__)
app.add_api("api.yaml")
app.run( host="127.0.0.1",port=8080)

