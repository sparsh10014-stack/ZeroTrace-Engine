# =========================================================
# ZKP SERVICE
# =========================================================
#
# This file is responsible ONLY for:
#
# 1. Receiving the ZK proof and public signals
# 2. Creating temporary JSON files
# 3. Calling SnarkJS Groth16 verifier
# 4. Returning verification result
# 5. Deleting temporary files
#
# Flask routes should NOT contain SnarkJS logic.
# =========================================================

import json
import os
import subprocess
from pathlib import Path


# =========================================================
# PROJECT PATHS
# =========================================================

# Current file:
#
# ZeroTrace-Engine/
# └── backend/
#     └── services/
#         └── zkp_service.py
#
# parents[0] = services
# parents[1] = backend
# parents[2] = ZeroTrace-Engine

BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = Path(__file__).resolve().parents[2]


# Verification key generated for our ZKP circuit.
VERIFICATION_KEY = BACKEND_DIR / "zkp" / "verification_key.json"


# Temporary files will be stored here.
TEMP_DIR = BACKEND_DIR / "temp"

PROOF_FILE = TEMP_DIR / "proof.json"
PUBLIC_FILE = TEMP_DIR / "public.json"


# =========================================================
# VERIFY ZKP
# =========================================================

def verify_zkp(proof, public_signals):
    """
    Verify a Zero-Knowledge Proof using SnarkJS Groth16.

    Parameters:
        proof:
            ZK proof object received from frontend.

        public_signals:
            Public signals associated with the proof.

    Returns:
        Dictionary containing:
            valid  -> True / False
            output -> SnarkJS output
            error  -> error message if any
    """

    # -----------------------------------------------------
    # STEP 1: Make sure temp directory exists
    # -----------------------------------------------------

    TEMP_DIR.mkdir(parents=True, exist_ok=True)


    try:

        # -------------------------------------------------
        # STEP 2: Save proof temporarily
        # -------------------------------------------------

        with open(PROOF_FILE, "w", encoding="utf-8") as file:
            json.dump(proof, file, indent=4)


        # -------------------------------------------------
        # STEP 3: Save public signals temporarily
        # -------------------------------------------------

        with open(PUBLIC_FILE, "w", encoding="utf-8") as file:
            json.dump(public_signals, file, indent=4)


        print("========================================")
        print("ZKP VERIFICATION STARTED")
        print("========================================")

        print("Proof file:", PROOF_FILE)
        print("Public signals:", PUBLIC_FILE)


        # -------------------------------------------------
        # STEP 4: Select NPX command
        # -------------------------------------------------

        # Windows uses npx.cmd
        # Linux/Mac uses npx

        npx_command = "npx.cmd" if os.name == "nt" else "npx"


        # -------------------------------------------------
        # STEP 5: Run SnarkJS Groth16 verification
        # -------------------------------------------------

        result = subprocess.run(
            [
                npx_command,
                "snarkjs",

                # Groth16 proving system
                "groth16",

                # Verification operation
                "verify",

                # Verification key
                str(VERIFICATION_KEY),

                # Public signals
                str(PUBLIC_FILE),

                # Proof
                str(PROOF_FILE)
            ],

            # Capture SnarkJS output
            capture_output=True,

            # Return output as string
            text=True,

            # Run from project root
            cwd=PROJECT_DIR
        )


        # -------------------------------------------------
        # STEP 6: Print SnarkJS output
        # -------------------------------------------------

        print("========== SNARKJS STDOUT ==========")
        print(result.stdout)

        print("========== SNARKJS STDERR ==========")
        print(result.stderr)

        print("========== RETURN CODE ==========")
        print(result.returncode)


        # -------------------------------------------------
        # STEP 7: Determine verification result
        # -------------------------------------------------

        if result.returncode == 0 and "OK!" in result.stdout:

            print("ZKP VERIFICATION: SUCCESS")

            return {
                "valid": True,
                "message": "Zero-Knowledge Proof verified successfully.",
                "snarkjs_output": result.stdout
            }


        # -------------------------------------------------
        # Verification failed
        # -------------------------------------------------

        print("ZKP VERIFICATION: FAILED")

        return {
            "valid": False,
            "message": "Zero-Knowledge Proof verification failed.",
            "snarkjs_output": result.stdout,
            "snarkjs_error": result.stderr
        }


    except Exception as error:

        # -------------------------------------------------
        # Unexpected error
        # -------------------------------------------------

        print("========== ZKP ERROR ==========")
        print(error)

        return {
            "valid": False,
            "error": str(error)
        }


    finally:

        # =================================================
        # CLEANUP
        # =================================================
        #
        # These files contain the proof/public signals
        # only temporarily.
        #
        # After verification we don't need them anymore.
        # =================================================

        if PROOF_FILE.exists():

            PROOF_FILE.unlink()

            print("Temporary proof file deleted.")


        if PUBLIC_FILE.exists():

            PUBLIC_FILE.unlink()

            print("Temporary public signals file deleted.")


        print("Temporary files cleanup completed.")