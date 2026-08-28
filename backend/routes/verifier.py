# =========================================================
# VERIFIER ROUTE
# =========================================================

from flask import Blueprint, request, jsonify

from services.zkp_service import verify_zkp


# Blueprint create kar rahe hain.
verifier_bp = Blueprint(
    "verifier",
    __name__
)


# =========================================================
# VERIFY ENDPOINT
# =========================================================

@verifier_bp.route("/verify", methods=["POST"])
def verify_proof():

    # -----------------------------------------------------
    # STEP 1: Receive JSON from frontend
    # -----------------------------------------------------

    payload = request.get_json()

    if not payload:

        return jsonify({
            "success": False,
            "message": "Request body is missing."
        }), 400


    # -----------------------------------------------------
    # STEP 2: Extract proof
    # -----------------------------------------------------

    proof = payload.get("proof")

    public_signals = payload.get("publicSignals")


    # -----------------------------------------------------
    # STEP 3: Validate input
    # -----------------------------------------------------

    if proof is None or public_signals is None:

        return jsonify({
            "success": False,
            "message": "Missing proof or public signals."
        }), 400


    # -----------------------------------------------------
    # STEP 4: Send proof to ZKP service
    # -----------------------------------------------------

    result = verify_zkp(
        proof,
        public_signals
    )


    # -----------------------------------------------------
    # STEP 5: Return result to frontend
    # -----------------------------------------------------

    if result.get("valid"):

        return jsonify({
            "success": True,
            "valid": True,
            "status": "success",
            "message": result["message"]
        }), 200


    # -----------------------------------------------------
    # Verification failed
    # -----------------------------------------------------

    return jsonify({
        "success": True,
        "valid": False,
        "status": "error",
        "message": result.get(
            "message",
            "Proof verification failed."
        )
    }), 400