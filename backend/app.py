from flask import Flask, jsonify
from flask_cors import CORS

from routes.verifier import verifier_bp

from routes.issuer import issuer_bp


# =========================================================
# FLASK APPLICATION
# =========================================================

app = Flask(__name__, static_folder='Frontend', static_url_path='')

CORS(app)

app.register_blueprint(issuer_bp)

# =========================================================
# HOME / HEALTH CHECK
# =========================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "status": "running",
        "service": "ZeroTrace Verifier Node"
    })


# =========================================================
# REGISTER ROUTES
# =========================================================

app.register_blueprint(verifier_bp)


# =========================================================
# APPLICATION START
# =========================================================

if __name__ == "__main__":

    print(
        "Starting ZeroTrace Verifier Node "
        "on http://127.0.0.1:5000 ..."
    )

    app.run(
        debug=True,
        port=5000
    )