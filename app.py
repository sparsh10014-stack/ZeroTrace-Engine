from flask import Flask, request, jsonify

# json module JSON data ko file me save karne ke liye use hoga.
import json

# os module folders aur file paths handle karne ke liye use hoga.
import os

app = Flask(__name__)

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
    # Agar temp folder already exist karta hai to error nahi aayega.
    os.makedirs("temp", exist_ok=True)

    # Temporary proof file ka path.
    proof_path = os.path.join("temp", "proof.json")

    # Temporary public signals file ka path.
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

    # Abhi SnarkJS verification next step me add karenge.
    return jsonify({
        "status": "success",
        "message": "Proof and public signals received and saved successfully."
    }), 200

if __name__ == '__main__':
    print("Starting ZeroTrace Verifier Node...")
    app.run(debug=True, port=5000)


