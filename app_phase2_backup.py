from flask import Flask, request, jsonify


app = Flask(__name__)

@app.route('/verify', methods=['POST'])
def verify_proof():
    # 1. Catch the ZKP payload from the frontend
    payload = request.get_json()
    
    # 2. Extract the components
    proof = payload.get('proof')
    public_signals = payload.get('publicSignals')
    
    # 3. Robust error handling
    if not proof or not public_signals:
        return jsonify({"error": "Invalid payload: Missing proof or public signals"}), 400

    print("Secure payload received! Ready for SnarkJS verification.")
    
    # 4. Return success status
    return jsonify({
        "status": "success", 
        "message": "Zero-Knowledge Proof hit the verifier node."
    }), 200

if __name__ == '__main__':
    print("Starting ZeroTrace Verifier Node...")
    app.run(debug=True, port=5000)