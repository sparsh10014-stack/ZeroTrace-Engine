from flask import Flask, jsonify, request

from backend.services.issuer_service import create_credential


app = Flask(__name__)


# =========================================================
# MOCK DIGILOCKER HOME
# =========================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "service": "ZeroTrace Mock DigiLocker",
        "status": "running"
    })


# =========================================================
# AUTHORIZE USER
# =========================================================

@app.route("/authorize", methods=["POST"])
def authorize():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is missing."
        }), 400


    document_id = data.get("document_id")

    if not document_id:

        return jsonify({
            "success": False,
            "message": "Document ID is required."
        }), 400


    # -----------------------------------------------------
    # In our demo, this represents successful user
    # authentication + consent.
    # -----------------------------------------------------

    return jsonify({
        "success": True,
        "authorized": True,
        "message": "User authorized successfully.",
        "document_id": document_id
    }), 200


# =========================================================
# GET CREDENTIAL
# =========================================================

@app.route("/credential", methods=["POST"])
def get_credential():

    data = request.get_json()

    if not data:

        return jsonify({
            "success": False,
            "message": "Request body is missing."
        }), 400


    document_id = data.get("document_id")

    name = data.get("name")

    date_of_birth = data.get("date_of_birth")


    if not document_id or not name or not date_of_birth:

        return jsonify({
            "success": False,
            "message": "Missing credential information."
        }), 400


    # -----------------------------------------------------
    # Mock DigiLocker asks the trusted issuer service
    # to create a signed credential.
    # -----------------------------------------------------

    credential = create_credential(
        document_id=document_id,
        name=name,
        date_of_birth=date_of_birth
    )


    return jsonify({
        "success": True,
        "credential": credential
    }), 200


# =========================================================
# APPLICATION START
# =========================================================

if __name__ == "__main__":

    print(
        "Starting ZeroTrace Mock DigiLocker "
        "on http://127.0.0.1:6001 ..."
    )

    app.run(
        debug=True,
        port=6001
    )