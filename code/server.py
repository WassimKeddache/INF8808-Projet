# server.py
from flask_failsafe import failsafe
import os

@failsafe
def create_app():
    '''
    Obtient le serveur sous-jacent Flask à partir de notre application Dash.
    Retourne:
        Le serveur à exécuter
    '''
    from app import app    # Importer le serveur depuis app.py
    return app.server

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    create_app().run(host="0.0.0.0", port=port, debug=True)
