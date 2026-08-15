from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import subprocess

app = Flask(__name__, static_folder='Frontend', static_url_path='')
CORS(app)  # Cross-Origin Resource Sharing enable kar rahe hain.


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/verify', methods=['POST'])
def verify_proof():
    # Frontend se JSON request body receive kar rahe hain.
    payload = request.get_json()

    # Check kar rahe hain ki request me JSON data actually aaya hai ya nahi.
    if not payload:
        return jsonify({
            "status": "error",
            "message": "Request body is missing"
        }), 400

    # JSON payload se Zero-Knowledge Proof nikal rahe hain.
    proof = payload.get('proof')

    # JSON payload se public signals nikal rahe hain.
    public_signals = payload.get('publicSignals')

    # Proof ya public signals missing hone par request reject kar denge.
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

    # Proof ko temporary JSON file me save kar rahe hain.
    with open(proof_path, "w") as file:
        json.dump(proof, file, indent=4)

    # Public signals ko temporary JSON file me save kar rahe hain.
    with open(public_path, "w") as file:
        json.dump(public_signals, file, indent=4)

    # Terminal me confirmation print kar rahe hain.
    print("Proof saved:", proof_path)
    print("Public signals saved:", public_path)

    # SnarkJS Groth16 verification run kar rahe hain
    npx_cmd = "npx.cmd" if os.name == "nt" else "npx"
    try:
        res = subprocess.run(
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

        print("SnarkJS STDOUT:", res.stdout)
        print("SnarkJS STDERR:", res.stderr)

        if res.returncode == 0 and "OK!" in res.stdout:
            return jsonify({
                "status": "success",
                "message": "Zero-Knowledge Proof verified successfully by backend verifier node."
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": f"Proof verification failed: {res.stderr or res.stdout}"
            }), 400
    except Exception as e:
        print("Verification exception:", str(e))
        return jsonify({
            "status": "error",
            "message": f"Server execution error during verification: {str(e)}"
        }), 500


if __name__ == '__main__':
    print("Starting ZeroTrace Verifier Node on http://127.0.0.1:5000 ...")
    app.run(debug=True, port=5000)



