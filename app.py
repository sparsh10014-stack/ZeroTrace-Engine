from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import subprocess
import sqlite3
import uuid



from database.db_manager import insert_log

app = Flask(__name__, static_folder='Frontend', static_url_path='')
CORS(app)  # Cross-Origin Resource Sharing enable kar rahe hain.

# =========================================================
# SERVER STATE (In-Memory Nonce Storage for Phase 4)
# =========================================================
active_nonces = set()

def get_citizen_record(id_hash):

    try:
        # SQLite database connection establish kar rahe hain.
        conn = sqlite3.connect('database/verification_log.db')
        cursor = conn.cursor()

        # Citizen record ko fetch karne ke liye SQL query execute kar rahe hain.
        cursor.execute("SELECT dob_year ,expiry , is_active FROM citizens WHERE id_hash = ?", (id_hash,))
        record = cursor.fetchone()

        return record

    except sqlite3.OperationalError :
        
        return (2005,1772150400,1)

    
@app.route('/')
def index():
    return app.send_static_file('index.html')


# =========================================================
# PHASE 4: NONCE GENERATOR (Replay Protection)
# =========================================================
@app.route('/api/get-nonce', methods=['GET'])
def get_nonce():
    # Unique nonce generate kar rahe hain.
    nonce = str(uuid.uuid4())
    active_nonces.add(nonce)

    return jsonify({
        "nonce": nonce
    }), 200

# =========================================================
# PHASE 1 & 3: MOCK ISSUER & REVOCATION LOOKUP
# =========================================================

@app.route('/api/issue-credential',methods=['POST'])
def issue_credential():
    data =  request.json
    client_id_hash = data.get("ocr_id_hash")

    # 1. Look up the OCR-extracted ID in Sachin's dummy database
    record = get_citizen_record(client_id_hash)

    if not record:
        return jsonify({"error":"ID not found in the database"}), 404

    dob_year, expiry, is_active = record

    # 2. Check if the credential is valid
    if is_active == 0:
        return jsonify({"error":"Credential is revoked"}), 403

    #3.call sparsh's mock issuer API to issue the credential
    try:
        process = subprocess.run(
            ['node', '-e', f"""
                const signer = require('./issuer_signer.js');
                signer.generateSignedCredential('{client_id_hash}', {dob_year}, {expiry}, {is_active})
                .then(res => console.log(JSON.stringify(res)));
            """],
            capture_output=True,text=True, check=True 
            )
        signed_credential = json.loads(process.stdout)
        return jsonify(signed_credential), 200

    except Exception as e:
        return jsonify({"error": "Failed to generate digital signature", "details": str(e)}), 500


# =========================================================
# VERIFY ROUTE
# =========================================================
@app.route('/verify', methods=['POST'])
def verify_proof():
    # Frontend se JSON request body receive kar rahe hain.
    payload = request.get_json()

    # Agar request body empty hai to error return karo.
    if not payload:
        return jsonify({
            "status": "error",
            "message": "Request body is missing"
        }), 400

    # STEP 2: Proof aur Public Signals nikalna
    proof = payload.get('proof')
    public_signals = payload.get('publicSignals')
    client_nonce = payload.get('nonce')

    # STEP 1: Nonce Replay Protection Check
    if client_nonce not in active_nonces:
        insert_log("FAIL")
        return jsonify({"status": "error", "message": "Invalid or expired challenge nonce! Replay attack detected."}), 403

    # Mark nonce as used so it can never be used again
    active_nonces.remove(client_nonce)

    if proof is None or public_signals is None:
        return jsonify({"status": "error", "message": "Missing proof or public signals"}), 400

    os.makedirs("temp", exist_ok=True)
    proof_path = os.path.join("temp", "proof.json")
    public_path = os.path.join("temp", "public.json")








    # # Agar proof ya public signals missing hain to request reject kar do.
    # if proof is None or public_signals is None:
    #     return jsonify({
    #         "status": "error",
    #         "message": "Missing proof or public signals"
    #     }), 400

    # Temporary folder ko ensure kar rahe hain.
    os.makedirs("temp", exist_ok=True)

    # Temporary proof & public signals file paths
    proof_path = os.path.join("temp", "proof.json")
    public_path = os.path.join("temp", "public.json")

    try:
        # STEP 4: Proof aur Public Signals ko temporary JSON files me save karna
        with open(proof_path, "w") as file:
            json.dump(proof, file, indent=4)

        with open(public_path, "w") as file:
            json.dump(public_signals, file, indent=4)

        print("Proof saved:", proof_path)
        print("Public signals saved:", public_path)

        # STEP 5: SnarkJS Groth16 Verification
        npx_cmd = "npx.cmd" if os.name == "nt" else "npx"
        
        result = subprocess.run(
            [
                npx_cmd,
                "snarkjs",
                "groth16",
                "verify",
                "verification_key.json",
                public_path,
                proof_path
            ],
            capture_output=True,
            text=True
        )

        # print("========== SNARKJS STDOUT ==========")
        # print(result.stdout)
        # print("========== SNARKJS STDERR ==========")
        # print(result.stderr)
        # print("========== RETURN CODE ==========")
        # print(result.returncode)

        # STEP 6: Verification result determine karna
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
        return jsonify({
            "success": False,
            "message": f"Internal verification error: {str(error)}"
        }), 500

    finally:
        # STEP 7: Temporary Files Cleanup
        if os.path.exists(proof_path):
            os.remove(proof_path)
            print("Temporary proof file deleted.")

        if os.path.exists(public_path):
            os.remove(public_path)
            print("Temporary public signals file deleted.")

        print("Temporary files cleanup completed.")


# =========================================================
# APPLICATION START
# =========================================================
if __name__ == '__main__':
    print("Starting ZeroTrace Verifier Node on http://127.0.0.1:5000 ...")
    app.run(debug=True, port=5000)