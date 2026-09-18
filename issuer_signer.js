// ZeroTrace-Engine/backend/issuer_signer.js

const { buildEddsa, buildPoseidon, buildBabyjub } = require("circomlibjs");
const crypto = require("crypto");

let eddsa, poseidon, babyJub;

async function initCrypto() {
    eddsa = await buildEddsa();
    poseidon = await buildPoseidon();
    babyJub = await buildBabyjub();
}

// Government Private Key (stored on mock server)
const ISSUER_PRIVATE_KEY = crypto
    .createHash("sha256")
    .update("Mock_DigiLocker_Secret_Key_2026")
    .digest();


// ============================================================
// CONVERT CITIZEN ID INTO NUMERIC FIELD VALUE
// ============================================================
// Citizen IDs such as:
//
// CITIZEN001
// CITIZEN012
//
// cannot be directly converted using BigInt().
//
// We therefore create a deterministic SHA-256 hash and
// convert that hash into a BigInt.
// ============================================================

function idToBigInt(idHash) {

    const hash = crypto
        .createHash("sha256")
        .update(String(idHash))
        .digest("hex");

    return BigInt("0x" + hash);
}


async function generateSignedCredential(
    idHash,
    dobYear,
    expiryTimestamp,
    isActive
) {

    if (!eddsa) {
        await initCrypto();
    }


    // ========================================================
    // 1. DERIVE PUBLIC KEY COORDINATES [Ax, Ay]
    // ========================================================

    const pubKey = eddsa.prv2pub(ISSUER_PRIVATE_KEY);

    const pubKeyFormatted = [
        babyJub.F.toString(pubKey[0]),
        babyJub.F.toString(pubKey[1])
    ];


    // ========================================================
    // 2. HASH PAYLOAD FIELDS INTO FIELD ELEMENT
    // ========================================================

    const numericIdHash = idToBigInt(idHash);

    const payload = [
        numericIdHash,
        BigInt(dobYear),
        BigInt(expiryTimestamp),
        BigInt(isActive)
    ];

    const messageHash = poseidon(payload);


    // ========================================================
    // 3. GENERATE EDDSA SIGNATURE
    // ========================================================

    const signature = eddsa.signPoseidon(
        ISSUER_PRIVATE_KEY,
        messageHash
    );


    // ========================================================
    // 4. RETURN COMPLETE SIGNED CREDENTIAL JSON
    // ========================================================

    return {

        issuer_pubkey: pubKeyFormatted,

        credential_data: {

            // Keep original citizen ID for API response.
            // Cryptographic hashing uses numericIdHash above.
            id_hash: String(idHash),

            // Store numeric hash used by cryptography.
            id_numeric_hash: numericIdHash.toString(),

            dob_year: Number(dobYear),

            expiry: Number(expiryTimestamp),

            is_active: Number(isActive)
        },

        signature: {

            R8: [
                babyJub.F.toString(signature.R8[0]),
                babyJub.F.toString(signature.R8[1])
            ],

            S: signature.S.toString()
        }
    };
}


module.exports = {
    generateSignedCredential
};