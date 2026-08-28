from flask import Blueprint, request, jsonify

from services.issuer_service import verify_credential


# =========================================================
# ISSUER ROUTE
# =========================================================
#
# This route receives a credential from the user/client
# and verifies whether it was genuinely issued by our
# trusted issuer.
# =========================================================

issuer_bp = Blueprint(
    "issuer",
    __name__,
    url_prefix="/issuer"
)


# =========================================================
# VERIFY CREDENTIAL
# =========================================================

@issuer_bp.route("/verify-credential", methods=["POST"])
def verify_issuer_credential():

    # -----------------------------------------------------
    # STEP 1: Receive JSON
    # -----------------------------------------------------

    payload = request.get_json()

    if not payload:

        return jsonify({
            "success": False,
            "message": "Request body is missing."
        }), 400


    # -----------------------------------------------------
    # STEP 2: Extract credential
    # -----------------------------------------------------

    credential = payload.get("credential")

    if credential is None:

        return jsonify({
            "success": False,
            "message": "Credential is missing."
        }), 400


    # -----------------------------------------------------
    # STEP 3: Verify credential
    # -----------------------------------------------------

    result = verify_credential(credential)


    # -----------------------------------------------------
    # STEP 4: Return verification result
    # -----------------------------------------------------

    if result["valid"]:

        return jsonify({
            "success": True,
            "valid": True,
            "message": result["message"],
            "issuer": result.get("issuer")
        }), 200


    return jsonify({
        "success": True,
        "valid": False,
        "message": result["message"]
    }), 400