from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import subprocess
import uuid

# Sachin's new database import (Keep this)
from database.citizen_db import get_citizen_by_id
from database.db_manager import insert_log

app = Flask(__name__, static_folder='Frontend', static_url_path='')
CORS(app) 

active_nonces = set()

@app.route('/')
def index():
    return app.send_static_file('index.html')


# =========================================================
# PHASE 4: NONCE GENERATOR
# =========================================================
@app.route('/api/get-nonce', methods=['GET'])
def get_nonce():
    nonce = str(uuid.uuid4())
    active_nonces.add(nonce)
    return jsonify({"nonce": nonce}), 200


# =========================================================
# PHASE 1 & 3: MOCK ISSUER WITH SACHIN'S DB + SPARSH'S CRYPTO
# =========================================================
@app.route('/api/issue-credential', methods=['POST'])
def issue_credential():
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "message": "Request body is missing."}), 400

    # Supporting both variable names to protect against frontend crashes
    citizen_id = data.get("ocr_id_number") or data.get("ocr_id_hash")

    if not citizen_id:
        return jsonify({"success": False, "message": "OCR citizen ID number is required."}), 400

    # 1. Sachin's Database Lookup
    citizen = get_citizen_by_id(citizen_id)

    if citizen is None:
        return jsonify({"success": False, "message": "Citizen ID not found in database."}), 404

    # 2. Revocation Check
    if citizen.get("active") is False or citizen.get("active") == 0:
        return jsonify({"success": False, "message": "Credential is revoked."}), 403

    # Map Sachin's database output to Sparsh's cryptography variables
    date_of_birth = citizen.get("date_of_birth")

    if not date_of_birth:
        return jsonify({
            "success": False,
            "message": "Citizen date of birth is missing."
    }), 500

    dob_year = int(date_of_birth.split("-")[0])
    expiry = 1772150400 # Mock expiry timestamp
    is_active = 1 if citizen.get("active") else 0

    # 3. SPARSH'S CORE LOGIC: Node.js Cryptographic Signer
    try:
        process = subprocess.run(
            ['node', '-e', f"""
                const signer = require('./issuer_signer.js');
                signer.generateSignedCredential('{citizen_id}', {dob_year}, {expiry}, {is_active})
                .then(res => console.log(JSON.stringify(res)));
            """],
            capture_output=True, text=True, check=True 
        )
        signed_credential = json.loads(process.stdout)
        return jsonify(signed_credential), 200

    except Exception as e:
        return jsonify({"error": "Failed to generate digital signature", "details": str(e)}), 500


# =========================================================
# PHASE 2 & 4: VERIFY ROUTE (Sparsh's perfect version)
# =========================================================
@app.route('/api/verify-proof', methods=['POST'])
@app.route('/verify', methods=['POST']) # Keeping both for QA testing
def verify_proof():
    payload = request.get_json()

    if not payload:
        return jsonify({"status": "error", "message": "Request body is missing"}), 400

    proof = payload.get('proof')
    public_signals = payload.get('publicSignals')
    client_nonce = payload.get('nonce')

    if client_nonce not in active_nonces:
        insert_log("FAIL")
        return jsonify({"status": "error", "message": "Invalid or expired challenge nonce! Replay attack detected."}), 403

    active_nonces.remove(client_nonce)

    if proof is None or public_signals is None:
        return jsonify({"status": "error", "message": "Missing proof or public signals"}), 400

    os.makedirs("temp", exist_ok=True)
    proof_path = os.path.join("temp", "proof.json")
    public_path = os.path.join("temp", "public.json")

    try:
        with open(proof_path, "w") as file:
            json.dump(proof, file, indent=4)

        with open(public_path, "w") as file:
            json.dump(public_signals, file, indent=4)

        npx_cmd = "npx.cmd" if os.name == "nt" else "npx"
        
        result = subprocess.run(
            [npx_cmd, "snarkjs", "groth16", "verify", "verification_key.json", public_path, proof_path],
            capture_output=True, text=True
        )

        if result.returncode == 0 and "OK!" in result.stdout:
            insert_log("PASS")
            return jsonify({
                "success": True,
                "valid": True,
                "status": "success",
                "message": "Zero-Knowledge Proof verified successfully."
            }), 200
        else:
            insert_log("FAIL")
            return jsonify({
                "success": True,
                "valid": False,
                "status": "error",
                "message": f"Proof verification failed: {result.stderr or result.stdout}"
            }), 400

    except Exception as error:
        print("========== VERIFICATION ERROR ==========")
        print(error)
        return jsonify({"success": False, "message": f"Internal verification error: {str(error)}"}), 500

    finally:
        if os.path.exists(proof_path):
            os.remove(proof_path)
        if os.path.exists(public_path):
            os.remove(public_path)

if __name__ == '__main__':
    print("Starting ZeroTrace Verifier Node on http://127.0.0.1:5000 ...") 
    app.run(debug=True, port=5000)  