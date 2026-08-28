# =========================================================
# ISSUER SERVICE
# =========================================================
#
# Responsibility:
#
# This service represents our TRUSTED ISSUER.
#
# In the final system, the issuer could be:
#
#     Government / DigiLocker
#
# For our current SIH implementation, we will use a
# controlled/mock issuer.
#
# IMPORTANT:
# The issuer creates a digitally signed credential.
#
# User -> receives credential
# Verifier -> verifies issuer signature
#
# The verifier should NEVER simply trust data supplied
# directly by the user.
# =========================================================

import base64
import hashlib
import hmac
import json
import os


# =========================================================
# MOCK ISSUER CONFIGURATION
# =========================================================

# This is ONLY for our controlled demo environment.
#
# In a real deployment, this secret would NOT be placed
# inside the application like this.
#
# A real issuer would use proper asymmetric cryptography
# and securely manage its private key.

ISSUER_NAME = "ZeroTrace Mock DigiLocker"

ISSUER_ID = "zerotrace-mock-digilocker"


# Demo-only signing secret.
ISSUER_SECRET = os.environ.get(
    "ISSUER_SECRET",
    "ZEROTRACE_DEMO_ISSUER_SECRET"
)


# =========================================================
# CREATE CREDENTIAL
# =========================================================

def create_credential(
    document_id,
    name,
    date_of_birth,
    document_type="GOVERNMENT_ID"
):
    """
    Create a digitally signed identity credential.

    Parameters:
        document_id:
            Unique ID/reference of the source document.

        name:
            Name present in the document.

        date_of_birth:
            DOB present in the document.

        document_type:
            Type of government identity document.

    Returns:
        A credential containing issuer information,
        claims and a digital signature.
    """

    # -----------------------------------------------------
    # STEP 1: Create credential payload
    # -----------------------------------------------------

    credential = {
        "issuer": {
            "id": ISSUER_ID,
            "name": ISSUER_NAME
        },

        "credential": {
            "type": document_type,

            "document_id": document_id,

            "name": name,

            "date_of_birth": date_of_birth
        }
    }


    # -----------------------------------------------------
    # STEP 2: Create canonical JSON
    # -----------------------------------------------------
    #
    # We need the exact same representation when creating
    # and verifying the signature.
    # -----------------------------------------------------

    credential_data = json.dumps(
        credential,
        sort_keys=True,
        separators=(",", ":")
    )


    # -----------------------------------------------------
    # STEP 3: Create digital signature
    # -----------------------------------------------------
    #
    # HMAC-SHA256 is being used ONLY for this demo issuer.
    #
    # Later we can replace this with proper asymmetric
    # issuer signatures.
    # -----------------------------------------------------

    signature = hmac.new(
        ISSUER_SECRET.encode("utf-8"),
        credential_data.encode("utf-8"),
        hashlib.sha256
    ).digest()


    # Convert binary signature into text so it can be sent
    # as JSON.

    signature_encoded = base64.b64encode(
        signature
    ).decode("utf-8")


    # -----------------------------------------------------
    # STEP 4: Attach signature
    # -----------------------------------------------------

    credential["signature"] = {
        "algorithm": "HMAC-SHA256",
        "value": signature_encoded
    }


    # -----------------------------------------------------
    # STEP 5: Return credential
    # -----------------------------------------------------

    return credential


# =========================================================
# VERIFY CREDENTIAL
# =========================================================

def verify_credential(credential):
    """
    Verify that a credential was created by our trusted
    mock issuer and has not been modified.

    Returns:
        {
            "valid": True/False,
            "message": "..."
        }
    """

    # -----------------------------------------------------
    # STEP 1: Basic validation
    # -----------------------------------------------------

    if not credential:

        return {
            "valid": False,
            "message": "Credential is missing."
        }


    if "issuer" not in credential:

        return {
            "valid": False,
            "message": "Issuer information is missing."
        }


    if "credential" not in credential:

        return {
            "valid": False,
            "message": "Credential data is missing."
        }


    if "signature" not in credential:

        return {
            "valid": False,
            "message": "Credential signature is missing."
        }


    # -----------------------------------------------------
    # STEP 2: Verify issuer
    # -----------------------------------------------------

    issuer = credential["issuer"]

    if issuer.get("id") != ISSUER_ID:

        return {
            "valid": False,
            "message": "Unknown or untrusted issuer."
        }


    # -----------------------------------------------------
    # STEP 3: Extract signature
    # -----------------------------------------------------

    signature_data = credential["signature"]

    if signature_data.get("algorithm") != "HMAC-SHA256":

        return {
            "valid": False,
            "message": "Unsupported signature algorithm."
        }


    provided_signature = signature_data.get("value")

    if not provided_signature:

        return {
            "valid": False,
            "message": "Signature value is missing."
        }


    # -----------------------------------------------------
    # STEP 4: Reconstruct original credential
    # -----------------------------------------------------
    #
    # Signature was generated BEFORE the signature field
    # was added.
    #
    # Therefore we remove it before calculating the expected
    # signature.
    # -----------------------------------------------------

    unsigned_credential = {
        "issuer": credential["issuer"],
        "credential": credential["credential"]
    }


    credential_data = json.dumps(
        unsigned_credential,
        sort_keys=True,
        separators=(",", ":")
    )


    # -----------------------------------------------------
    # STEP 5: Calculate expected signature
    # -----------------------------------------------------

    expected_signature = hmac.new(
        ISSUER_SECRET.encode("utf-8"),
        credential_data.encode("utf-8"),
        hashlib.sha256
    ).digest()


    expected_signature_encoded = base64.b64encode(
        expected_signature
    ).decode("utf-8")


    # -----------------------------------------------------
    # STEP 6: Compare signatures safely
    # -----------------------------------------------------

    if not hmac.compare_digest(
        provided_signature,
        expected_signature_encoded
    ):

        return {
            "valid": False,
            "message": "Invalid credential signature."
        }


    # -----------------------------------------------------
    # STEP 7: Credential is valid
    # -----------------------------------------------------

    return {
        "valid": True,
        "message": "Credential verified successfully.",
        "issuer": ISSUER_NAME
    }