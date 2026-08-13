from flask import Flask, request, jsonify

# Python se external command (SnarkJS) run karne ke liye.
import subprocess

# JSON data ko file me save karne ke liye.
import json

# Folder aur file paths handle karne ke liye.
import os


# =========================================================
# FLASK APPLICATION
# =========================================================

# Flask application create kar rahe hain.
app = Flask(__name__)


# =========================================================
# VERIFY ROUTE
# =========================================================

# /verify endpoint sirf POST request accept karega.
@app.route('/verify', methods=['POST'])
def verify_proof():

    # -----------------------------------------------------
    # STEP 1: Frontend se JSON receive karna
    # -----------------------------------------------------

    # Request body se JSON data Python object me convert hoga.
    payload = request.get_json()

    # Agar request body empty hai to error return karo.
    if not payload:
        return jsonify({
            "status": "error",
            "message": "Request body is missing"
        }), 400


    # -----------------------------------------------------
    # STEP 2: Proof aur Public Signals nikalna
    # -----------------------------------------------------

    # JSON payload ke andar se proof nikal rahe hain.
    proof = payload.get('proof')

    # JSON payload ke andar se public signals nikal rahe hain.
    public_signals = payload.get('publicSignals')


    # Agar proof ya public signals missing hain
    # to request reject kar do.
    if proof is None or public_signals is None:
        return jsonify({
            "status": "error",
            "message": "Missing proof or public signals"
        }), 400


    # -----------------------------------------------------
    # STEP 3: Temporary folder aur file paths
    # -----------------------------------------------------

    # temp folder ensure kar rahe hain.
    # Agar folder already exist karta hai,
    # to exist_ok=True ki wajah se error nahi aayega.
    os.makedirs("temp", exist_ok=True)

    # Temporary proof file ka path.
    proof_path = os.path.join("temp", "proof.json")

    # Temporary public signals file ka path.
    public_path = os.path.join("temp", "public.json")


    # -----------------------------------------------------
    # STEP 4: Proof aur Public Signals save karna
    # -----------------------------------------------------

    try:

        # -------------------------------------------------
        # Proof ko temporary JSON file me save karna
        # -------------------------------------------------

        # proof.json ko write mode me open kar rahe hain.
        with open(proof_path, "w") as file:

            # Python proof object ko JSON format me save kar rahe hain.
            json.dump(proof, file, indent=4)


        # -------------------------------------------------
        # Public Signals ko temporary JSON file me save karna
        # -------------------------------------------------

        # public.json ko write mode me open kar rahe hain.
        with open(public_path, "w") as file:

            # Public signals ko JSON format me save kar rahe hain.
            json.dump(public_signals, file, indent=4)


        # Terminal me confirmation print karo.
        print("Proof saved:", proof_path)
        print("Public signals saved:", public_path)


        # =================================================
        # STEP 5: SnarkJS Groth16 Verification
        # =================================================

        # Python ke through SnarkJS command execute kar rahe hain.
        result = subprocess.run(
            [
                # Windows par NPX executable.
                "npx.cmd",

                # SnarkJS package.
                "snarkjs",

                # Groth16 verification system.
                "groth16",

                # Verify operation.
                "verify",

                # Circuit ki verification key.
                "verification_key.json",

                # Temporary public signals file.
                public_path,

                # Temporary proof file.
                proof_path
            ],

            # SnarkJS ka output Python ke paas capture hoga.
            capture_output=True,

            # Output ko string ke form me receive karenge.
            text=True
        )


        # =================================================
        # STEP 6: SnarkJS ka result terminal me print karna
        # =================================================

        # SnarkJS ka normal output.
        print("========== SNARKJS STDOUT ==========")
        print(result.stdout)

        # SnarkJS ka error output.
        print("========== SNARKJS STDERR ==========")
        print(result.stderr)

        # Command ka exit/return code.
        print("========== RETURN CODE ==========")
        print(result.returncode)


        # =================================================
        # STEP 7: Verification result determine karna
        # =================================================

        # Return code 0 ka matlab SnarkJS successfully
        # proof verify kar chuka hai.
        if result.returncode == 0:

            return jsonify({
                "success": True,
                "valid": True,
                "message": "Zero-Knowledge Proof verified successfully."
            }), 200


        # Return code 0 nahi hai to proof verification fail hui.
        else:

            return jsonify({
                "success": True,
                "valid": False,
                "message": "Zero-Knowledge Proof verification failed."
            }), 400


    # =====================================================
    # STEP 8: Unexpected Python/System Error
    # =====================================================

    except Exception as error:

        # Actual error terminal me print karenge
        # taaki debugging easy ho.
        print("========== VERIFICATION ERROR ==========")
        print(error)

        # Frontend ko internal server error response.
        return jsonify({
            "success": False,
            "message": "Internal verification error"
        }), 500


    # =====================================================
    # STEP 9: Temporary Files Cleanup
    # =====================================================

    finally:

        # -------------------------------------------------
        # Temporary proof file delete karna
        # -------------------------------------------------

        # Check kar rahe hain ki proof file exist karti hai ya nahi.
        if os.path.exists(proof_path):

            # Proof file delete kar rahe hain.
            os.remove(proof_path)

            print("Temporary proof file deleted.")


        # -------------------------------------------------
        # Temporary public signals file delete karna
        # -------------------------------------------------

        # Check kar rahe hain ki public signals file exist
        # karti hai ya nahi.
        if os.path.exists(public_path):

            # Public signals file delete kar rahe hain.
            os.remove(public_path)

            print("Temporary public signals file deleted.")


        print("Temporary files cleanup completed.")


# =========================================================
# APPLICATION START
# =========================================================

# Ye block tab execute hoga jab hum:
#
# python app.py
#
# run karenge.
if __name__ == '__main__':

    # Terminal me startup message.
    print("Starting ZeroTrace Verifier Node...")

    # Flask development server start.
    app.run(debug=True, port=5000)