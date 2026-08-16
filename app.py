from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import subprocess

from database.db_manager import insert_log

app = Flask(__name__, static_folder='Frontend', static_url_path='')
CORS(app)  # Cross-Origin Resource Sharing enable kar rahe hain.


@app.route('/')
def index():
    return app.send_static_file('index.html')


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

    # Agar proof ya public signals missing hain to request reject kar do.
    if proof is None or public_signals is None:
        return jsonify({
            "status": "error",
            "message": "Missing proof or public signals"
        }), 400

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

        print("========== SNARKJS STDOUT ==========")
        print(result.stdout)
        print("========== SNARKJS STDERR ==========")
        print(result.stderr)
        print("========== RETURN CODE ==========")
        print(result.returncode)

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